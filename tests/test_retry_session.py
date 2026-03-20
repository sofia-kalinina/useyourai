import json
import os
from unittest.mock import MagicMock, patch

import boto3
import pytest
from moto import mock_aws

os.environ["TABLE_NAME"] = "test-table"

import retry_session  # noqa: E402


PARENT_SESSION_ID = "parent-session-123"

FAKE_MISTAKES = [
    {
        "question": "Translate: I see the man.",
        "expected_answer": "Ich sehe den Mann.",
        "user_answer": "Ich sehe der Mann.",
    },
    {
        "question": "Translate: She buys the book.",
        "expected_answer": "Sie kauft das Buch.",
        "user_answer": "Sie kauft die Buch.",
    },
]

FAKE_EXERCISE_DATA = {
    "topic": "German accusative case",
    "category": "grammar",
    "language": "German",
    "exercises": [
        {"id": "01", "question": "Fix the sentence: Ich sehe der Hund.", "expected_answer": "Ich sehe den Hund."},
        {"id": "02", "question": "Fill in the blank: Sie kauft ___ Buch. (das/die/dem)", "expected_answer": "das"},
    ],
}


def bedrock_response_for(data):
    raw = json.dumps(data)
    body_bytes = json.dumps({"content": [{"type": "text", "text": raw}]}).encode()
    mock_body = MagicMock()
    mock_body.read.return_value = body_bytes
    return {"body": mock_body}


