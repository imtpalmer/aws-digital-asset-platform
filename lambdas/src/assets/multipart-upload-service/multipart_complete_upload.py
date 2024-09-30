import json
import os
import boto3
import jwt
from botocore.exceptions import ClientError
from jwt import PyJWKClient, PyJWKClientError
from logging_utils import configure_logging
from cors_utils import get_cors_headers_from_event

# Initialize S3 client
s3_client = boto3.client('s3')

# Validate environment variables at cold start
DIGITAL_ASSETS_BUCKET_NAME = os.getenv('DIGITAL_ASSETS_BUCKET_NAME')
COGNITO_USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
AWS_REGION = os.getenv('AWS_REGION')

if not all([DIGITAL_ASSETS_BUCKET_NAME, COGNITO_USER_POOL_ID, AWS_REGION]):
    raise ValueError("Missing required environment variables")

_jwks_client = None  # Cache JWKS client

def get_jwks_client(jwks_url, logger):
    global _jwks_client
    if _jwks_client is None:
        try:
            _jwks_client = PyJWKClient(jwks_url)
            logger.info("JWKS client initialized")
        except PyJWKClientError as e:
            logger.error("Error initializing JWKS client: %s", str(e))
            raise
    return _jwks_client

def lambda_handler(event, context):
    """
    Lambda function handler for completing a multipart upload.
    """
    logger = configure_logging()
    logger.info("Lambda function started")
    logger.info(f"Received event: {json.dumps(event)}")

    # Get CORS headers
    cors_headers = get_cors_headers_from_event(event, logger)

    # Determine the HTTP method
    http_method = event.get('routeKey', '').split(' ')[0] if 'routeKey' in event else event.get('httpMethod')

    if http_method == 'OPTIONS':
        return generate_response(200, 'CORS preflight', cors_headers)

    if http_method == 'POST':
        return handle_post_request(event, logger, cors_headers)

    return generate_response(405, f'Method {http_method} not allowed', cors_headers)

def handle_post_request(event, logger, cors_headers):
    """
    Handle POST requests for completing a multipart upload.
    """
    try:
         # Validate JWT from Authorization header
        auth_token = get_authorization_token(event, logger)
        if not auth_token or not validate_jwt_token(auth_token, logger):
            return generate_response(401, 'Unauthorized', cors_headers)

        # Parse the request body
        body = json.loads(event.get('body', '{}'))
        upload_id = body.get('uploadId')
        filename = body.get('filename')
        parts = body.get('parts')

        # Validate required fields
        if not all([upload_id, filename, parts]):
            return generate_response(400, 'upload_id, filename, and parts are required', cors_headers)

        # Complete the multipart upload
        s3_client.complete_multipart_upload(
            Bucket=DIGITAL_ASSETS_BUCKET_NAME,
            Key=filename,
            UploadId=upload_id,
            MultipartUpload={'Parts': parts}
        )

        logger.info(f"Multipart upload for file {filename} completed successfully.")
        return generate_response(200, 'Multipart upload completed successfully', cors_headers)

    except ClientError as e:
        logger.error("ClientError: %s", e)
        return generate_response(500, f'Error completing multipart upload: {e}', cors_headers)

    except Exception as e:
        logger.error("Unhandled exception: %s", str(e))
        return generate_response(500, 'Internal server error', cors_headers)

def get_authorization_token(event, logger):
    """Extract the JWT token from the Authorization header."""
    authorization = event.get('headers', {}).get('Authorization') or event.get('headers', {}).get('authorization')
    if authorization and authorization.startswith('Bearer '):
        return authorization.split(' ')[1]
    logger.warning("Malformed Authorization header")
    return None

def validate_jwt_token(token, logger):
    """Validate and decode the JWT token."""
    cognito_issuer = f'https://cognito-idp.{AWS_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}'
    jwks_url = f'{cognito_issuer}/.well-known/jwks.json'

    try:
        jwks_client = get_jwks_client(jwks_url, logger)
        signing_key = jwks_client.get_signing_key_from_jwt(token).key

        jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            issuer=cognito_issuer,
            options={"verify_aud": False}
        )
        logger.info("JWT token decoded and validated successfully")
        return True

    except Exception as e:
        logger.error(f"JWT validation failed: {str(e)}")
        return False

def generate_response(status_code, message, cors_headers):
    """
    Helper function to generate HTTP responses with CORS headers.
    """
    return {
        'statusCode': status_code,
        'headers': cors_headers,
        'body': json.dumps(message)
    }