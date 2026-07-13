from uuid import UUID

from pydantic import BaseModel, Field

from app.ai.llm import get_llm
from app.ai.tools.base import BaseToolOutput, ToolContext, ToolError
from app.ai.utils import safe_parse_llm_json
from app.core.logging import get_logger
from app.crud import interaction as interaction_crud

logger = get_logger(__name__)

SUMMARIZE_PROMPT = """Summarize this healthcare professional (HCP) interaction.

Provide a concise professional summary for a CRM record.

Respond ONLY with valid JSON:
{{
  "summary": "<2-3 sentence summary>",
  "key_points": ["<point>"],
  "outcome_highlight": "<main outcome>"
}}

Interaction details:
Doctor: {doctor_name}
Type: {interaction_type}
Date: {interaction_date}
Topics: {topics}
Sentiment: {sentiment}
Outcome: {outcome}
Samples: {samples}
Notes: {notes}
"""


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
            notes = input_data.text or ""

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
                notes = outcome or input_data.text or ""

            if not notes and not topics and not outcome:
                return SummarizeInteractionOutput(
                    success=False,
                    message="No interaction content to summarize",
                    errors=[ToolError(code="NO_CONTENT", message="Provide interaction_id or text")],
                )

            llm = get_llm()
            prompt = SUMMARIZE_PROMPT.format(
                doctor_name=doctor_name,
                interaction_type=interaction_type,
                interaction_date=interaction_date,
                topics=", ".join(topics) if topics else "None",
                sentiment=sentiment,
                outcome=outcome or "None",
                samples=samples or "None",
                notes=notes,
            )
            response = llm.invoke(prompt)
            content = response.content if isinstance(response.content, str) else str(response.content)
            parsed = safe_parse_llm_json(content, fallback={})

            output = SummarizeInteractionOutput(
                success=True,
                message="Interaction summarized successfully",
                summary=parsed.get("summary", ""),
                key_points=parsed.get("key_points", []),
                outcome_highlight=parsed.get("outcome_highlight", ""),
            )

            if not output.summary:
                output = SummarizeInteractionOutput(
                    success=False,
                    message="Failed to generate summary",
                    errors=[ToolError(code="LLM_PARSE_FAILED", message="Empty summary from model")],
                )

            logger.info("tool_summarize_interaction_success")
            return output

        except Exception as exc:
            logger.error("tool_summarize_interaction_failed", error=str(exc))
            return SummarizeInteractionOutput(
                success=False,
                message="Failed to summarize interaction",
                errors=[ToolError(code="SUMMARIZE_FAILED", message=str(exc))],
            )
