import json

from app.ai.llm import get_llm
from app.ai.prompts.hcp_agent import RESPONSE_GENERATION_PROMPT
from app.ai.state import AgentState
from app.core.logging import get_logger

logger = get_logger(__name__)


def generate_response(state: AgentState) -> dict:
    """Generate the final natural-language response for the user."""
    llm = get_llm()

    prompt = RESPONSE_GENERATION_PROMPT.format(
        intent=state.get("intent", "general"),
        entities=json.dumps(state.get("entities", {}), indent=2),
        is_valid=state.get("is_valid", False),
        validation_errors=json.dumps(state.get("validation_errors", [])),
        recommendations=json.dumps(state.get("recommendations", [])),
        interaction_saved=state.get("interaction_saved", False),
        saved_interaction_id=state.get("saved_interaction_id"),
        user_input=state.get("user_input", ""),
    )

    response = llm.invoke(prompt)
    content = response.content if isinstance(response.content, str) else str(response.content)

    logger.info("response_generated", length=len(content))

    return {"response": content.strip()}
