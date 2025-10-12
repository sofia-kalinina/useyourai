import boto3
import json

from botocore.exceptions import ClientError

def lambda_handler(event, context):
    # Get the human prompt from the event
    human_prompt = event.get('prompt')
    if not human_prompt:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Prompt is required"})
        }

    # Initialize Bedrock runtime client
    client = boto3.client('bedrock-runtime', region_name='eu-central-1')

    model_id = "meta.llama3-2-1b-instruct-v1:0"

    formatted_prompt = f"""
    <|begin_of_text|><|start_header_id|>user<|end_header_id|>
    {human_prompt}
    <|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>
    """

    native_request = {
        "prompt": formatted_prompt,
        "max_gen_len": 512,
        "temperature": 0.5,
    }

    # Convert the native request to JSON.
    request = json.dumps(native_request)

    try:
        # Invoke the model with the request.
        response = client.invoke_model(modelId=model_id, body=request)

    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        exit(1)

    model_response = json.loads(response["body"].read())
    response_text = model_response["generation"]
    
    return {
        "statusCode": 200,
        "body": json.dumps(response_text)
    }
