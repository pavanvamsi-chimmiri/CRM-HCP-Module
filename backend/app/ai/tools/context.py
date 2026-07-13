from uuid import UUID

from langchain_core.runnables import RunnableConfig
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.tools.base import ToolContext


def get_tool_context(config: RunnableConfig) -> ToolContext:
    """Build a ToolContext from LangGraph runnable configuration."""
    configurable = config.get("configurable", {})
    db: AsyncSession | None = configurable.get("db")
    owner_id_raw = configurable.get("owner_id")

    if db is None:
        raise ValueError("Database session not available in graph configuration")
    if not owner_id_raw:
        raise ValueError("owner_id not available in graph configuration")

    return ToolContext(db=db, owner_id=UUID(str(owner_id_raw)))
