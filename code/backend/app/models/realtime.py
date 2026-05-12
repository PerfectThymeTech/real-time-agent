from azure.communication.callautomation import CallAutomationClient
from pydantic import BaseModel


class UserSessionContext(BaseModel):
    acs_client: CallAutomationClient
    call_connection_id: str
