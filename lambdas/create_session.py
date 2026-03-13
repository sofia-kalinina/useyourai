import boto3
import json
import os
import time
import uuid

from botocore.exceptions import ClientError

table_name = os.getenv('TABLE_NAME')
if not table_name:
    raise ValueError("Environment variable 'TABLE_NAME' is not set.")

dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
table = dynamodb.Table(table_name)

bedrock = boto3.client(service_name='bedrock-runtime', region_name='eu-central-1')

INFERENCE_PROFILE_ID = "eu.anthropic.claude-sonnet-4-5-20250929-v1:0"

SYSTEM_PROMPT = """You are a language exercise generator. Given a user's free-text request, generate a set of practice exercises.
Return ONLY valid JSON in this exact format, with no other text before or after:
{
  "topic": "<specific topic name>",
  "category": "<e.g. grammar, vocabulary, pronunciation>",
  "language": "<target language>",
  "exercises": [
    {"id": "01", "question": "<exercise question>", "expected_answer": "<correct answer>"},
    {"id": "02", "question": "...", "expected_answer": "..."}
  ]
}"""


def lambda_handler(event, context):
    body_string = event.get('body')
    if not body_string:
        return {"statusCode": 400, "body": json.dumps({"error": "Request body is required"})}

    try:
        body = json.loads(body_string)
    except (json.JSONDecodeError, ValueError):
        return {"statusCode": 400, "body": json.dumps({"error": "Invalid JSON in request body"})}

    prompt = body.get('prompt')
    feedback_every_n = body.get('feedback_every_n')

    if not prompt:
        return {"statusCode": 400, "body": json.dumps({"error": "'prompt' is required"})}
    if feedback_every_n is None:
        return {"statusCode": 400, "body": json.dumps({"error": "'feedback_every_n' is required"})}

    try:
        bedrock_response = bedrock.invoke_model(
            modelId=INFERENCE_PROFILE_ID,
            accept="application/json",
            contentType="application/json",
            body=json.dumps({
                "system": SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2048,
                "temperature": 0.7
            })
        )
    except ClientError as e:
        return {"statusCode": 502, "body": json.dumps({"error": "Failed to call Claude", "detail": str(e)})}

    model_output = json.loads(bedrock_response["body"].read())
    raw_text = model_output["content"][0]["text"]

    try:
        exercise_data = json.loads(raw_text)
    except (json.JSONDecodeError, ValueError):
        return {"statusCode": 502, "body": json.dumps({"error": "Claude returned invalid JSON"})}

    exercises = exercise_data.get("exercises", [])
    if not exercises:
        return {"statusCode": 502, "body": json.dumps({"error": "Claude returned no exercises"})}

    session_id = str(uuid.uuid4())
    ttl = int(time.time()) + 24 * 60 * 60

    with table.batch_writer() as batch:
        batch.put_item(Item={
            "session_id": session_id,
            "question_id": "SESSION",
            "topic": exercise_data.get("topic", ""),
            "category": exercise_data.get("category", ""),
            "language": exercise_data.get("language", ""),
            "feedback_every_n": feedback_every_n,
            "status": "active",
            "ttl": ttl
        })
        for exercise in exercises:
            batch.put_item(Item={
                "session_id": session_id,
                "question_id": exercise["id"],
                "question": exercise["question"],
                "expected_answer": exercise["expected_answer"]
            })

    first_exercise = exercises[0]
    return {
        "statusCode": 200,
        "body": json.dumps({
            "session_id": session_id,
            "exercise": {
                "id": first_exercise["id"],
                "question": first_exercise["question"]
            }
        })
    }
