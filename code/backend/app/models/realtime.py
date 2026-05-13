from pydantic import BaseModel


class UserSessionContext(BaseModel):
    call_connection_id: str
