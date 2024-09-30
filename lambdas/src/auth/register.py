import json
import os
import boto3
from botocore.exceptions import ClientError

from logging_utils import configure_logging
from cors_utils import get_cors_headers_from_event

# Initialize Cognito client at cold start
cognito_client = boto3.client('cognito-idp')

# Validate environment variable at cold start
COGNITO_USER_POOL_CLIENT_ID = os.getenv('COGNITO_USER_POOL_CLIENT_ID')
if not COGNITO_USER_POOL_CLIENT_ID:
    raise ValueError("Missing required environment variable: COGNITO_USER_POOL_CLIENT_ID")

def lambda_handler(event, context):
    """
    Lambda function handler for user registration.
    """
    logger = configure_logging()
    logger.info("Lambda function started")
    logger.info(f"Received event: {json.dumps(event)}")

    # Get CORS headers
    cors_headers = get_cors_headers_from_event(event, logger)

    # Determine the HTTP method from routeKey if available, otherwise fallback to httpMethod
    http_method = (
        event.get('routeKey', '').split(' ')[0] 
        if 'routeKey' in event 
        else event.get('httpMethod')
    )

    if http_method == 'OPTIONS':
        return generate_response(200, 'CORS preflight', cors_headers)
    
    if http_method == 'POST':
        return handle_post_request(event, logger, cors_headers)

    return generate_response(405, f'Method {http_method} not allowed', cors_headers)


def handle_post_request(event, logger, cors_headers):
    """
    Handle POST requests for user registration.
    """
    try:
        # Parse the request body
        body = json.loads(event.get('body', '{}'))
        username = body.get('username')
        password = body.get('password')
        email = body.get('email')

        # Validate required fields
        if not all([username, password, email]):
            return generate_response(400, 'Username, password, and email are required.', cors_headers)

        # Call Cognito sign up
        response = cognito_client.sign_up(
            ClientId=COGNITO_USER_POOL_CLIENT_ID,
            Username=username,
            Password=password,
            UserAttributes=[{'Name': 'email', 'Value': email}]
        )

        logger.info(f"User {username} registration successful")
        return generate_response(200, 'User registration successful!', cors_headers)

    except ClientError as e:
        error_message = e.response['Error']['Message']
        logger.error(f"Error during user registration: {error_message}")
        return generate_response(400, error_message, cors_headers)

    except (json.JSONDecodeError, ValueError):
        logger.error("Invalid JSON in request body.")
        return generate_response(400, 'Invalid JSON in request body.', cors_headers)

    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return generate_response(500, f'An unexpected error occurred: {str(e)}', cors_headers)


def generate_response(status_code, message, cors_headers):
    """
    Helper function to generate HTTP responses with CORS headers.
    """
    return {
        'statusCode': status_code,
        'headers': cors_headers,
        'body': json.dumps(message)
    }