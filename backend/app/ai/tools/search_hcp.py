from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

from app.ai.tools.base import BaseToolOutput, ToolContext, ToolError
from app.core.logging import get_logger
from app.crud import hcp as hcp_crud
from app.crud import interaction as interaction_crud
from app.models import InteractionType, Sentiment

logger = get_logger(__name__)


class InteractionSearchResult(BaseModel):
    interaction_id: UUID
    hcp_id: UUID
    doctor_name: str
    interaction_type: InteractionType
    interaction_date: date
    topics: list[str] = Field(default_factory=list)
    sentiment: Sentiment | None = None
    outcome: str | None = None


class SearchHCPInput(BaseModel):
    doctor_name: str | None = Field(default=None, description="Partial or full doctor name")
    specialty: str | None = None
    interaction_type: InteractionType | None = None
    sentiment: Sentiment | None = None
    from_date: date | None = None
    to_date: date | None = None
    limit: int = Field(default=20, ge=1, le=100)


class SearchHCPOutput(BaseToolOutput):
    total: int = 0
    results: list[InteractionSearchResult] = Field(default_factory=list)


class SearchHCPTool:
    """Search previous HCP interactions."""

    name = "search_hcp"
    description = (
        "Search previous doctor interactions by name, specialty, date range, type, or sentiment. "
        "Returns structured JSON with matching interaction records."
    )

    @classmethod
    async def execute(cls, ctx: ToolContext, input_data: SearchHCPInput) -> SearchHCPOutput:
        try:
            hcp_id: UUID | None = None

            if input_data.doctor_name:
                hcp = await hcp_crud.get_by_doctor_name(
                    ctx.db,
                    doctor_name=input_data.doctor_name,
                    owner_id=ctx.owner_id,
                )
                if not hcp and input_data.specialty is None:
                    return SearchHCPOutput(
                        success=True,
                        message="No matching HCP found",
                        total=0,
                        results=[],
                    )
                if hcp:
                    hcp_id = hcp.id

            interactions = await interaction_crud.get_multi_by_owner(
                ctx.db,
                owner_id=ctx.owner_id,
                skip=0,
                limit=input_data.limit,
                hcp_id=hcp_id,
                interaction_type=input_data.interaction_type,
                sentiment=input_data.sentiment,
                from_date=input_data.from_date,
                to_date=input_data.to_date,
            )

            if input_data.doctor_name and not hcp_id:
                needle = input_data.doctor_name.lower()
                interactions = [
                    i for i in interactions if needle in i.doctor_name.lower()
                ]

            if input_data.specialty:
                filtered = []
                for item in interactions:
                    hcp = await hcp_crud.get_by_owner(
                        ctx.db, hcp_id=item.hcp_id, owner_id=ctx.owner_id
                    )
                    if hcp and hcp.specialty and input_data.specialty.lower() in hcp.specialty.lower():
                        filtered.append(item)
                interactions = filtered

            results = [
                InteractionSearchResult(
                    interaction_id=item.id,
                    hcp_id=item.hcp_id,
                    doctor_name=item.doctor_name,
                    interaction_type=item.interaction_type,
                    interaction_date=item.interaction_date,
                    topics=item.topics or [],
                    sentiment=item.sentiment,
                    outcome=item.outcome,
                )
                for item in interactions
            ]

            logger.info("tool_search_hcp_success", total=len(results))

            return SearchHCPOutput(
                success=True,
                message=f"Found {len(results)} interaction(s)",
                total=len(results),
                results=results,
            )

        except Exception as exc:
            logger.error("tool_search_hcp_failed", error=str(exc))
            return SearchHCPOutput(
                success=False,
                message="Failed to search interactions",
                errors=[ToolError(code="SEARCH_FAILED", message=str(exc))],
            )
