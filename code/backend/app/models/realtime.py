from pydantic import BaseModel
from azure.communication.callautomation import CallAutomationClient


class UserSessionContext(BaseModel):
    acs_client: CallAutomationClient
    call_connection_id: str
