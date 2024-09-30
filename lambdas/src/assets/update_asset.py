import json
import jwt
from jwt import PyJWKClient
import boto3
import os
import base64
from botocore.exceptions import ClientError
import datetime
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
    Lambda function handler for updating documents in S3 and DynamoDB.
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
    Handle POST request for updating a document.
    """
    try:
        # Extract JWT token
        token = extract_jwt_token(event, logger)
        if not token:
            return generate_response(401, 'Authorization header missing', cors_headers)

        # Validate JWT token
        user_id = validate_jwt_token(token, logger, cors_headers)
        if not user_id:
            return generate_response(401, 'Invalid JWT token', cors_headers)

        # Parse request body
        body = json.loads(event.get('body', '{}'))
        document_name = body.get('document_name')
        encoded_document = body.get('document')

        if not document_name or not encoded_document:
            logger.warning("Document name or content missing in request")
            return generate_response(400, 'Document name or content missing', cors_headers)

        # Base64 decode document
        decoded_document = base64.b64decode(encoded_document)
        logger.info("Document decoded successfully")

        # Upload document to S3
        upload_document_to_s3(user_id, document_name, decoded_document, logger, cors_headers)

        # Update document metadata in DynamoDB
        update_document_metadata_in_dynamodb(user_id, document_name, logger, cors_headers)

        return generate_response(200, 'Document updated successfully!', cors_headers)

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


def upload_document_to_s3(user_id, document_name, decoded_document, logger, cors_headers):
    """Upload the document to S3."""
    try:
        s3_client.put_object(
            Bucket=DIGITAL_ASSETS_BUCKET_NAME,
            Key=f'{user_id}/{document_name}',
            Body=decoded_document
        )
        logger.info(f"Document {document_name} updated in S3 successfully")
    except ClientError as e:
        logger.error(f"Failed to update document in S3: {e.response['Error']['Message']}")
        raise


def update_document_metadata_in_dynamodb(user_id, document_name, logger, cors_headers):
    """Update document metadata in DynamoDB."""
    try:
        dynamodb_client.update_item(
            TableName=DYNAMODB_TABLE_NAME,
            Key={
                'user_id': {'S': user_id},
                'document_name': {'S': document_name}
            },
            UpdateExpression='SET upload_date = :val1',
            ExpressionAttributeValues={
                ':val1': {'S': str(datetime.datetime.now())}
            }
        )
        logger.info(f"Document metadata for {document_name} updated in DynamoDB successfully")
    except ClientError as e:
        logger.error(f"Failed to update document metadata in DynamoDB: {e.response['Error']['Message']}")
        raise


def generate_response(status_code, message, cors_headers):
    """Generate an HTTP response with CORS headers."""
    return {
        'statusCode': status_code,
        'headers': cors_headers,
        'body': json.dumps(message)
    }