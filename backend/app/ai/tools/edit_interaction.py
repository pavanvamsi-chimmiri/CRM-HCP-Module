from datetime import date, time
from uuid import UUID

from pydantic import BaseModel, Field

from app.ai.tools.base import BaseToolOutput, ToolContext, ToolError
from app.ai.tools.helpers import resolve_material_ids
from app.core.logging import get_logger
from app.crud import interaction as interaction_crud
from app.models import InteractionType, Sentiment

logger = get_logger(__name__)


class EditInteractionInput(BaseModel):
    interaction_id: UUID
    doctor_name: str | None = Field(default=None, max_length=255)
    interaction_type: InteractionType | None = None
    interaction_date: date | None = None
    interaction_time: time | None = None
    topics: list[str] | None = None
    sentiment: Sentiment | None = None
    outcome: str | None = None
    samples: str | None = None
    materials: list[str] | None = None


class EditInteractionOutput(BaseToolOutput):
    interaction_id: UUID | None = None
    updated_fields: list[str] = Field(default_factory=list)


class EditInteractionTool:
    """Edit an existing HCP interaction."""

    name = "edit_interaction"
    description = (
        "Update fields on an existing interaction by ID. Only provided fields are changed. "
        "Returns structured JSON with updated field names."
    )

    @classmethod
    async def execute(cls, ctx: ToolContext, input_data: EditInteractionInput) -> EditInteractionOutput:
        try:
            interaction = await interaction_crud.get_by_owner(
                ctx.db,
                interaction_id=input_data.interaction_id,
                owner_id=ctx.owner_id,
            )
            if not interaction:
                return EditInteractionOutput(
                    success=False,
                    message="Interaction not found",
                    errors=[ToolError(code="NOT_FOUND", message="Interaction not found or access denied")],
                )

            update_data = input_data.model_dump(
                exclude={"interaction_id", "materials"},
                exclude_unset=True,
            )
            updated_fields = list(update_data.keys())

            if not updated_fields and input_data.materials is None:
                return EditInteractionOutput(
                    success=False,
                    message="No fields provided to update",
                    errors=[ToolError(code="NO_CHANGES", message="No update fields supplied")],
                )

            if update_data:
                await interaction_crud.update(ctx.db, db_obj=interaction, obj_in=update_data)

            if input_data.materials is not None:
                material_ids = await resolve_material_ids(
                    ctx.db,
                    material_names=input_data.materials,
                    owner_id=ctx.owner_id,
                )
                await interaction_crud.set_materials(
                    ctx.db,
                    interaction=interaction,
                    material_ids=material_ids,
                )
                updated_fields.append("materials")

            logger.info(
                "tool_edit_interaction_success",
                interaction_id=str(input_data.interaction_id),
                fields=updated_fields,
            )

            return EditInteractionOutput(
                success=True,
                message="Interaction updated successfully",
                interaction_id=input_data.interaction_id,
                updated_fields=updated_fields,
            )

        except Exception as exc:
            logger.error("tool_edit_interaction_failed", error=str(exc))
            return EditInteractionOutput(
                success=False,
                message="Failed to edit interaction",
                errors=[ToolError(code="EDIT_FAILED", message=str(exc))],
            )
