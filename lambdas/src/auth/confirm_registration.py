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
    Lambda function handler for confirming user registration.
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

    if not http_method:
        return generate_response(400, 'HTTP method not specified', cors_headers)

    if http_method == 'OPTIONS':
        return generate_response(200, 'CORS preflight', cors_headers)
    
    if http_method == 'POST':
        return handle_post_request(event, logger, cors_headers)

    return generate_response(405, f'Method {http_method} not allowed', cors_headers)


def handle_post_request(event, logger, cors_headers):
    """
    Handle POST requests for confirming user registration.
    """
    try:
        # Parse the request body
        body = json.loads(event.get('body', '{}'))
        username = body.get('username')
        confirmation_code = body.get('confirmation_code')

        # Validate required fields
        if not all([username, confirmation_code]):
            return generate_response(400, 'Username and confirmation code are required', cors_headers)

        # Confirm the registration
        response = cognito_client.confirm_sign_up(
            ClientId=COGNITO_USER_POOL_CLIENT_ID,
            Username=username,
            ConfirmationCode=confirmation_code
        )

        logger.info(f"User {username} confirmed successfully.")
        return generate_response(200, 'User confirmed successfully', cors_headers)

    except ClientError as e:
        logger.error("ClientError: %s", e)
        return handle_cognito_errors(e, cors_headers)

    except Exception as e:
        logger.error("Unhandled exception: %s", str(e))
        return generate_response(500, 'Internal server error', cors_headers)


def handle_cognito_errors(error, cors_headers):
    """
    Handle specific ClientError exceptions from Cognito.
    """
    error_code = error.response['Error']['Code']
    error_messages = {
        'CodeMismatchException': 'Invalid confirmation code.',
        'ExpiredCodeException': 'The confirmation code has expired.',
        'NotAuthorizedException': 'User already confirmed.',
        'UserNotFoundException': 'User does not exist.'
    }

    return generate_response(400, error_messages.get(error_code, 'Confirmation failed. Please try again.'), cors_headers)


def generate_response(status_code, message, cors_headers):
    """
    Helper function to generate HTTP responses with CORS headers.
    """
    return {
        'statusCode': status_code,
        'headers': cors_headers,
        'body': json.dumps(message)
    }