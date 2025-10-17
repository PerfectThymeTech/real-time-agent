from pydantic import BaseModel
from pydantic.alias_generators import to_camel


class ValidationResponse(BaseModel):
    validation_response: str

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
