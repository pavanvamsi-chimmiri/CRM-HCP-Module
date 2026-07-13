from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

from app.ai.groq_service import FollowupRecommendationRequest, get_groq_service
from app.ai.tools.base import BaseToolOutput, ToolContext, ToolError
from app.core.logging import get_logger
from app.crud import interaction as interaction_crud

logger = get_logger(__name__)


class RecommendFollowupInput(BaseModel):
    interaction_id: UUID | None = None
    doctor_name: str | None = None
    topics: list[str] = Field(default_factory=list)
    outcome: str | None = None
    sentiment: str | None = None


class RecommendFollowupOutput(BaseToolOutput):
    recommendations: list[str] = Field(default_factory=list)
    suggested_date: date | None = None
    priority: str = "medium"
    rationale: str = ""


class RecommendFollowupTool:
    """Generate follow-up recommendations for an HCP interaction."""

    name = "recommend_followup"
    description = (
        "Generate follow-up action recommendations based on an interaction ID or context. "
        "Returns structured JSON with recommendations, suggested date, and priority."
    )

    @classmethod
    async def execute(
        cls,
        ctx: ToolContext,
        input_data: RecommendFollowupInput,
    ) -> RecommendFollowupOutput:
        try:
            doctor_name = input_data.doctor_name or "Unknown"
            interaction_type = "unknown"
            interaction_date = "unknown"
            topics = input_data.topics
            sentiment = input_data.sentiment or "unknown"
            outcome = input_data.outcome or "None"
            samples = "None"

            if input_data.interaction_id:
                interaction = await interaction_crud.get_with_relations(
                    ctx.db,
                    interaction_id=input_data.interaction_id,
                    owner_id=ctx.owner_id,
                )
                if not interaction:
                    return RecommendFollowupOutput(
                        success=False,
                        message="Interaction not found",
                        errors=[ToolError(code="NOT_FOUND", message="Interaction not found")],
                    )
                doctor_name = interaction.doctor_name
                interaction_type = interaction.interaction_type.value
                interaction_date = interaction.interaction_date.isoformat()
                topics = interaction.topics or []
                sentiment = interaction.sentiment.value if interaction.sentiment else "unknown"
                outcome = interaction.outcome or "None"
                samples = interaction.samples or "None"

            groq = get_groq_service()
            result = groq.recommend_followup(
                FollowupRecommendationRequest(
                    doctor_name=doctor_name,
                    interaction_type=interaction_type,
                    interaction_date=interaction_date,
                    topics=topics,
                    sentiment=sentiment,
                    outcome=outcome,
                    samples=samples,
                ),
            )

            if not result.success:
                return RecommendFollowupOutput(
                    success=False,
                    message=result.message,
                    errors=[ToolError(code=err.code, message=err.message) for err in result.errors],
                )

            suggested_date = None
            if result.suggested_date:
                try:
                    suggested_date = date.fromisoformat(result.suggested_date)
                except ValueError:
                    suggested_date = None

            logger.info("tool_recommend_followup_success", count=len(result.recommendations))

            return RecommendFollowupOutput(
                success=True,
                message="Follow-up recommendations generated",
                recommendations=result.recommendations,
                suggested_date=suggested_date,
                priority=result.priority,
                rationale=result.rationale,
            )

        except Exception as exc:
            logger.error("tool_recommend_followup_failed", error=str(exc))
            return RecommendFollowupOutput(
                success=False,
                message="Failed to generate follow-up recommendations",
                errors=[ToolError(code="FOLLOWUP_FAILED", message=str(exc))],
            )
