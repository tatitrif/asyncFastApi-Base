from pydantic import BaseModel, Field


class PagedParamsSchema(BaseModel):
    limit: int | None = Field(
        10,
        ge=1,
        description="Page size",
        alias="page[size]",
    )
    offset: int | None = Field(
        1,
        ge=1,
        description="Page number",
        alias="page[number]",
    )


class PageInfoResponse(BaseModel):
    total: int | None = Field(
        default=0,
        title="Total Count",
        description="How many entities exist in the database for filters (excluding limit/offset).",
    )
    page: int | None = Field(default=0, title="Offset")
    size: int | None = Field(default=10, title="Limit")
    first: int | None
    last: int | None
    previous: int | None
    next: int | None


class PageResponse(BaseModel):
    page_info: PageInfoResponse
    page_data: list
