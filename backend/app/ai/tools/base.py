from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession


class ToolContext(BaseModel):
    """Runtime context injected into tools at execution time."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    db: AsyncSession
    owner_id: UUID


class ToolError(BaseModel):
    code: str
    message: str


class BaseToolOutput(BaseModel):
    success: bool
    message: str = ""
    errors: list[ToolError] = Field(default_factory=list)

    def to_json(self) -> str:
        return self.model_dump_json()
