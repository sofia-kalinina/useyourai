import json
import os
from unittest.mock import MagicMock, patch

import boto3
import pytest
from moto import mock_aws

os.environ["TABLE_NAME"] = "test-table"

import submit_answer  # noqa: E402


SESSION_ID = "test-session-123"

FAKE_EXERCISES = [
    {"id": "01", "question": "Translate: I see the man.", "expected_answer": "Ich sehe den Mann."},
    {"id": "02", "question": "Translate: She buys the book.", "expected_answer": "Sie kauft das Buch."},
    {"id": "03", "question": "Translate: We need the car.", "expected_answer": "Wir brauchen das Auto."},
]


def bedrock_eval_response(is_correct):
    data = {"is_correct": is_correct}
    body_bytes = json.dumps({"content": [{"type": "text", "text": json.dumps(data)}]}).encode()
    mock_body = MagicMock()
    mock_body.read.return_value = body_bytes
    return {"body": mock_body}


def bedrock_feedback_response(text="Good job!"):
    body_bytes = json.dumps({"content": [{"type": "text", "text": text}]}).encode()
    mock_body = MagicMock()
    mock_body.read.return_value = body_bytes
    return {"body": mock_body}


def make_event(session_id=SESSION_ID, exercise_id=None, answer=None):
    payload = {}
    if exercise_id is not None:
        payload["exercise_id"] = exercise_id
    if answer is not None:
        payload["answer"] = answer
    return {
        "pathParameters": {"id": session_id},
        "body": json.dumps(payload),
    }


