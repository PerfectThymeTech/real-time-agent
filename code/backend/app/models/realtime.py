from azure.communication.callautomation import CallAutomationClient
from pydantic import BaseModel, ConfigDict


class UserSessionContext(BaseModel):
    acs_client: CallAutomationClient
    call_connection_id: str

    model_config = ConfigDict(arbitrary_types_allowed=True)
