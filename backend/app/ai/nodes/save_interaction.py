from datetime import date, datetime, time
from uuid import UUID

from langchain_core.runnables import RunnableConfig
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.state import AgentState
from app.core.logging import get_logger
from app.crud import followup as followup_crud
from app.crud import hcp as hcp_crud
from app.crud import interaction as interaction_crud
from app.models import FollowupStatus, InteractionType, Material, Sentiment

logger = get_logger(__name__)


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


def _parse_time(value: str | None) -> time | None:
    if not value:
        return None
    if len(value) == 5:
        value = f"{value}:00"
    return time.fromisoformat(value)


async def _resolve_hcp(
    db: AsyncSession,
    *,
    doctor_name: str,
    owner_id: UUID,
) -> tuple[UUID, bool]:
    existing = await hcp_crud.get_by_doctor_name(db, doctor_name=doctor_name, owner_id=owner_id)
    if existing:
        return existing.id, False

    created = await hcp_crud.create(
        db,
        obj_in={"doctor_name": doctor_name, "owner_id": owner_id},
    )
    return created.id, True


async def _resolve_material_ids(
    db: AsyncSession,
    *,
    material_names: list[str],
    owner_id: UUID,
) -> list[UUID]:
    if not material_names:
        return []

    result = await db.execute(
        select(Material).where(
            Material.owner_id == owner_id,
            Material.name.in_(material_names),
            Material.is_active.is_(True),
        )
    )
    return [material.id for material in result.scalars().all()]


async def save_interaction(state: AgentState, config: RunnableConfig) -> dict:
    """Persist a validated interaction to the database."""
    intent = state.get("intent", "general")
    is_valid = state.get("is_valid", False)
    entities = state.get("entities", {})

    if intent != "log_interaction" or not is_valid:
        logger.info(
            "interaction_save_skipped",
            intent=intent,
            is_valid=is_valid,
        )
        return {
            "interaction_saved": False,
            "saved_interaction_id": None,
            "saved_hcp_id": None,
        }

    configurable = config.get("configurable", {})
    db: AsyncSession | None = configurable.get("db")
    if db is None:
        logger.error("interaction_save_failed", reason="missing_db_session")
        return {
            "interaction_saved": False,
            "saved_interaction_id": None,
            "saved_hcp_id": None,
            "validation_errors": state.get("validation_errors", [])
            + ["Database session not available"],
        }

    owner_id = UUID(state["owner_id"])
    doctor_name = entities.get("doctor_name")

    try:
        hcp_id, hcp_created = await _resolve_hcp(db, doctor_name=doctor_name, owner_id=owner_id)

        interaction_data = {
            "hcp_id": hcp_id,
            "doctor_name": doctor_name,
            "interaction_type": InteractionType(entities["interaction_type"]),
            "interaction_date": _parse_date(entities.get("interaction_date")) or date.today(),
            "interaction_time": _parse_time(entities.get("interaction_time")) or datetime.now().time(),
            "topics": entities.get("topics") or [],
            "sentiment": Sentiment(entities["sentiment"]) if entities.get("sentiment") else None,
            "outcome": entities.get("outcome"),
            "samples": entities.get("samples"),
            "owner_id": owner_id,
        }

        interaction = await interaction_crud.create(db, obj_in=interaction_data)

        material_ids = await _resolve_material_ids(
            db,
            material_names=entities.get("materials", []),
            owner_id=owner_id,
        )
        if material_ids:
            await interaction_crud.add_materials(db, interaction=interaction, material_ids=material_ids)

        followup_date = _parse_date(entities.get("followup_date"))
        followup_notes = entities.get("followup_notes") or state.get("followup_action")
        if followup_date or followup_notes:
            await followup_crud.create(
                db,
                obj_in={
                    "interaction_id": interaction.id,
                    "followup_date": followup_date or date.today(),
                    "followup_time": None,
                    "notes": followup_notes,
                    "status": FollowupStatus.PENDING,
                    "owner_id": owner_id,
                },
            )

        logger.info(
            "interaction_saved",
            interaction_id=str(interaction.id),
            hcp_created=hcp_created,
        )

        return {
            "interaction_saved": True,
            "saved_interaction_id": str(interaction.id),
            "saved_hcp_id": str(hcp_id),
        }

    except Exception as exc:
        logger.error("interaction_save_failed", error=str(exc))
        return {
            "interaction_saved": False,
            "saved_interaction_id": None,
            "saved_hcp_id": None,
            "validation_errors": state.get("validation_errors", []) + [str(exc)],
        }
