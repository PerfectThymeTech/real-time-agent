from agents import RunContextWrapper, function_tool
from app.logs import setup_logging
from app.models.realtime import UserSessionContext

logger = setup_logging(__name__)


@function_tool()
async def get_caller_phone_number(ctx: RunContextWrapper[UserSessionContext]) -> str:
    """ "Function tool to get the caller's phone number from the call connection context.

    :return: The caller's phone number as a string.
    :rtype: str
    """
    logger.info(
        "Function tool 'get_caller_phone_number' called",
        extra={"code": "FUNCTION_TOOL_GET_CALLER_PHONE_NUMBER_CALLED"},
    )

    # Get call properties
    call_properties = ctx.context.acs_client.get_call_connection(
        call_connection_id=ctx.context.call_connection_id
    ).get_call_properties()

    # Get the caller's phone number from the call properties
    caller_phone_number = call_properties.source_caller_id_number.properties.get(
        "value", "unknown"
    )

    return caller_phone_number


@function_tool()
async def hang_up_call(ctx: RunContextWrapper[UserSessionContext]) -> None:
    """Function tool to hang up the call."""
    logger.info(
        "Function tool 'hang_up_call' called",
        extra={"code": "FUNCTION_TOOL_HANG_UP_CALL_CALLED"},
    )

    # Hang up the call using the ACS client
    ctx.context.acs_client.get_call_connection(
        call_connection_id=ctx.context.call_connection_id
    ).hang_up(is_for_everyone=True)
