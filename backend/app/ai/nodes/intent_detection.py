from app.ai.llm import get_llm
from app.ai.prompts.hcp_agent import INTENT_DETECTION_PROMPT
from app.ai.schemas import IntentResult
from app.ai.state import AgentState
from app.ai.utils import safe_parse_llm_json
from app.core.logging import get_logger

logger = get_logger(__name__)


def detect_intent(state: AgentState) -> dict:
    """Classify the user's intent from their message."""
    user_input = state.get("user_input", "")
    llm = get_llm()

    prompt = INTENT_DETECTION_PROMPT.format(user_input=user_input)
    response = llm.invoke(prompt)
    content = response.content if isinstance(response.content, str) else str(response.content)

    parsed = safe_parse_llm_json(
        content,
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