@pytest.fixture
def dynamodb_table():
    with mock_aws():
        ddb = boto3.resource("dynamodb", region_name="eu-central-1")
        table = ddb.create_table(
            TableName="test-table",
            KeySchema=[
                {"AttributeName": "session_id", "KeyType": "HASH"},
                {"AttributeName": "question_id", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "session_id", "AttributeType": "S"},
                {"AttributeName": "question_id", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        submit_answer.table = table
        yield table


@pytest.fixture
def seeded_table(dynamodb_table):
    """Table pre-populated with one session and three exercises."""
    dynamodb_table.put_item(Item={
        "session_id": SESSION_ID,
        "question_id": "SESSION",
        "topic": "German accusative case",
        "category": "grammar",
        "language": "German",
        "feedback_every_n": 2,
        "status": "active",
        "ttl": 9999999999,
    })
    for ex in FAKE_EXERCISES:
        dynamodb_table.put_item(Item={
            "session_id": SESSION_ID,
            "question_id": ex["id"],
            "question": ex["question"],
            "expected_answer": ex["expected_answer"],
        })
    return dynamodb_table


# --- Happy path ---

def test_correct_answer_returns_200_with_next_exercise(seeded_table):
    with patch.object(submit_answer.bedrock, "invoke_model", return_value=bedrock_eval_response(True)):
        response = submit_answer.lambda_handler(make_event(exercise_id="01", answer="Ich sehe den Mann."), {})
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["is_correct"] is True
    assert body["next_exercise"]["id"] == "02"
    assert "feedback" not in body


def test_incorrect_answer_returns_200_with_is_correct_false(seeded_table):
    with patch.object(submit_answer.bedrock, "invoke_model", return_value=bedrock_eval_response(False)):
        response = submit_answer.lambda_handler(make_event(exercise_id="01", answer="wrong"), {})
    assert response["statusCode"] == 200
    assert json.loads(response["body"])["is_correct"] is False


def test_answer_persisted_to_dynamodb(seeded_table):
    with patch.object(submit_answer.bedrock, "invoke_model", return_value=bedrock_eval_response(True)):
        submit_answer.lambda_handler(make_event(exercise_id="01", answer="Ich sehe den Mann."), {})
    item = seeded_table.get_item(Key={"session_id": SESSION_ID, "question_id": "01"})["Item"]
    assert item["user_answer"] == "Ich sehe den Mann."
    assert item["is_correct"] is True


def test_feedback_triggered_every_n_answers(seeded_table):
    # feedback_every_n = 2, so feedback fires after 2nd answer
    eval_mock = MagicMock(side_effect=[bedrock_eval_response(True), bedrock_eval_response(False)])
    feedback_text = "You're doing well!"

    def invoke_side_effect(**kwargs):
        # Detect feedback call by max_tokens or by call order
        if eval_mock.call_count <= 1:
            return bedrock_eval_response(True)
        return bedrock_eval_response(False)

    # First answer (no feedback expected)
    with patch.object(submit_answer.bedrock, "invoke_model", return_value=bedrock_eval_response(True)):
        r1 = submit_answer.lambda_handler(make_event(exercise_id="01", answer="Ich sehe den Mann."), {})
    assert "feedback" not in json.loads(r1["body"])

    # Second answer (feedback expected — answer_count=2, 2%2==0)
    responses = [bedrock_eval_response(False), bedrock_feedback_response(feedback_text)]
    call_count = [0]

    def invoke_model(**kwargs):
        r = responses[call_count[0]]
        call_count[0] += 1
        return r

    with patch.object(submit_answer.bedrock, "invoke_model", side_effect=invoke_model):
        r2 = submit_answer.lambda_handler(make_event(exercise_id="02", answer="wrong"), {})
    body2 = json.loads(r2["body"])
    assert body2["feedback"] == feedback_text


def test_last_exercise_marks_session_complete_and_returns_mistakes(seeded_table):
    # Pre-answer exercises 01 and 02
    seeded_table.update_item(
        Key={"session_id": SESSION_ID, "question_id": "01"},
        UpdateExpression="SET user_answer = :ua, is_correct = :ic",
        ExpressionAttributeValues={":ua": "Ich sehe den Mann.", ":ic": True},
    )
    seeded_table.update_item(
        Key={"session_id": SESSION_ID, "question_id": "02"},
        UpdateExpression="SET user_answer = :ua, is_correct = :ic",
        ExpressionAttributeValues={":ua": "wrong", ":ic": False},
    )

    # Answer exercise 03 (last one) — 3 % 2 != 0, no feedback
    with patch.object(submit_answer.bedrock, "invoke_model", return_value=bedrock_eval_response(True)):
        response = submit_answer.lambda_handler(make_event(exercise_id="03", answer="Wir brauchen das Auto."), {})

    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert body["next_exercise"] is None
    assert "mistakes" in body
    # exercise 02 was wrong
    assert len(body["mistakes"]) == 1
    assert body["mistakes"][0]["exercise_id"] == "02"

    # Session should be marked complete in DynamoDB
    session = seeded_table.get_item(Key={"session_id": SESSION_ID, "question_id": "SESSION"})["Item"]
    assert session["status"] == "complete"


# --- Validation errors ---

def test_missing_path_param_returns_400():
    event = {"pathParameters": {}, "body": json.dumps({"exercise_id": "01", "answer": "x"})}
    response = submit_answer.lambda_handler(event, {})
    assert response["statusCode"] == 400


def test_missing_body_returns_400():
    response = submit_answer.lambda_handler({"pathParameters": {"id": SESSION_ID}}, {})
    assert response["statusCode"] == 400


def test_invalid_json_body_returns_400():
    response = submit_answer.lambda_handler({"pathParameters": {"id": SESSION_ID}, "body": "not json"}, {})
    assert response["statusCode"] == 400


def test_missing_exercise_id_returns_400():
    response = submit_answer.lambda_handler(make_event(exercise_id=None, answer="x"), {})
    assert response["statusCode"] == 400


def test_missing_answer_returns_400():
    response = submit_answer.lambda_handler(make_event(exercise_id="01", answer=None), {})
    assert response["statusCode"] == 400


# --- Not found / conflict ---

def test_session_not_found_returns_404(seeded_table):
    event = {
        "pathParameters": {"id": "nonexistent-session"},
        "body": json.dumps({"exercise_id": "01", "answer": "x"}),
    }
    with patch.object(submit_answer.bedrock, "invoke_model", return_value=bedrock_eval_response(True)):
        response = submit_answer.lambda_handler(event, {})
    assert response["statusCode"] == 404


def test_session_complete_returns_409(seeded_table):
    seeded_table.update_item(
        Key={"session_id": SESSION_ID, "question_id": "SESSION"},
        UpdateExpression="SET #s = :c",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":c": "complete"},
    )
    response = submit_answer.lambda_handler(make_event(exercise_id="01", answer="x"), {})
    assert response["statusCode"] == 409


def test_exercise_not_found_returns_404(seeded_table):
    event = {
        "pathParameters": {"id": SESSION_ID},
        "body": json.dumps({"exercise_id": "99", "answer": "x"}),
    }
    with patch.object(submit_answer.bedrock, "invoke_model", return_value=bedrock_eval_response(True)):
        response = submit_answer.lambda_handler(event, {})
    assert response["statusCode"] == 404


# --- Bedrock failure ---

def test_claude_invalid_eval_json_returns_502(seeded_table):
    body_bytes = json.dumps({"content": [{"type": "text", "text": "not json at all"}]}).encode()
    mock_body = MagicMock()
    mock_body.read.return_value = body_bytes
    with patch.object(submit_answer.bedrock, "invoke_model", return_value={"body": mock_body}):
        response = submit_answer.lambda_handler(make_event(exercise_id="01", answer="x"), {})
    assert response["statusCode"] == 502
