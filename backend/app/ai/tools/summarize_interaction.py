from uuid import UUID

from pydantic import BaseModel, Field

from app.ai.groq_service import SummarizeRequest, get_groq_service
from app.ai.tools.base import BaseToolOutput, ToolContext, ToolError
from app.core.logging import get_logger
from app.crud import interaction as interaction_crud

logger = get_logger(__name__)


class SummarizeInteractionInput(BaseModel):
    interaction_id: UUID | None = None
    text: str | None = Field(default=None, description="Free-text interaction notes to summarize")
    doctor_name: str | None = None
    topics: list[str] = Field(default_factory=list)
    outcome: str | None = None


class SummarizeInteractionOutput(BaseToolOutput):
    summary: str = ""
    key_points: list[str] = Field(default_factory=list)
    outcome_highlight: str = ""


class SummarizeInteractionTool:
    """Summarize a doctor's visit or interaction."""

    name = "summarize_interaction"
    description = (
        "Generate a concise summary of a doctor visit using an interaction ID or free text. "
        "Returns structured JSON with summary, key points, and outcome highlight."
    )

    @classmethod
    async def execute(
        cls,
        ctx: ToolContext,
        input_data: SummarizeInteractionInput,
    ) -> SummarizeInteractionOutput:
        try:
            doctor_name = input_data.doctor_name or "Unknown"
            interaction_type = "unknown"
            interaction_date = "unknown"
            topics = input_data.topics
            sentiment = "unknown"
            outcome = input_data.outcome
            samples = ""
            text = input_data.text or ""

            if input_data.interaction_id:
                interaction = await interaction_crud.get_with_relations(
                    ctx.db,
                    interaction_id=input_data.interaction_id,
                    owner_id=ctx.owner_id,
                )
                if not interaction:
                    return SummarizeInteractionOutput(
                        success=False,
                        message="Interaction not found",
                        errors=[ToolError(code="NOT_FOUND", message="Interaction not found")],
                    )

                doctor_name = interaction.doctor_name
                interaction_type = interaction.interaction_type.value
                interaction_date = interaction.interaction_date.isoformat()
                topics = interaction.topics or []
                sentiment = interaction.sentiment.value if interaction.sentiment else "unknown"
                outcome = interaction.outcome
                samples = interaction.samples or ""
                text = outcome or input_data.text or ""

            if not text and not topics and not outcome:
                return SummarizeInteractionOutput(
                    success=False,
                    message="No interaction content to summarize",
                    errors=[ToolError(code="NO_CONTENT", message="Provide interaction_id or text")],
                )

            groq = get_groq_service()
            result = groq.summarize(
                SummarizeRequest(
                    text=text,
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
                return SummarizeInteractionOutput(
                    success=False,
                    message=result.message,
                    errors=[
                        ToolError(code=err.code, message=err.message) for err in result.errors
                    ],
                )

            logger.info("tool_summarize_interaction_success")
            return SummarizeInteractionOutput(
                success=True,
                message="Interaction summarized successfully",
                summary=result.summary,
                key_points=result.key_points,
                outcome_highlight=result.outcome_highlight,
            )

        except Exception as exc:
            logger.error("tool_summarize_interaction_failed", error=str(exc))
            return SummarizeInteractionOutput(
                success=False,
                message="Failed to summarize interaction",
                errors=[ToolError(code="SUMMARIZE_FAILED", message=str(exc))],
            )
