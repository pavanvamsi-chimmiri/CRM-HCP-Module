import json

from app.ai.llm import get_llm
from app.ai.prompts.hcp_agent import RECOMMENDATION_PROMPT
from app.ai.schemas import RecommendationResult
from app.ai.state import AgentState
from app.ai.utils import safe_parse_llm_json
from app.core.logging import get_logger

logger = get_logger(__name__)


def generate_recommendations(state: AgentState) -> dict:
    """Generate follow-up and engagement recommendations."""
    llm = get_llm()

    prompt = RECOMMENDATION_PROMPT.format(
        intent=state.get("intent", "general"),
        entities=json.dumps(state.get("entities", {}), indent=2),
        warnings=json.dumps(state.get("validation_warnings", [])),
    )
    response = llm.invoke(prompt)
    content = response.content if isinstance(response.content, str) else str(response.content)
    parsed = safe_parse_llm_json(content, fallback={})

    try:
        result = RecommendationResult.model_validate(parsed)
    except Exception:
        logger.warning("recommendation_parse_failed", parsed=parsed)
        result = RecommendationResult(
            recommendations=["Review interaction details and plan next touchpoint"],
            suggested_materials=[],
            followup_action=None,
        )

    logger.info("recommendations_generated", count=len(result.recommendations))

    return {
        "recommendations": result.recommendations,
        "suggested_materials": result.suggested_materials,
        "followup_action": result.followup_action,
    }
