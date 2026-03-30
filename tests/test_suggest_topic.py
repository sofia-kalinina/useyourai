import json
from unittest.mock import MagicMock, patch

import suggest_topic


FAKE_TOPICS = [
    "Separable verbs in the present tense",
    "Accusative vs. dative prepositions",
    "Modal verbs with infinitive",
    "Adjective endings after definite articles",
    "Two-way prepositions with movement vs. location",
]

FAKE_RESPONSE = {"topics": FAKE_TOPICS}


def bedrock_response_for(data):
    raw = json.dumps(data)
    body_bytes = json.dumps({"content": [{"type": "text", "text": raw}]}).encode()
    mock_body = MagicMock()
    mock_body.read.return_value = body_bytes
    return {"body": mock_body}


def make_event(language="German", level="B1"):
    payload = {}
    if language is not None:
        payload["language"] = language
    if level is not None:
        payload["level"] = level
    return {"body": json.dumps(payload)}


def test_valid_request_returns_200():
    with patch.object(suggest_topic.bedrock, "invoke_model", return_value=bedrock_response_for(FAKE_RESPONSE)):
        response = suggest_topic.lambda_handler(make_event(), {})
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["topics"] == FAKE_TOPICS


def test_missing_body_returns_400():
    response = suggest_topic.lambda_handler({}, {})
    assert response["statusCode"] == 400


def test_missing_language_returns_400():
    response = suggest_topic.lambda_handler({"body": json.dumps({"level": "B1"})}, {})
    assert response["statusCode"] == 400


def test_missing_level_returns_400():
    response = suggest_topic.lambda_handler({"body": json.dumps({"language": "German"})}, {})
    assert response["statusCode"] == 400


def test_invalid_level_returns_400():
    response = suggest_topic.lambda_handler(make_event(level="Z9"), {})
    assert response["statusCode"] == 400


def test_language_too_long_returns_400():
    response = suggest_topic.lambda_handler(make_event(language="a" * 51), {})
    assert response["statusCode"] == 400


def test_invalid_json_body_returns_400():
    response = suggest_topic.lambda_handler({"body": "not json"}, {})
    assert response["statusCode"] == 400


def test_claude_invalid_json_returns_502():
    mock_body = MagicMock()
    mock_body.read.return_value = json.dumps({"content": [{"type": "text", "text": "not json at all"}]}).encode()
    with patch.object(suggest_topic.bedrock, "invoke_model", return_value={"body": mock_body}):
        response = suggest_topic.lambda_handler(make_event(), {})
    assert response["statusCode"] == 502


def test_claude_wrong_topic_count_returns_502():
    bad_data = {"topics": ["Only one topic"]}
    with patch.object(suggest_topic.bedrock, "invoke_model", return_value=bedrock_response_for(bad_data)):
        response = suggest_topic.lambda_handler(make_event(), {})
    assert response["statusCode"] == 502


def test_claude_non_string_topics_returns_502():
    bad_data = {"topics": [1, 2, 3, 4, 5]}
    with patch.object(suggest_topic.bedrock, "invoke_model", return_value=bedrock_response_for(bad_data)):
        response = suggest_topic.lambda_handler(make_event(), {})
    assert response["statusCode"] == 502
