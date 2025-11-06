from pydantic import BaseModel
from pydantic.alias_generators import to_camel


class ValidationResponse(BaseModel):
    validation_response: str

    class Config:
        alias_generator = to_camel
        validate_by_name = True
