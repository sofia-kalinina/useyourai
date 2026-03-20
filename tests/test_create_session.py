import json
import os
from unittest.mock import MagicMock, patch

import boto3
import pytest
from moto import mock_aws

os.environ["TABLE_NAME"] = "test-table"

import create_session  # noqa: E402


FAKE_EXERCISE_DATA = {
    "topic": "German accusative case",
    "category": "grammar",
    "language": "German",
    "exercises": [
        {"id": "01", "question": "Translate: I see the man.", "expected_answer": "Ich sehe den Mann."},
        {"id": "02", "question": "Translate: She buys the book.", "expected_answer": "Sie kauft das Buch."},
    ],
}


def bedrock_response_for(data):
    raw = json.dumps(data)
    body_bytes = json.dumps({"content": [{"type": "text", "text": raw}]}).encode()
    mock_body = MagicMock()
    mock_body.read.return_value = body_bytes
    return {"body": mock_body}


def make_event(prompt=None, level="B1", feedback_mode="end", lang="en", user_id="test-user-uuid"):
    payload = {}
    if prompt is not None:
        payload["prompt"] = prompt
    if level is not None:
        payload["level"] = level
    if feedback_mode is not None:
        payload["feedback_mode"] = feedback_mode
    if lang is not None:
        payload["lang"] = lang
    if user_id is not None:
        payload["user_id"] = user_id
    return {"body": json.dumps(payload)}


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
        create_session.table = table
        yield table


def test_valid_request_returns_200(dynamodb_table):
    with patch.object(create_session.bedrock, "invoke_model", return_value=bedrock_response_for(FAKE_EXERCISE_DATA)):
        response = create_session.lambda_handler(make_event("10 German accusative exercises"), {})
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert "session_id" in body
    assert body["exercise"]["id"] == "01"
    assert "question" in body["exercise"]
    assert "expected_answer" not in body["exercise"]


def test_valid_request_persists_session_metadata(dynamodb_table):
    with patch.object(create_session.bedrock, "invoke_model", return_value=bedrock_response_for(FAKE_EXERCISE_DATA)):
        response = create_session.lambda_handler(make_event("10 German accusative exercises", level="B1", feedback_mode="end"), {})
    session_id = json.loads(response["body"])["session_id"]
    item = dynamodb_table.get_item(Key={"session_id": session_id, "question_id": "SESSION"})["Item"]
    assert item["topic"] == "German accusative case"
    assert item["language"] == "German"
    assert item["status"] == "active"
    assert item["level"] == "B1"
    assert item["feedback_mode"] == "end"
    assert item["lang"] == "en"
    assert item["user_id"] == "test-user-uuid"
    assert "ttl" in item


def test_valid_request_persists_exercises(dynamodb_table):
    with patch.object(create_session.bedrock, "invoke_model", return_value=bedrock_response_for(FAKE_EXERCISE_DATA)):
        response = create_session.lambda_handler(make_event("10 German accusative exercises"), {})
    session_id = json.loads(response["body"])["session_id"]
    exercise = dynamodb_table.get_item(Key={"session_id": session_id, "question_id": "01"})["Item"]
    assert exercise["question"] == "Translate: I see the man."
    assert exercise["expected_answer"] == "Ich sehe den Mann."


def test_missing_body_returns_400():
    response = create_session.lambda_handler({}, {})
    assert response["statusCode"] == 400


def test_missing_prompt_returns_400():
    response = create_session.lambda_handler(make_event(prompt=None), {})
    assert response["statusCode"] == 400


def test_invalid_level_returns_400():
    response = create_session.lambda_handler(make_event(prompt="some prompt", level="Z9"), {})
    assert response["statusCode"] == 400


def test_invalid_lang_returns_400():
    response = create_session.lambda_handler(make_event(prompt="some prompt", lang="fr"), {})
    assert response["statusCode"] == 400


def test_lang_uk_persisted(dynamodb_table):
    with patch.object(create_session.bedrock, "invoke_model", return_value=bedrock_response_for(FAKE_EXERCISE_DATA)):
        response = create_session.lambda_handler(make_event("10 exercises", lang="uk"), {})
    session_id = json.loads(response["body"])["session_id"]
    item = dynamodb_table.get_item(Key={"session_id": session_id, "question_id": "SESSION"})["Item"]
    assert item["lang"] == "uk"


def test_invalid_feedback_mode_returns_400():
    response = create_session.lambda_handler(make_event(prompt="some prompt", feedback_mode="sometimes"), {})
    assert response["statusCode"] == 400


def test_invalid_json_body_returns_400():
    response = create_session.lambda_handler({"body": "not json"}, {})
    assert response["statusCode"] == 400


def test_prompt_too_long_returns_400():
    long_prompt = "a" * 501
    response = create_session.lambda_handler(make_event(prompt=long_prompt), {})
    assert response["statusCode"] == 400


def test_claude_malformed_exercise_schema_returns_502(dynamodb_table):
    bad_data = {**FAKE_EXERCISE_DATA, "exercises": [{"id": "01"}]}  # missing question and expected_answer
    with patch.object(create_session.bedrock, "invoke_model", return_value=bedrock_response_for(bad_data)):
        response = create_session.lambda_handler(make_event("10 exercises"), {})
    assert response["statusCode"] == 502


def test_claude_invalid_json_returns_502(dynamodb_table):
    mock_body = MagicMock()
    mock_body.read.return_value = json.dumps({"content": [{"type": "text", "text": "not json at all"}]}).encode()
    with patch.object(create_session.bedrock, "invoke_model", return_value={"body": mock_body}):
        response = create_session.lambda_handler(make_event("10 exercises"), {})
    assert response["statusCode"] == 502


def test_missing_user_id_returns_400():
    response = create_session.lambda_handler(make_event(prompt="some prompt", user_id=None), {})
    assert response["statusCode"] == 400


def test_user_id_too_long_returns_400():
    response = create_session.lambda_handler(make_event(prompt="some prompt", user_id="x" * 129), {})
    assert response["statusCode"] == 400
