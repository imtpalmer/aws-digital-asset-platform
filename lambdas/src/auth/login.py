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
COGNITO_USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
AWS_REGION = os.getenv('AWS_REGION')

if not all([COGNITO_USER_POOL_ID, COGNITO_USER_POOL_CLIENT_ID, AWS_REGION]):
    raise ValueError("Missing required environment variable: COGNITO_USER_POOL_CLIENT_ID, COGNITO_USER_POOL_ID, AWS_REGION")

def lambda_handler(event, context):
    """
    Lambda function handler for user login.
    """
    logger = configure_logging()
    logger.info("login AWS Lambda called")
    logger.debug(f"Received event: {json.dumps(event)}")

    # Get CORS headers
    cors_headers = get_cors_headers_from_event(event, logger)

    # Determine the HTTP method from routeKey if available, otherwise fallback to httpMethod
    http_method = (
        event.get('routeKey', '').split(' ')[0] 
        if 'routeKey' in event 
        else event.get('httpMethod')
    )

    logger.debug(f'Method: {http_method} received')

    if http_method == 'OPTIONS':
        return generate_response(200,'CORS preflight', cors_headers, logger)
    
    if http_method == 'POST':
        return handle_post_request(event, logger, cors_headers)

    return generate_response(405, f'Method {http_method} not allowed', cors_headers)


def handle_post_request(event, logger, cors_headers):
    """
    Handle POST requests for user login.
    """
    logger.info("Processing POST request")
    try:
        # Parse the request body
        body = json.loads(event.get('body', '{}'))
        username = body.get('username')
        password = body.get('password')

        # Validate required fields
        if not all([username, password]):
            return generate_response(400, 'Username and password are required', cors_headers)

        # Authenticate the user
        auth_result = cognito_client.admin_initiate_auth(
            UserPoolId=COGNITO_USER_POOL_ID,
            ClientId=COGNITO_USER_POOL_CLIENT_ID,
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )['AuthenticationResult']

        logger.info(f"Authentication successful for user: {username}")
        return generate_response(200, auth_result, cors_headers)

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
        'UserNotConfirmedException': 'User account is not confirmed. Please confirm your account before logging in.',
        'NotAuthorizedException': 'Incorrect username or password.',
        'PasswordResetRequiredException': 'Password reset is required.',
        'UserNotFoundException': 'User does not exist.'
    }

    return generate_response(400, error_messages.get(error_code, 'Authentication failed. Please try again.'), cors_headers)

def generate_response(status_code, message, cors_headers, logger=None):
    """
    Helper function to generate HTTP responses with CORS headers.
    Accepts an optional logger. If none is provided, it uses the default logger.
    """
    # Construct the response
    response =  {
        'statusCode': status_code,
        'headers': cors_headers,
        'body': json.dumps(message)
    }

    if logger :
        # Log the status code, message, and CORS headers
        logger.info(f"Generating response {response}" )

    return response