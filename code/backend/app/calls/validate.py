import jwt
from app.logs import setup_logging

logger = setup_logging(__name__)


def validate_callback_authorization(
    authorization_header: str, acs_resource_id: str
) -> bool:
    """
    Validates the authorization header of a callback event to ensure it is coming from a trusted source.
    This is a placeholder function and should be implemented with proper validation logic, such as checking a shared secret or validating a JWT token.

    :param authorization_header: The value of the authorization header from the incoming request.
    :type authorization_header: str
    :param acs_resource_id: The Azure Communication Services resource ID.
    :type acs_resource_id: str
    :return: True if the authorization is valid, False otherwise.
    :rtype: bool
    """
    logger.info(
        "Validating callback authorization",
        extra={"code": "VALIDATE_AUTHORIZATION_CALLBACK_START"},
    )
    # Create a PyJWKClient to fetch the signing keys from Azure Communication Services
    jwks_client = jwt.PyJWKClient(
        "https://acscallautomation.communication.azure.com/calling/keys"
    )

    # Get the token from the authorization header (assuming it is in the format "Bearer <token>")
    if not authorization_header.startswith("Bearer "):
        return False
    token = authorization_header.split(" ")[1]

    try:
        # Decode and validate the JWT token
        jwt.decode(
            token,
            jwks_client.get_signing_key_from_jwt(token).key,
            algorithms=["RS256"],
            issuer="https://acscallautomation.communication.azure.com",
            audience=acs_resource_id,
        )

    except jwt.PyJWTError as e:
        logger.warning(
            f"JWT validation failed: {e}",
            exc_info=True,
            extra={"code": "VALIDATE_AUTHORIZATION_CALLBACK_FAILED"},
        )
        return False

    except Exception as e:
        logger.error(
            f"Unexpected error during JWT validation: {e}",
            exc_info=True,
            extra={"code": "VALIDATE_AUTHORIZATION_CALLBACK_FAILED"},
        )
        return False

    logger.info(
        "Callback authorization validated successfully",
        extra={"code": "VALIDATE_AUTHORIZATION_CALLBACK_SUCCESS"},
    )
    return True


def validate_incoming_call_authorization(
    token_query: str, acs_token_query: str
) -> bool:
    """
    Validates the token query parameter of an incoming call event to ensure it matches the expected value.

    :param token_query: The value of the token query parameter from the incoming request.
    :type token_query: str
    :param acs_token_query: The expected token query value from settings.
    :type acs_token_query: str
    :return: True if the token query is valid, False otherwise.
    :rtype: bool
    """
    logger.info(
        "Validating incoming call authorization",
        extra={"code": "VALIDATE_AUTHORIZATION_INCOMING_CALL_START"},
    )

    if token_query != acs_token_query:
        logger.warning(
            "Incoming call authorization failed: Invalid token query",
            extra={"code": "VALIDATE_AUTHORIZATION_INCOMING_CALL_FAILED"},
        )
        return False

    logger.info(
        "Incoming call authorization validated successfully",
        extra={"code": "VALIDATE_AUTHORIZATION_INCOMING_CALL_SUCCESS"},
    )
    return True


def validate_websocket_authorization(
    authorization_header: str, acs_resource_id: str
) -> bool:
    """
    Validates the authorization header of a WebSocket connection to ensure it is coming from a trusted source.
    This is a placeholder function and should be implemented with proper validation logic, such as checking a shared secret or validating a JWT token.

    :param authorization_header: The value of the authorization header from the incoming WebSocket connection request.
    :type authorization_header: str
    :param acs_resource_id: The Azure Communication Services resource ID.
    :type acs_resource_id: str
    :return: True if the authorization is valid, False otherwise.
    :rtype: bool
    """
    logger.info(
        "Validating WebSocket authorization",
        extra={"code": "VALIDATE_AUTHORIZATION_WEBSOCKET_START"},
    )
    # Create a PyJWKClient to fetch the signing keys from Azure Communication Services
    jwks_client = jwt.PyJWKClient(
        "https://acscallautomation.communication.azure.com/calling/keys"
    )

    # Get the token from the authorization header (assuming it is in the format "Bearer <token>")
    if not authorization_header.startswith("Bearer "):
        return False
    token = authorization_header.split(" ")[1]

    try:
        # Decode and validate the JWT token
        jwt.decode(
            token,
            jwks_client.get_signing_key_from_jwt(token).key,
            algorithms=["RS256"],
            issuer="https://acscallautomation.communication.azure.com",
            audience=acs_resource_id,
        )

    except jwt.PyJWTError as e:
        logger.warning(
            f"JWT validation failed: {e}",
            exc_info=True,
            extra={"code": "VALIDATE_AUTHORIZATION_WEBSOCKET_FAILED"},
        )
        return False

    except Exception as e:
        logger.error(
            f"Unexpected error during JWT validation: {e}",
            exc_info=True,
            extra={"code": "VALIDATE_AUTHORIZATION_WEBSOCKET_FAILED"},
        )
        return False

    logger.info(
        "WebSocket authorization validated successfully",
        extra={"code": "VALIDATE_AUTHORIZATION_WEBSOCKET_SUCCESS"},
    )
    return True
