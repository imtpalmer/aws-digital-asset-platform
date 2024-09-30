
import json
import jwt
from jwt import PyJWKClient
import boto3
import os
from botocore.exceptions import ClientError
from logging_utils import configure_logging
from cors_utils import get_cors_headers_from_event

# Initialize AWS clients
s3_client = boto3.client('s3')

# Validate environment variables at cold start
DIGITAL_ASSETS_BUCKET_NAME = os.getenv('DIGITAL_ASSETS_BUCKET_NAME')
COGNITO_USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
AWS_REGION = os.getenv('AWS_REGION')

if not all([DIGITAL_ASSETS_BUCKET_NAME, COGNITO_USER_POOL_ID, AWS_REGION]):
    raise ValueError("Missing required environment variables")


def lambda_handler(event, context):
    """
    Lambda function handler for fetching documents.
    """
    logger = configure_logging()
    logger.info("Lambda function started")
    logger.debug("Received event: %s", json.dumps(event))

    # Get CORS headers
    cors_headers = get_cors_headers_from_event(event, logger)

    # Determine the HTTP method
    http_method = event.get('routeKey', '').split()[0] or event.get('httpMethod')

    if http_method == 'OPTIONS':
        return generate_response(200, 'CORS preflight', cors_headers)

    elif http_method == 'POST':
        return handle_post_request(event, logger, cors_headers)

    return generate_response(405, f'Method {http_method} not allowed', cors_headers)


def handle_post_request(event, logger, cors_headers):
    """
    Handle GET request for fetching a document.
    """
    try:
        # Extract JWT token from Authorization header
        token = extract_jwt_token(event, logger)
        if not token:
            return generate_response(401, 'Authorization header missing', cors_headers)

        # Decode JWT token
        decoded_token = decode_jwt_token(token, logger)
        if not decoded_token:
            return generate_response(401, 'Invalid JWT token', cors_headers)

        # Fetch user ID from the decoded token
        user_id = decoded_token.get('sub')
        if not user_id:
            logger.error("User ID not found in JWT token")
            return generate_response(401, 'Unauthorized', cors_headers)

        # Extract document name from the event path or query string
        document_name = event['queryStringParameters'].get('documentName')
        if not document_name:
            return generate_response(400, 'Document name missing', cors_headers)

        # Fetch the document from S3
        document = fetch_document_from_s3(user_id, document_name, logger)
        if document is None:
            return generate_response(404, 'Document not found', cors_headers)

        return generate_response(200, document.decode('utf-8'), cors_headers)

    except Exception as e:
        logger.error(f"Error occurred while handling GET request: {str(e)}")
        return generate_response(500, 'Internal server error', cors_headers)


def extract_jwt_token(event, logger):
    """
    Extract JWT token from the Authorization header.
    """
    auth_header = event['headers'].get('authorization')
    if not auth_header:
        logger.warning("Authorization header is missing")
        return None
    return auth_header.split()[1]


def decode_jwt_token(token, logger):
    """
    Decode the JWT token using Cognito public keys.
    """
    try:
        cognito_issuer = f'https://cognito-idp.{AWS_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}'
        jwks_url = f'{cognito_issuer}/.well-known/jwks.json'

        jwks_client = PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token).key

        decoded_token = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            issuer=cognito_issuer,
            options={"verify_aud": False}  # Skipping audience verification
        )
        logger.info("JWT token decoded successfully")
        return decoded_token

    except jwt.ExpiredSignatureError:
        logger.error("JWT token has expired")
        return None
    except jwt.InvalidTokenError:
        logger.error("Invalid JWT token")
        return None
    except Exception as e:
        logger.error(f"Failed to decode JWT token: {str(e)}")
        return None


def fetch_document_from_s3(user_id, document_name, logger):
    """
    Fetch the document from the S3 bucket.
    """
    try:
        response = s3_client.get_object(
            Bucket=DIGITAL_ASSETS_BUCKET_NAME,
            Key=f'{user_id}/{document_name}'
        )
        logger.info(f"Document {document_name} fetched from S3 successfully")
        return response['Body'].read()

    except ClientError as e:
        logger.error(f"Failed to fetch document from S3: {e.response['Error']['Message']}")
        return None


def generate_response(status_code, message, cors_headers):
    """
    Helper function to generate HTTP responses with CORS headers.
    """
    return {
        'statusCode': status_code,
        'headers': cors_headers,
        'body': json.dumps(message)
    }
