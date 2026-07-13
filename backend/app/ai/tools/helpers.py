from datetime import date, datetime, time
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import hcp as hcp_crud
from app.models import Material


def parse_date(value: str | date | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(value)


def parse_time(value: str | time | None) -> time | None:
    if value is None:
        return None
    if isinstance(value, time):
        return value
    if len(value) == 5:
        value = f"{value}:00"
    return time.fromisoformat(value)


async def resolve_hcp(
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


async def resolve_material_ids(
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


def default_interaction_time() -> time:
    return datetime.now().time().replace(microsecond=0)
