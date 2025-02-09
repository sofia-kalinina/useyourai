import boto3
import uuid
import json
import time

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('LanguageLearningTable-{ENVIRONMENT}')

def lambda_handler(event, context):
    """Creates a new session when a user enters the app."""
    
    # Generate a new session ID
    session_id = str(uuid.uuid4())

    # Current timestamp for session creation
    timestamp = int(time.time())

    # Prepare the session data
    session_data = {
        "session_id": session_id,
        "created_at": timestamp,
        "status": "active",  # Can be "active", "completed", etc.
        "ttl": timestamp + (24 * 60 * 60)  # Auto-delete after 24 hours
    }

    # Store in DynamoDB
    table.put_item(Item=session_data)

    # Return the session ID
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Session created successfully!",
            "session_id": session_id
        })
    }
