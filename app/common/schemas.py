from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints
from pydantic.alias_generators import to_camel


class APIModel(BaseModel):
    """Base for every request/response schema: camelCase JSON, snake_case Python."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


Name = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=2, max_length=100)
]

Password = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=8, max_length=128)
]
