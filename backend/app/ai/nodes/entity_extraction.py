from app.ai.groq_service import EntityExtractionRequest, get_groq_service
from app.ai.state import AgentState
from app.core.logging import get_logger

logger = get_logger(__name__)


def extract_entities(state: AgentState) -> dict:
    """Extract HCP interaction entities from the user message."""
    user_input = state.get("user_input", "")
    intent = state.get("intent", "general")

    groq = get_groq_service()
    result = groq.extract_entities(
        EntityExtractionRequest(text=user_input, intent=intent),
    )

    entities = result.entities
    logger.info(
        "entities_extracted",
        doctor_name=entities.get("doctor_name"),
        offline=not groq.is_configured,
    )

    return {"entities": entities}
