import json
import jwt
from jwt import PyJWKClient
import boto3
import os
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from logging_utils import configure_logging
from cors_utils import get_cors_headers_from_event

# Initialize AWS clients
dynamodb_client = boto3.client('dynamodb')

# Validate environment variables at cold start
DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME')
COGNITO_USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
AWS_REGION = os.getenv('AWS_REGION')

if not all([DYNAMODB_TABLE_NAME, COGNITO_USER_POOL_ID, AWS_REGION]):
    raise ValueError("Missing required environment variables")

# Initialize DynamoDB table resource
table = boto3.resource('dynamodb').Table(DYNAMODB_TABLE_NAME)

def lambda_handler(event, context):
    """
    Lambda function handler for querying user documents from DynamoDB.
    """
    logger = configure_logging()
    logger.info("Lambda function started")
    logger.debug("Received event: %s", json.dumps(event))

    # Get CORS headers
    cors_headers = get_cors_headers_from_event(event, logger)

    # Determine the HTTP method
    http_method = event.get('routeKey', '').split()[0] or event.get('httpMethod')

    if http_method == 'OPTIONS':
        return generate_response(200, 'CORS preflight', cors_headers, logger)

    elif http_method == 'POST':
        return handle_post_request(event, logger, cors_headers)

    return generate_response(405, 'Method not allowed', cors_headers, logger)


def handle_post_request(event, logger, cors_headers):
    """
    Handle POST request for querying user documents.
    """
    try:
        # Extract JWT token
        token = extract_jwt_token(event, logger)
        if not token:
            return generate_response(401, 'Authorization header missing', cors_headers, logger)

        # Validate JWT token
        user_id = validate_jwt_token(token, logger)
        if not user_id:
            return generate_response(401, 'Invalid JWT token', cors_headers, logger)

        # Query DynamoDB for user documents
        return query_user_documents(user_id, logger, cors_headers)

    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return generate_response(500, f'An unexpected error occurred: {str(e)}', cors_headers, logger)


def extract_jwt_token(event, logger):
    """Extract the JWT token from the Authorization header."""
    auth_header = event['headers'].get('authorization')
    if not auth_header:
        logger.warning("Authorization header is missing")
        return None
    return auth_header.split()[1]


def validate_jwt_token(token, logger):
    """Validate and decode the JWT token."""
    cognito_issuer = f'https://cognito-idp.{AWS_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}'
    jwks_url = f'{cognito_issuer}/.well-known/jwks.json'

    try:
        jwks_client = PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token).key
        logger.info("Public key fetched successfully from JWKS URL")

        # Decode the JWT token
        decoded_token = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            issuer=cognito_issuer,
            options={"verify_aud": False}  # Skipping audience verification
        )
        logger.info("JWT token decoded successfully")
        return decoded_token.get('sub')  # Return user_id (sub) from the token

    except jwt.ExpiredSignatureError:
        logger.warning("JWT token has expired")
    except jwt.InvalidTokenError:
        logger.warning("Invalid JWT token")
    except Exception as e:
        logger.error(f"Failed to validate JWT token: {str(e)}")
    return None


def query_user_documents(user_id, logger, cors_headers):
    """Query DynamoDB to get documents for the user."""
    try:
        response = table.query(
            KeyConditionExpression=Key('user_id').eq(user_id)
        )
        logger.info(f"DynamoDB query successful, retrieved {len(response['Items'])} items")
        return generate_response(200, response['Items'], cors_headers, logger)

    except ClientError as e:
        logger.error(f"Failed to query DynamoDB: {e.response['Error']['Message']}")
        return generate_response(400, e.response['Error']['Message'], cors_headers, logger)


def generate_response(status_code, message, cors_headers, logger):
    """Generate an HTTP response with CORS headers and log the response."""
    response = {
        'statusCode': status_code,
        'headers': cors_headers,
        'body': json.dumps(message)
    }
    logger.info(f"Response: {json.dumps(response)}")
    return response