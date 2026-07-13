
from app.ai.groq_service import FollowupRecommendationRequest, get_groq_service
from app.ai.state import AgentState
from app.core.logging import get_logger

logger = get_logger(__name__)


def generate_recommendations(state: AgentState) -> dict:
    """Generate follow-up and engagement recommendations."""
    entities = state.get("entities", {})

    groq = get_groq_service()
    result = groq.recommend_followup(
        FollowupRecommendationRequest(
            doctor_name=entities.get("doctor_name"),
            interaction_type=entities.get("interaction_type"),
            interaction_date=entities.get("interaction_date"),
            topics=entities.get("topics", []),
            sentiment=entities.get("sentiment"),
            outcome=entities.get("outcome"),
            samples=entities.get("samples"),
        ),
    )

    logger.info("recommendations_generated", count=len(result.recommendations))

    return {
        "recommendations": result.recommendations,
        "suggested_materials": [],
        "followup_action": result.rationale or None,
    }