def make_event(session_id=PARENT_SESSION_ID, mistakes=None):
    if mistakes is None:
        mistakes = FAKE_MISTAKES
    return {
        "pathParameters": {"id": session_id},
        "body": json.dumps({"mistakes": mistakes}),
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
        retry_session.table = table
        yield table


@pytest.fixture
def seeded_table(dynamodb_table):
    dynamodb_table.put_item(Item={
        "session_id": PARENT_SESSION_ID,
        "question_id": "SESSION",
        "topic": "German accusative case",
        "category": "grammar",
        "language": "German",
        "level": "B1",
        "feedback_mode": "end",
        "lang": "en",
        "status": "complete",
        "ttl": 9999999999,
    })
    return dynamodb_table


# --- Happy path ---

def test_valid_request_returns_200(seeded_table):
    with patch.object(retry_session.bedrock, "invoke_model", return_value=bedrock_response_for(FAKE_EXERCISE_DATA)):
        response = retry_session.lambda_handler(make_event(), {})
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert "session_id" in body
    assert body["exercise"]["id"] == "01"
    assert "question" in body["exercise"]
    assert "expected_answer" not in body["exercise"]


def test_retry_session_persists_metadata_with_parent_link(seeded_table):
    with patch.object(retry_session.bedrock, "invoke_model", return_value=bedrock_response_for(FAKE_EXERCISE_DATA)):
        response = retry_session.lambda_handler(make_event(), {})
    session_id = json.loads(response["body"])["session_id"]
    item = seeded_table.get_item(Key={"session_id": session_id, "question_id": "SESSION"})["Item"]
    assert item["parent_session_id"] == PARENT_SESSION_ID
    assert item["status"] == "active"
    assert item["level"] == "B1"
    assert item["feedback_mode"] == "end"
    assert item["lang"] == "en"
    assert "ttl" in item


def test_retry_session_persists_exercises(seeded_table):
    with patch.object(retry_session.bedrock, "invoke_model", return_value=bedrock_response_for(FAKE_EXERCISE_DATA)):
        response = retry_session.lambda_handler(make_event(), {})
    session_id = json.loads(response["body"])["session_id"]
    exercise = seeded_table.get_item(Key={"session_id": session_id, "question_id": "01"})["Item"]
    assert exercise["question"] == "Fix the sentence: Ich sehe der Hund."
    assert exercise["expected_answer"] == "Ich sehe den Hund."


def test_inherits_lang_from_parent_session(seeded_table):
    seeded_table.update_item(
        Key={"session_id": PARENT_SESSION_ID, "question_id": "SESSION"},
        UpdateExpression="SET lang = :l",
        ExpressionAttributeValues={":l": "uk"},
    )
    captured_calls = []

    def invoke_model(**kwargs):
        captured_calls.append(kwargs)
        return bedrock_response_for(FAKE_EXERCISE_DATA)

    with patch.object(retry_session.bedrock, "invoke_model", side_effect=invoke_model):
        retry_session.lambda_handler(make_event(), {})

    call_body = json.loads(captured_calls[0]["body"])
    user_message = call_body["messages"][0]["content"][0]["text"]
    assert "Ukrainian" in user_message


# --- Validation errors ---

def test_missing_path_param_returns_400():
    event = {"pathParameters": {}, "body": json.dumps({"mistakes": FAKE_MISTAKES})}
    response = retry_session.lambda_handler(event, {})
    assert response["statusCode"] == 400


def test_missing_body_returns_400():
    response = retry_session.lambda_handler({"pathParameters": {"id": PARENT_SESSION_ID}}, {})
    assert response["statusCode"] == 400


def test_invalid_json_body_returns_400():
    response = retry_session.lambda_handler({"pathParameters": {"id": PARENT_SESSION_ID}, "body": "not json"}, {})
    assert response["statusCode"] == 400


def test_missing_mistakes_returns_400():
    event = {"pathParameters": {"id": PARENT_SESSION_ID}, "body": json.dumps({})}
    response = retry_session.lambda_handler(event, {})
    assert response["statusCode"] == 400


def test_empty_mistakes_list_returns_400():
    event = {"pathParameters": {"id": PARENT_SESSION_ID}, "body": json.dumps({"mistakes": []})}
    response = retry_session.lambda_handler(event, {})
    assert response["statusCode"] == 400


def test_malformed_mistake_item_returns_400():
    bad_mistakes = [{"question": "Q?"}]  # missing expected_answer and user_answer
    event = {"pathParameters": {"id": PARENT_SESSION_ID}, "body": json.dumps({"mistakes": bad_mistakes})}
    response = retry_session.lambda_handler(event, {})
    assert response["statusCode"] == 400


def test_mistake_field_too_long_returns_400():
    long_mistakes = [{
        "question": "Q?",
        "expected_answer": "A",
        "user_answer": "x" * 501,
    }]
    event = {"pathParameters": {"id": PARENT_SESSION_ID}, "body": json.dumps({"mistakes": long_mistakes})}
    response = retry_session.lambda_handler(event, {})
    assert response["statusCode"] == 400


def test_too_many_mistakes_returns_400():
    too_many = [{"question": "Q?", "expected_answer": "A", "user_answer": "B"}] * 21
    event = {"pathParameters": {"id": PARENT_SESSION_ID}, "body": json.dumps({"mistakes": too_many})}
    response = retry_session.lambda_handler(event, {})
    assert response["statusCode"] == 400


# --- Not found ---

def test_parent_session_not_found_returns_404(seeded_table):
    event = {
        "pathParameters": {"id": "nonexistent-session"},
        "body": json.dumps({"mistakes": FAKE_MISTAKES}),
    }
    response = retry_session.lambda_handler(event, {})
    assert response["statusCode"] == 404


# --- Bedrock failures ---

def test_claude_invalid_json_returns_502(seeded_table):
    mock_body = MagicMock()
    mock_body.read.return_value = json.dumps({"content": [{"type": "text", "text": "not json at all"}]}).encode()
    with patch.object(retry_session.bedrock, "invoke_model", return_value={"body": mock_body}):
        response = retry_session.lambda_handler(make_event(), {})
    assert response["statusCode"] == 502


def test_claude_malformed_exercise_schema_returns_502(seeded_table):
    bad_data = {**FAKE_EXERCISE_DATA, "exercises": [{"id": "01"}]}  # missing question and expected_answer
    with patch.object(retry_session.bedrock, "invoke_model", return_value=bedrock_response_for(bad_data)):
        response = retry_session.lambda_handler(make_event(), {})
    assert response["statusCode"] == 502
