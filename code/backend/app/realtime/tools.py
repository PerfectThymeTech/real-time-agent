from agents import RunContextWrapper, function_tool
from app.calls.client import ACS_CLIENT
from app.logs import setup_logging
from app.models.realtime import UserSessionContext

logger = setup_logging(__name__)


def tool_error_handling(
    ctx: RunContextWrapper[UserSessionContext], error: Exception
) -> str:
    """Helper function to handle errors in function tools.

    :param ctx: The function tool execution context, which includes the user session context.
    :type ctx: RunContextWrapper[UserSessionContext]
    :param error: The exception that was raised.
    :type error: Exception
    :return: A user-friendly error message.
    :rtype: str
    """
    logger.error(
        f"Error in function tool: {str(error)}",
        extra={
            "code": "FUNCTION_TOOL_ERROR",
            "error_message": str(error),
        },
    )
    return "Sorry, I am having trouble processing your request."


@function_tool(failure_error_function=tool_error_handling)
async def get_caller_phone_number(ctx: RunContextWrapper[UserSessionContext]) -> str:
    """Function tool to get the caller's phone number from the call connection context.

    :return: The caller's phone number as a string.
    :rtype: str
    """
    logger.info(
        "Function tool 'get_caller_phone_number' called",
        extra={"code": "FUNCTION_TOOL_GET_CALLER_PHONE_NUMBER_CALLED"},
    )

    # Get call properties
    call_connection_client = ACS_CLIENT.get_call_connection(
        call_connection_id=ctx.context.call_connection_id
    )
    call_properties = await call_connection_client.get_call_properties()

    # Get the caller's phone number from the call properties
    caller_phone_number = call_properties.source_caller_id_number.properties.get(
        "value", "unknown"
    )
    logger.info(
        f"Retrieved caller phone number: {caller_phone_number}",
        extra={
            "code": "FUNCTION_TOOL_GET_CALLER_PHONE_NUMBER_RETRIEVED",
            "caller_phone_number": caller_phone_number,
        },
    )

    return caller_phone_number


@function_tool(failure_error_function=tool_error_handling)
async def hang_up_call(ctx: RunContextWrapper[UserSessionContext]) -> None:
    """Function tool to hang up the call."""
    logger.info(
        "Function tool 'hang_up_call' called",
        extra={"code": "FUNCTION_TOOL_HANG_UP_CALL_CALLED"},
    )

    # Hang up the call using the ACS client
    call_connection_client = ACS_CLIENT.get_call_connection(
        call_connection_id=ctx.context.call_connection_id
    )
    await call_connection_client.hang_up(is_for_everyone=True)
    logger.info(
        "Call hung up successfully",
        extra={"code": "FUNCTION_TOOL_HANG_UP_CALL_SUCCESS"},
    )
