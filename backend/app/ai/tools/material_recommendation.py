from pydantic import BaseModel, Field

from app.ai.groq_service import get_groq_service
from app.ai.tools.base import BaseToolOutput, ToolContext, ToolError
from app.core.logging import get_logger
from app.crud import material as material_crud

logger = get_logger(__name__)

MATERIAL_PROMPT = """You are a pharmaceutical CRM assistant recommending promotional materials.

Based on the interaction context and available catalog, recommend the most relevant brochures/materials.

Respond ONLY with valid JSON:
{{
  "recommended_materials": [
    {{
      "name": "<material name from catalog or suggested>",
      "reason": "<why this material is relevant>",
      "priority": "high|medium|low"
    }}
  ],
  "strategy": "<brief sharing strategy>"
}}

Interaction context:
Doctor: {doctor_name}
Specialty: {specialty}
Topics: {topics}
Outcome: {outcome}
Sentiment: {sentiment}

Available material catalog:
{catalog}
"""


class RecommendedMaterial(BaseModel):
    name: str
    reason: str
    priority: str = "medium"
    material_id: str | None = None
    category: str | None = None


class MaterialRecommendationInput(BaseModel):
    doctor_name: str | None = None
    specialty: str | None = None
    topics: list[str] = Field(default_factory=list)
    outcome: str | None = None
    sentiment: str | None = None


class MaterialRecommendationOutput(BaseToolOutput):
    recommended_materials: list[RecommendedMaterial] = Field(default_factory=list)
    strategy: str = ""


class MaterialRecommendationTool:
    """Recommend brochures and promotional materials."""

    name = "recommend_materials"
    description = (
        "Recommend brochures and promotional materials based on doctor specialty, topics, "
        "and interaction context. Returns structured JSON with material names and reasons."
    )

    @classmethod
    async def execute(
        cls,
        ctx: ToolContext,
        input_data: MaterialRecommendationInput,
    ) -> MaterialRecommendationOutput:
        try:
            catalog_items = await material_crud.get_multi_by_owner(
                ctx.db,
                owner_id=ctx.owner_id,
                skip=0,
                limit=50,
                active_only=True,
            )

            if catalog_items:
                catalog = "\n".join(
                    f"- {m.name} ({m.category or 'general'}): {m.description or 'No description'}"
                    for m in catalog_items
                )
                catalog_map = {m.name.lower(): m for m in catalog_items}
            else:
                catalog = "No catalog items available. Suggest common HCP brochure types."
                catalog_map = {}

            groq = get_groq_service()
            prompt = MATERIAL_PROMPT.format(
                doctor_name=input_data.doctor_name or "Unknown",
                specialty=input_data.specialty or "Unknown",
                topics=", ".join(input_data.topics) if input_data.topics else "None",
                outcome=input_data.outcome or "None",
                sentiment=input_data.sentiment or "unknown",
                catalog=catalog,
            )
            parsed = groq.invoke_json(prompt, fallback={})

            raw_materials = parsed.get("recommended_materials", [])
            recommended: list[RecommendedMaterial] = []

            for item in raw_materials:
                if not isinstance(item, dict):
                    continue
                name = item.get("name", "")
                catalog_entry = catalog_map.get(name.lower())
                recommended.append(
                    RecommendedMaterial(
                        name=name,
                        reason=item.get("reason", ""),
                        priority=item.get("priority", "medium"),
                        material_id=str(catalog_entry.id) if catalog_entry else None,
                        category=catalog_entry.category if catalog_entry else None,
                    )
                )

            if not recommended:
                recommended = [
                    RecommendedMaterial(
                        name="Product Overview Brochure",
                        reason="General introductory material for HCP engagement",
                        priority="medium",
                    )
                ]

            logger.info("tool_material_recommendation_success", count=len(recommended))

            return MaterialRecommendationOutput(
                success=True,
                message="Material recommendations generated",
                recommended_materials=recommended,
                strategy=parsed.get("strategy", ""),
            )

        except Exception as exc:
            logger.error("tool_material_recommendation_failed", error=str(exc))
            return MaterialRecommendationOutput(
                success=False,
                message="Failed to generate material recommendations",
                errors=[ToolError(code="MATERIAL_FAILED", message=str(exc))],
            )
