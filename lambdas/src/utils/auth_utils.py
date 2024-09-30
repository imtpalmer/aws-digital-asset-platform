import logging
import jwt
from jwt import PyJWKClient

logger = logging.getLogger()

def extract_and_verify_token(event, region, user_pool_id):
    """
    Extracts and verifies the JWT token from the Authorization header in the event, 
    fetches the signing key from the JWKS URL, and decodes the token.
    
    Args:
        event (dict): The event containing the request headers.
        region (str): The AWS region of the Cognito User Pool.
        user_pool_id (str): The Cognito User Pool ID.
        
    Returns:
        dict: A response containing the decoded token or an error message.
    """
    # Extract the JWT token from the Authorization header
    auth_header = event['headers'].get('authorization')
    if not auth_header:
        logger.warning("Authorization header is missing")
        return generate_response(401, 'Authorization header missing')

    try:
        token = auth_header.split()[1]
        logger.info("Authorization token extracted successfully")
    except IndexError:
        logger.error("Invalid Authorization header format")
        return generate_response(400, 'Invalid Authorization header format')

    # Define Cognito User Pool information
    cognito_issuer = f'https://cognito-idp.{region}.amazonaws.com/{user_pool_id}'
    jwks_url = f'{cognito_issuer}/.well-known/jwks.json'

    # Fetch the public key from the JWKS URL
    try:
        jwks_client = PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token).key
        logger.info("Public key fetched successfully from JWKS URL")
    except Exception as e:
        logger.error("Failed to fetch the public key: %s", str(e))
        return generate_response(500, f'Failed to fetch the public key: {str(e)}')

    # Decode the JWT token
    try:
        decoded_token = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            issuer=cognito_issuer,
            options={"verify_aud": False}  # Skipping audience verification
        )
        logger.info("JWT token decoded successfully")

        # Extract the username and user_id from the decoded token
        username = decoded_token.get('cognito:username')
        user_id = decoded_token.get('sub')

        return {
            "statusCode": 200,
            "body": {
                "message": "Token decoded successfully",
                "username": username,
                "user_id": user_id
            }
        }
    except jwt.ExpiredSignatureError:
        logger.error("Token has expired")
        return generate_response(401, "Token has expired")
    except jwt.InvalidTokenError as e:
        logger.error("Invalid token: %s", str(e))
        return generate_response(401, f'Invalid token: {str(e)}')

def generate_response(status_code, message):
    """Helper function to generate a standard HTTP response."""
    return {
        "statusCode": status_code,
        "body": {
            "message": message
        }
    }