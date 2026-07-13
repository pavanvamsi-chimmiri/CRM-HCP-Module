from datetime import date, time

from app.ai.llm import get_llm
from app.ai.prompts.hcp_agent import ENTITY_EXTRACTION_PROMPT
from app.ai.schemas import ExtractedEntities
from app.ai.state import AgentState
from app.ai.utils import safe_parse_llm_json
from app.core.logging import get_logger

logger = get_logger(__name__)


def _serialize_entities(entities: ExtractedEntities) -> dict:
    data = entities.model_dump()
    if data.get("interaction_date") and isinstance(data["interaction_date"], date):
        data["interaction_date"] = data["interaction_date"].isoformat()
    if data.get("interaction_time") and isinstance(data["interaction_time"], time):
        data["interaction_time"] = data["interaction_time"].isoformat()
    if data.get("followup_date") and isinstance(data["followup_date"], date):
        data["followup_date"] = data["followup_date"].isoformat()
    return data


def extract_entities(state: AgentState) -> dict:
    """Extract HCP interaction entities from the user message."""
    user_input = state.get("user_input", "")
    intent = state.get("intent", "general")
    llm = get_llm()

    prompt = ENTITY_EXTRACTION_PROMPT.format(user_input=user_input, intent=intent)
    response = llm.invoke(prompt)
    content = response.content if isinstance(response.content, str) else str(response.content)

    parsed = safe_parse_llm_json(content, fallback={})

    try:
        entities = ExtractedEntities.model_validate(parsed)
    except Exception:
        logger.warning("entity_validation_failed", parsed=parsed)
        entities = ExtractedEntities()

    serialized = _serialize_entities(entities)
    logger.info("entities_extracted", doctor_name=serialized.get("doctor_name"))

    return {"entities": serialized}
