import json

# CORS headers (update with allowed origins as needed)
ALLOWED_ORIGINS = ['*']  # Update this to restrict to specific domains
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',  # Default to allow all origins
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, Content-Security-Policy, ETag, X-Amz-Date, X-Api-Key, x-amz-security-token',
    'Access-Control-Allow-Methods': 'GET, PUT, POST, OPTIONS',
    'Access-Control-Expose-Headers': 'ETag, Content-Security-Policy, x-amz-security-token'
}

def get_cors_headers_from_event(event, logger):
    """
    Extracts the origin from the event's request headers and returns the appropriate CORS headers.
    Adds basic error handling for missing or malformed event data.

    Args:
        event (dict): The Lambda event object containing request headers.

    Returns:
        dict: A dictionary containing the CORS headers based on the request's origin.
    """
    try:
        # Extract the origin from the request headers
        # origin = event.get('headers', {}).get('origin', '*')
        # logger.info("found origin: %s", origin)

        # Create a copy of the default CORS headers
        headers = CORS_HEADERS.copy()

        # Set the Access-Control-Allow-Origin header based on the request origin
        # if origin in ALLOWED_ORIGINS or '*' in ALLOWED_ORIGINS:
            #headers['Access-Control-Allow-Origin'] = origin

        logger.info("Generated CORS header: %s",  json.dumps(headers))
        return headers

    except Exception as e:
        logger.info("Error generating CORS headers: %s", str(e))
        # Return default headers as a fallback in case of error
        return CORS_HEADERS.copy()