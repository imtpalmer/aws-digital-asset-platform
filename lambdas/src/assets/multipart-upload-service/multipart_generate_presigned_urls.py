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
REQUIRED_ENV_VARS = ['DIGITAL_ASSETS_BUCKET_NAME', 'COGNITO_USER_POOL_ID', 'AWS_REGION']
MISSING_ENV_VARS = [var for var in REQUIRED_ENV_VARS if os.getenv(var) is None]

if MISSING_ENV_VARS:
    raise ValueError(f"Missing required environment variables: {', '.join(MISSING_ENV_VARS)}")

DIGITAL_ASSETS_BUCKET_NAME = os.getenv('DIGITAL_ASSETS_BUCKET_NAME')
COGNITO_USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
AWS_REGION = os.getenv('AWS_REGION')

# Cache JWKS client globally to avoid re-initializing
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
    logger.info(f"Received event: {json.dumps(event)}")

    cors_headers = get_cors_headers_from_event(event, logger)
    http_method = extract_http_method(event)

    if http_method == 'OPTIONS':
        return generate_response(200, 'CORS preflight', cors_headers, logger)
    if http_method == 'POST':
        return handle_post_request(event, logger, cors_headers)

    return generate_response(405, f'Method {http_method} not allowed', cors_headers)

def extract_http_method(event):
    """Extract HTTP method from event."""
    route_key = event.get('routeKey', '')
    if route_key:
        return route_key.split(' ')[0]
    return event.get('httpMethod')

def handle_post_request(event, logger, cors_headers):
    """Handle POST request logic for generating presigned URLs."""
    try:
        auth_token = get_authorization_token(event, logger)
        if not auth_token or not validate_jwt_token(auth_token, logger):
            return generate_response(401, 'Unauthorized', cors_headers)

        body = json.loads(event.get('body', '{}'))
        uploadId, filename, parts = extract_body_fields(body, logger)
        if not all([uploadId, filename, parts]):
            return generate_response(400, 'uploadId, filename, and parts are required', cors_headers, logger)

        presigned_urls = generate_presigned_urls(uploadId, filename, parts, logger)
        return generate_response(200, {'partUrls': presigned_urls}, cors_headers, logger)

    except ClientError as e:
        logger.error(f"ClientError: {e}")
        return generate_response(500, f'Error generating presigned URLs: {e}', cors_headers)

    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        return generate_response(500, 'Internal server error', cors_headers)

def extract_body_fields(body, logger):
    """Extract fields from the request body."""
    uploadId = body.get('uploadId')
    filename = body.get('filename')
    parts = body.get('parts')
    logger.info(f"Extracted body fields - uploadId: {uploadId}, filename: {filename}, parts: {parts}")
    return uploadId, filename, parts

def generate_presigned_urls(uploadId, filename, parts, logger):
    """Generate presigned URLs for each part."""
    presigned_urls = []
    for part_number in range(1, parts + 1):
        try:
            url = s3_client.generate_presigned_url(
                ClientMethod='upload_part',
                Params={
                    'Bucket': DIGITAL_ASSETS_BUCKET_NAME,
                    'Key': filename,
                    'UploadId': uploadId,
                    'PartNumber': part_number
                },
                ExpiresIn=3600 # 1 hour in seconds 
            )
            logger.info(f"Presigned URL for part {part_number}: {url}")
            presigned_urls.append(url)
        except ClientError as e:
            logger.error(f"Error generating URL for part {part_number}: {e}")
            raise e
    logger.info(f"Presigned URLs generated for file: {filename}")
    return presigned_urls

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

    except jwt.ExpiredSignatureError:
        logger.error("JWT token has expired")
        return False
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid JWT token: {e}")
        return False

def generate_response(status_code, message, cors_headers, logger=None):
    """Generate a HTTP response."""
    response = {
        'statusCode': status_code,
        'headers': cors_headers,
        'body': json.dumps(message)
    }

    if logger:
        logger.info(f"Generating response: {response}")
    
    return response