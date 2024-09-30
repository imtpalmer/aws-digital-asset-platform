import json
import os
import boto3
import jwt
from botocore.exceptions import ClientError
from jwt import PyJWKClient, PyJWKClientError
from logging_utils import configure_logging
from cors_utils import get_cors_headers_from_event

# Initialize S3 client at module level
s3_client = boto3.client('s3')

# Environment variables validation
REQUIRED_ENV_VARS = ['DIGITAL_ASSETS_BUCKET_NAME', 'COGNITO_USER_POOL_ID', 'AWS_REGION']
MISSING_ENV_VARS = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]

if MISSING_ENV_VARS:
    raise ValueError(f"Missing required environment variables: {', '.join(MISSING_ENV_VARS)}")

DIGITAL_ASSETS_BUCKET_NAME = os.getenv('DIGITAL_ASSETS_BUCKET_NAME')
COGNITO_USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
AWS_REGION = os.getenv('AWS_REGION')

# Cache JWKS client globally
_jwks_client = None

def get_jwks_client(jwks_url, logger):
    """Fetch JWKS client, using cached instance for efficiency."""
    global _jwks_client
    if _jwks_client is None:
        try:
            _jwks_client = PyJWKClient(jwks_url)
            logger.info("JWKS client initialized")
        except PyJWKClientError as e:
            logger.error(f"Error initializing JWKS client: {e}")
            raise
    return _jwks_client

def lambda_handler(event, context):
    """Main Lambda handler."""
    logger = configure_logging()
    logger.info("Lambda function started")
    logger.debug(f"Received event: {json.dumps(event)}")

    cors_headers = get_cors_headers_from_event(event, logger)
    http_method = extract_http_method(event)

    if http_method == 'OPTIONS':
        return generate_response(200, 'CORS preflight', cors_headers, logger)
    
    if http_method == 'POST':
        return handle_post_request(event, logger, cors_headers)

    return generate_response(405, f'Method {http_method} not allowed', cors_headers, logger)

def extract_http_method(event):
    """Extract HTTP method from event."""
    return event.get('routeKey', '').split(' ')[0] if 'routeKey' in event else event.get('httpMethod')

def handle_post_request(event, logger, cors_headers):
    """Handle POST request logic."""
    try:
        auth_token = get_authorization_token(event, logger)
        if not auth_token or not validate_jwt_token(auth_token, logger):
            return generate_response(401, 'Unauthorized', cors_headers, logger)

        body = extract_body(event, logger)
        filename = body.get('filename')
        if not filename:
            return generate_response(400, 'Filename is required', cors_headers, logger)

        upload_id = initiate_multipart_upload(filename, logger)
        return generate_response(200, {'uploadId': upload_id}, cors_headers, logger)

    except ClientError as e:
        logger.error(f"ClientError: {e}")
        return generate_response(500, f'Error starting multipart upload: {e}', cors_headers, logger)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding error: {e}")
        return generate_response(400, 'Invalid JSON format', cors_headers, logger)

    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        return generate_response(500, 'Internal server error', cors_headers, logger)

def extract_body(event, logger):
    """Extract and parse the request body from the event."""
    try:
        body = json.loads(event.get('body', '{}'))
        logger.info(f"Extracted body: {body}")
        return body
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format: {e}")
        raise

def initiate_multipart_upload(filename, logger):
    """Initiate S3 multipart upload."""
    response = s3_client.create_multipart_upload(Bucket=DIGITAL_ASSETS_BUCKET_NAME, Key=filename)
    upload_id = response['UploadId']
    logger.info(f"Multipart upload initiated for file: {filename}, uploadId: {upload_id}")
    return upload_id

def get_authorization_token(event, logger):
    """Extract Bearer token from Authorization header."""
    auth_header = event.get('headers', {}).get('Authorization') or event.get('headers', {}).get('authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    logger.warning("Malformed Authorization header")
    return None

def validate_jwt_token(token, logger):
    """Validate the JWT token with Cognito."""
    cognito_issuer = f'https://cognito-idp.{AWS_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}'
    jwks_url = f'{cognito_issuer}/.well-known/jwks.json'

    try:
        jwks_client = get_jwks_client(jwks_url, logger)
        signing_key = jwks_client.get_signing_key_from_jwt(token).key

        jwt.decode(token, signing_key, algorithms=["RS256"], issuer=cognito_issuer, options={"verify_aud": False})
        logger.info("JWT token decoded and validated successfully")
        return True

    except jwt.ExpiredSignatureError:
        logger.error("JWT token has expired")
        return False
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid JWT token: {e}")
        return False

def generate_response(status_code, message, cors_headers, logger=None):
    """Generate an HTTP response."""
    response = {
        'statusCode': status_code,
        'headers': cors_headers,
        'body': json.dumps(message)
    }
    if logger:
        logger.info(f"Response generated: {response}")
    return response