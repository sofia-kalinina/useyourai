import boto3
import json

def lambda_handler(event, context):
    # Get the human prompt from the event
    human_prompt = event.get('prompt')
    if not human_prompt:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Prompt is required"})
        }

    # Initialize Bedrock runtime client
    bedrock_runtime = boto3.client('bedrock-runtime', region_name='eu-central-1')

    # Prepare the payload for Bedrock
    payload = { 
        "prompt": f"\n\nHuman: {human_prompt}\n\nAssistant:",
        "max_tokens_to_sample": 300,
        "temperature": 0.5,
        "top_k": 250,
        "top_p": 1,
        "stop_sequences": ["\n\nHuman:"],
        "anthropic_version": "bedrock-2023-05-31"
    }

    # Invoke the Bedrock model
    response = bedrock_runtime.invoke_model(
        modelId="anthropic.claude-v2",
        contentType="application/json",
        accept="application/json",
        body=json.dumps(payload)
    )

    # Parse the response from Bedrock
    response_body = json.loads(response['body'].read().decode('utf-8'))
    
    return {
        "statusCode": 200,
        "body": json.dumps(response_body)
    }
