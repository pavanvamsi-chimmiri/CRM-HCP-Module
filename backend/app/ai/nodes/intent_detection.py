from app.ai.groq_service import get_groq_service
from app.ai.prompts.hcp_agent import INTENT_DETECTION_PROMPT
from app.ai.schemas import IntentResult
from app.ai.state import AgentState
from app.core.logging import get_logger

logger = get_logger(__name__)


def detect_intent(state: AgentState) -> dict:
    """Classify the user's intent from their message."""
    user_input = state.get("user_input", "")
    groq = get_groq_service()
    prompt = INTENT_DETECTION_PROMPT.format(user_input=user_input)
    parsed = groq.invoke_json(
        prompt,
        fallback={"intent": "general", "confidence": 0.5, "reasoning": "Fallback classification"},
    )

    try:
        result = IntentResult.model_validate(parsed)
    except Exception:
        logger.warning("intent_validation_failed", parsed=parsed)
        result = IntentResult(intent="general", confidence=0.5, reasoning="Parse fallback")

    logger.info(
        "intent_detected",
        intent=result.intent,
        confidence=result.confidence,
    )

    return {
        "intent": result.intent,
        "intent_confidence": result.confidence,
        "intent_reasoning": result.reasoning,
    }
