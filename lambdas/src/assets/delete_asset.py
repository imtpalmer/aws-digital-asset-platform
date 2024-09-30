import json
import boto3
import os
from jwt import PyJWKClient
import jwt
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
    Lambda function handler for deleting documents from S3 and DynamoDB.
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
    Handle POST request for deleting a document.
    """
    try:
        # Extract JWT token
        token = extract_jwt_token(event, logger)
        if not token:
            return generate_response(401, 'Authorization header missing', cors_headers, logger)

        # Validate JWT token
        user_id = validate_jwt_token(token, logger, cors_headers)
        if not user_id:
            return generate_response(401, 'Invalid JWT token', cors_headers, logger)

        # Parse request body
        body = json.loads(event.get('body', '{}'))
        document_name = body.get('document_name')

        if not document_name:
            logger.warning("Document name is missing")
            return generate_response(400, 'Document name is missing', cors_headers, logger)

        # Delete document from S3
        delete_document_from_s3(user_id, document_name, logger, cors_headers)

        # Delete document metadata from DynamoDB
        delete_document_from_dynamodb(user_id, document_name, logger, cors_headers)

        return generate_response(200, f'Document {document_name} deleted successfully.', cors_headers)

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


def validate_jwt_token(token, logger, cors_headers):
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


def delete_document_from_s3(user_id, document_name, logger, cors_headers):
    """Delete a document from S3."""
    try:
        s3_client.delete_object(
            Bucket=DIGITAL_ASSETS_BUCKET_NAME,
            Key=f'{user_id}/{document_name}'
        )
        logger.info(f"Document {document_name} deleted from S3 successfully")
    except ClientError as e:
        logger.error(f"Failed to delete document from S3: {e.response['Error']['Message']}")
        raise


def delete_document_from_dynamodb(user_id, document_name, logger, cors_headers):
    """Delete a document record from DynamoDB."""
    try:
        dynamodb_client.delete_item(
            TableName=DYNAMODB_TABLE_NAME,
            Key={
                'user_id': {'S': user_id},
                'document_name': {'S': document_name}
            }
        )
        logger.info(f"Document metadata for {document_name} deleted from DynamoDB successfully")
    except ClientError as e:
        logger.error(f"Failed to delete document metadata from DynamoDB: {e.response['Error']['Message']}")
        raise


def generate_response(status_code, message, cors_headers, logger):
    """Generate an HTTP response with CORS headers and log the response."""
    response = {
        'statusCode': status_code,
        'headers': cors_headers,
        'body': json.dumps(message)
    }
    logger.info(f"Response: {json.dumps(response)}")
    return response