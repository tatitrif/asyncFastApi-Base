from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, ConfigDict


class IdResponse(BaseModel):
    id: Annotated[int, Field(description="ID")]


class OutMixin(IdResponse):
    created_at: Annotated[datetime, Field(description="CreatedAt")]

    model_config = ConfigDict(from_attributes=True)
