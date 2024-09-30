import json
import jwt
from jwt import PyJWKClient
import boto3
import os
import base64
import datetime
from botocore.exceptions import ClientError
from logging_utils import configure_logging
from cors_utils import get_cors_headers_from_event

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb_client = boto3.client('dynamodb')

# Validate environment variables at cold start
DIGITAL_ASSETS_BUCKET_NAME = os.getenv('DIGITAL_ASSETS_BUCKET_NAME')
DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME')
COGNITO_USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
AWS_REGION = os.getenv('AWS_REGION')

if not all([DIGITAL_ASSETS_BUCKET_NAME, DYNAMODB_TABLE_NAME, COGNITO_USER_POOL_ID, AWS_REGION]):
    raise ValueError("Missing required environment variables")

def lambda_handler(event, context):
    """
    Lambda function handler for processing document uploads and storing metadata.
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
    Handle POST request for document upload and storing metadata.
    """
    try:
        # Extract JWT token from Authorization header
        token = extract_jwt_token(event, logger)
        if not token:
            return generate_response(401, 'Authorization header missing', cors_headers)

        # Decode JWT token
        decoded_token = decode_jwt_token(token, logger)
        if not decoded_token:
            return generate_response(401, 'Invalid or expired token', cors_headers)

        # Extract user information from token
        username = decoded_token.get('cognito:username')
        user_id = decoded_token.get('sub')
        logger.info(f"Username extracted from token: {username}")

        # Parse request body
        body = json.loads(event.get('body', '{}'))
        document = body.get('document')
        document_name = body.get('document_name')

        if not document or not document_name:
            return generate_response(400, 'Document and document_name are required.', cors_headers)

        # Base64 decode the document content
        decoded_document = decode_document(document, logger, cors_headers)
        if not decoded_document:
            return generate_response(400, 'Failed to decode document.', cors_headers)

        # Upload document to S3
        upload_document_to_s3(user_id, document_name, decoded_document, logger, cors_headers)

        # Store metadata in DynamoDB
        store_document_metadata(user_id, document_name, logger, cors_headers)

        return generate_response(200, 'Document uploaded and metadata stored successfully!', cors_headers)

    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return generate_response(500, f'An unexpected error occurred: {str(e)}', cors_headers)


def extract_jwt_token(event, logger):
    """Extract the JWT token from the Authorization header."""
    auth_header = event['headers'].get('authorization')
    if not auth_header:
        logger.warning("Authorization header is missing")
        return None
    return auth_header.split()[1]


def decode_jwt_token(token, logger):
    """Decode the JWT token using the Cognito public keys."""
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
        logger.warning("Token has expired")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Invalid token")
        return None
    except Exception as e:
        logger.error(f"Failed to decode token: {str(e)}")
        return None


def decode_document(document, logger, cors_headers):
    """Base64 decode the document."""
    try:
        decoded_document = base64.b64decode(document)
        logger.info("Document base64 decoded successfully")
        return decoded_document
    except Exception as e:
        logger.error(f"Failed to decode document: {str(e)}")
        return None


def upload_document_to_s3(user_id, document_name, decoded_document, logger, cors_headers):
    """Upload the document to the S3 bucket."""
    try:
        s3_client.put_object(
            Bucket=DIGITAL_ASSETS_BUCKET_NAME,
            Key=f'{user_id}/{document_name}',
            Body=decoded_document
        )
        logger.info("Document uploaded to S3 successfully")
    except ClientError as e:
        logger.error(f"Failed to upload document to S3: {e.response['Error']['Message']}")
        raise


def store_document_metadata(user_id, document_name, logger, cors_headers):
    """Store document metadata in DynamoDB."""
    try:
        dynamodb_client.put_item(
            TableName=DYNAMODB_TABLE_NAME,
            Item={
                'user_id': {'S': user_id},
                'document_name': {'S': document_name},
                'upload_date': {'S': str(datetime.datetime.now())}
            }
        )
        logger.info("Metadata for document stored in DynamoDB successfully")
    except ClientError as e:
        logger.error(f"Failed to store metadata in DynamoDB: {e.response['Error']['Message']}")
        raise


def generate_response(status_code, message, cors_headers):
    """Generate an HTTP response with CORS headers."""
    return {
        'statusCode': status_code,
        'headers': cors_headers,
        'body': json.dumps(message)
    }