from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, PlainSerializer, ConfigDict

custom_datetime = Annotated[
    datetime,
    PlainSerializer(
        lambda _datetime: _datetime.strftime("%d/%m/%Y, %H:%M:%S"), return_type=str
    ),
]


class IdResponse(BaseModel):
    id: Annotated[int, Field(description="ID")]


class OutMixin(IdResponse):
    created_at: Annotated[custom_datetime, Field(description="Создано в")]

    model_config = ConfigDict(from_attributes=True)
