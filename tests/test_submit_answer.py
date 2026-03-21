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


def seed_session(dynamodb_table, feedback_mode="end", lang="en"):
    dynamodb_table.put_item(Item={
        "session_id": SESSION_ID,
        "question_id": "SESSION",
        "topic": "German accusative case",
        "category": "grammar",
        "language": "German",
        "level": "B1",
        "feedback_mode": feedback_mode,
        "lang": lang,
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


@pytest.fixture
def seeded_table(dynamodb_table):
    """Table pre-populated with feedback_mode='end' (default)."""
    return seed_session(dynamodb_table, feedback_mode="end")


@pytest.fixture
def seeded_table_each(dynamodb_table):
    """Table pre-populated with feedback_mode='each'."""
    return seed_session(dynamodb_table, feedback_mode="each")


@pytest.fixture
def seeded_table_uk(dynamodb_table):
    """Table pre-populated with lang='uk' and feedback_mode='each'."""
    return seed_session(dynamodb_table, feedback_mode="each", lang="uk")


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


def test_feedback_mode_each_returns_feedback_on_incorrect_answer(seeded_table_each):
    feedback_text = "The correct answer is: Ich sehe den Mann."
    responses = [bedrock_eval_response(False), bedrock_feedback_response(feedback_text)]
    call_count = [0]

    def invoke_model(**kwargs):
        r = responses[call_count[0]]
        call_count[0] += 1
        return r

    with patch.object(submit_answer.bedrock, "invoke_model", side_effect=invoke_model):
        response = submit_answer.lambda_handler(make_event(exercise_id="01", answer="wrong"), {})
    body = json.loads(response["body"])
    assert body["feedback"] == feedback_text


def test_feedback_mode_each_no_feedback_on_correct_answer(seeded_table_each):
    with patch.object(submit_answer.bedrock, "invoke_model", return_value=bedrock_eval_response(True)):
        response = submit_answer.lambda_handler(make_event(exercise_id="01", answer="Ich sehe den Mann."), {})
    body = json.loads(response["body"])
    assert body["is_correct"] is True
    assert "feedback" not in body


def test_feedback_mode_end_no_feedback_mid_session(seeded_table):
    with patch.object(submit_answer.bedrock, "invoke_model", return_value=bedrock_eval_response(True)):
        response = submit_answer.lambda_handler(make_event(exercise_id="01", answer="Ich sehe den Mann."), {})
    assert "feedback" not in json.loads(response["body"])


def test_session_complete_returns_mistakes_and_end_feedback(seeded_table):
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

    feedback_text = "Well done overall!"
    responses = [bedrock_eval_response(True), bedrock_feedback_response(feedback_text)]
    call_count = [0]

    def invoke_model(**kwargs):
        r = responses[call_count[0]]
        call_count[0] += 1
        return r

    with patch.object(submit_answer.bedrock, "invoke_model", side_effect=invoke_model):
        response = submit_answer.lambda_handler(make_event(exercise_id="03", answer="Wir brauchen das Auto."), {})

    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert body["next_exercise"] is None
    assert len(body["mistakes"]) == 1
    assert body["mistakes"][0]["exercise_id"] == "02"
    assert body["feedback"] == feedback_text

    session = seeded_table.get_item(Key={"session_id": SESSION_ID, "question_id": "SESSION"})["Item"]
    assert session["status"] == "complete"


def test_session_complete_feedback_mode_each_no_end_feedback(seeded_table_each):
    seeded_table_each.update_item(
        Key={"session_id": SESSION_ID, "question_id": "01"},
        UpdateExpression="SET user_answer = :ua, is_correct = :ic",
        ExpressionAttributeValues={":ua": "Ich sehe den Mann.", ":ic": True},
    )
    seeded_table_each.update_item(
        Key={"session_id": SESSION_ID, "question_id": "02"},
        UpdateExpression="SET user_answer = :ua, is_correct = :ic",
        ExpressionAttributeValues={":ua": "Sie kauft das Buch.", ":ic": True},
    )

    # Last answer correct — no per-answer feedback, no end-of-session feedback for mode "each"
    with patch.object(submit_answer.bedrock, "invoke_model", return_value=bedrock_eval_response(True)):
        response = submit_answer.lambda_handler(make_event(exercise_id="03", answer="Wir brauchen das Auto."), {})

    body = json.loads(response["body"])
    assert body["next_exercise"] is None
    assert "mistakes" in body
    assert "feedback" not in body


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


def test_wrong_user_returns_403(dynamodb_table):
    seed_session(dynamodb_table)
    dynamodb_table.update_item(
        Key={"session_id": SESSION_ID, "question_id": "SESSION"},
        UpdateExpression="SET user_id = :uid",
        ExpressionAttributeValues={":uid": "owner-sub"},
    )
    event = {
        "pathParameters": {"id": SESSION_ID},
        "body": json.dumps({"exercise_id": "01", "answer": "x"}),
        "requestContext": {"authorizer": {"jwt": {"claims": {"sub": "different-sub"}}}},
    }
    response = submit_answer.lambda_handler(event, {})
    assert response["statusCode"] == 403


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

def test_answer_too_long_returns_400(seeded_table):
    long_answer = "a" * 301
    response = submit_answer.lambda_handler(make_event(exercise_id="01", answer=long_answer), {})
    assert response["statusCode"] == 400


def test_claude_eval_json_embedded_in_text_is_extracted(seeded_table):
    # Claude sometimes wraps the JSON in an explanation — we should still extract is_correct
    explanation = 'The answer is wrong. {"is_correct": false} The adjective ending is incorrect.'
    body_bytes = json.dumps({"content": [{"type": "text", "text": explanation}]}).encode()
    mock_body = MagicMock()
    mock_body.read.return_value = body_bytes
    with patch.object(submit_answer.bedrock, "invoke_model", return_value={"body": mock_body}):
        response = submit_answer.lambda_handler(make_event(exercise_id="01", answer="wrong"), {})
    assert response["statusCode"] == 200
    assert json.loads(response["body"])["is_correct"] is False


def test_claude_invalid_eval_json_returns_502(seeded_table):
    body_bytes = json.dumps({"content": [{"type": "text", "text": "not json at all"}]}).encode()
    mock_body = MagicMock()
    mock_body.read.return_value = body_bytes
    with patch.object(submit_answer.bedrock, "invoke_model", return_value={"body": mock_body}):
        response = submit_answer.lambda_handler(make_event(exercise_id="01", answer="x"), {})
    assert response["statusCode"] == 502


def test_claude_non_boolean_is_correct_returns_502(seeded_table):
    # Claude returns is_correct as a string instead of boolean
    body_bytes = json.dumps({"content": [{"type": "text", "text": '{"is_correct": "true"}'}]}).encode()
    mock_body = MagicMock()
    mock_body.read.return_value = body_bytes
    with patch.object(submit_answer.bedrock, "invoke_model", return_value={"body": mock_body}):
        response = submit_answer.lambda_handler(make_event(exercise_id="01", answer="x"), {})
    assert response["statusCode"] == 502


# --- Ukrainian language ---

def test_lang_uk_includes_language_instruction_in_feedback_prompt(seeded_table_uk):
    """When lang='uk' and answer is incorrect, the feedback prompt sent to Claude must contain the Ukrainian instruction."""
    captured_calls = []

    def invoke_model(**kwargs):
        captured_calls.append(kwargs)
        r = bedrock_eval_response(False) if len(captured_calls) == 1 else bedrock_feedback_response("Правильна відповідь: Ich sehe den Mann.")
        return r

    with patch.object(submit_answer.bedrock, "invoke_model", side_effect=invoke_model):
        response = submit_answer.lambda_handler(make_event(exercise_id="01", answer="wrong"), {})

    assert response["statusCode"] == 200
    # Second call is the feedback call — its body must contain the Ukrainian instruction
    feedback_call_body = json.loads(captured_calls[1]["body"])
    feedback_prompt = feedback_call_body["messages"][0]["content"][0]["text"]
    assert "Ukrainian" in feedback_prompt
