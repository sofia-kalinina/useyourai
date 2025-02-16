import boto3
import uuid
import json
import time
import os

# Get environment variables
environment = os.getenv('ENVIRONMENT')
if environment is None:
    raise ValueError("Environment variable 'ENVIRONMENT' is not set.")

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(f"LanguageLearningTable-{environment}")

def lambda_handler(event, context):
    """Creates a new session when a user enters the app."""
    
    # Generate a new session ID
    session_id = str(uuid.uuid4())

    # Current timestamp for session creation
    timestamp = int(time.time())

    # Assume question_id is a required key in the table
    question_id = str(uuid.uuid4())  # You can change this to a real ID if needed

    # Prepare the session data
    session_data = {
        "question_id": question_id,  # Add the missing key
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
