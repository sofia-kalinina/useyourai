import boto3
import json

from botocore.exceptions import ClientError

bedrock = boto3.client(service_name='bedrock-runtime', region_name='eu-central-1')

MODEL_ID = "anthropic.claude-sonnet-4-5-20250929-v1:0"
INFERENCE_PROFILE_ID = "eu.anthropic.claude-sonnet-4-5-20250929-v1:0"


def lambda_handler(event, context):
    """
    Example AWS Lambda function to invoke Claude Sonnet 4.5 through Bedrock.
    'event' is expected to contain a 'prompt' key.
    """

    # Validate and extract the prompt from the event body
    user_prompt = None
    body_string = event.get('body')

    if body_string:
        try:
            body = json.loads(body_string)
            user_prompt = body.get('prompt')
            if not user_prompt:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"message": "Prompt is required"})
                }
        except:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Invalid JSON in request body"})
            }
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Request body is required"})
        }

    # Build the message structure for Anthropic Claude model
    body = {
        "messages": [
            {"role": "user", "content": [{"type": "text", "text": user_prompt}]}
        ],
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "temperature": 0.7
    }

    # Invoke the model
    response = bedrock.invoke_model(
        modelId=INFERENCE_PROFILE_ID,
        accept="application/json",
        contentType="application/json",
        body=json.dumps(body)
    )

    # Parse the model output
    model_output = json.loads(response["body"].read())
    reply = model_output["content"][0]["text"]

    return {
        "statusCode": 200,
        "body": json.dumps({"reply": reply})
    }
