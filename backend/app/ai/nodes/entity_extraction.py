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

    logger.info("entities_extracted", doctor_name=result.entities.get("doctor_name"))

    return {"entities": result.entities}
