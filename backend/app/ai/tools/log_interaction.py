from datetime import date, time
from uuid import UUID

from pydantic import BaseModel, Field

from app.ai.tools.base import BaseToolOutput, ToolContext, ToolError
from app.ai.tools.helpers import (
    default_interaction_time,
    resolve_hcp,
    resolve_material_ids,
)
from app.core.logging import get_logger
from app.crud import interaction as interaction_crud
from app.models import InteractionType, Sentiment

logger = get_logger(__name__)


class LogInteractionInput(BaseModel):
    doctor_name: str = Field(min_length=1, max_length=255)
    interaction_type: InteractionType
    interaction_date: date
    interaction_time: time | None = None
    topics: list[str] = Field(default_factory=list)
    sentiment: Sentiment | None = None
    outcome: str | None = None
    samples: str | None = None
    materials: list[str] = Field(default_factory=list)


class LogInteractionOutput(BaseToolOutput):
    interaction_id: UUID | None = None
    hcp_id: UUID | None = None
    hcp_created: bool = False


class LogInteractionTool:
    """Store a new HCP interaction in the database."""

    name = "log_interaction"
    description = (
        "Log a new doctor/HCP interaction with visit details, topics, sentiment, "
        "outcome, samples, and materials. Returns structured JSON with the saved IDs."
    )

    @classmethod
    async def execute(cls, ctx: ToolContext, input_data: LogInteractionInput) -> LogInteractionOutput:
        try:
            hcp_id, hcp_created = await resolve_hcp(
                ctx.db,
                doctor_name=input_data.doctor_name,
                owner_id=ctx.owner_id,
            )

            interaction = await interaction_crud.create(
                ctx.db,
                obj_in={
                    "hcp_id": hcp_id,
                    "doctor_name": input_data.doctor_name,
                    "interaction_type": input_data.interaction_type,
                    "interaction_date": input_data.interaction_date,
                    "interaction_time": input_data.interaction_time or default_interaction_time(),
                    "topics": input_data.topics,
                    "sentiment": input_data.sentiment,
                    "outcome": input_data.outcome,
                    "samples": input_data.samples,
                    "owner_id": ctx.owner_id,
                },
            )

            material_ids = await resolve_material_ids(
                ctx.db,
                material_names=input_data.materials,
                owner_id=ctx.owner_id,
            )
            if material_ids:
                await interaction_crud.add_materials(
                    ctx.db,
                    interaction=interaction,
                    material_ids=material_ids,
                )

            logger.info("tool_log_interaction_success", interaction_id=str(interaction.id))

            return LogInteractionOutput(
                success=True,
                message="Interaction logged successfully",
                interaction_id=interaction.id,
                hcp_id=hcp_id,
                hcp_created=hcp_created,
            )

        except Exception as exc:
            logger.error("tool_log_interaction_failed", error=str(exc))
            return LogInteractionOutput(
                success=False,
                message="Failed to log interaction",
                errors=[ToolError(code="LOG_FAILED", message=str(exc))],
            )
