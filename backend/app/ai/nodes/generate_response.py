import json

from app.ai.groq_service import ChatMessage, ChatRequest, get_groq_service
from app.ai.state import AgentState
from app.core.logging import get_logger

logger = get_logger(__name__)

RESPONSE_PROMPT = """Generate a clear, professional response for the sales representative.

Context:
- Intent: {intent}
- Entities: {entities}
- Valid: {is_valid}
- Validation errors: {validation_errors}
- Recommendations: {recommendations}
- Interaction saved: {interaction_saved}
- Saved interaction ID: {saved_interaction_id}
- Search results: {search_results}
- Summary: {summary}
- Tool results: {tool_results}

If interaction was saved, confirm what was recorded.
If validation failed, explain what information is missing.
If search results or a summary are present, present them clearly.
Include relevant recommendations naturally. Keep response concise (2-4 sentences).

User message:
{user_input}
"""


def generate_response(state: AgentState) -> dict:
    """Generate the final natural-language response for the user."""
    prompt = RESPONSE_PROMPT.format(
        intent=state.get("intent", "general"),
        entities=json.dumps(state.get("entities", {}), indent=2),
        is_valid=state.get("is_valid", False),
        validation_errors=json.dumps(state.get("validation_errors", [])),
        recommendations=json.dumps(state.get("recommendations", [])),
        interaction_saved=state.get("interaction_saved", False),
        saved_interaction_id=state.get("saved_interaction_id"),
        search_results=json.dumps(state.get("search_results", [])),
        summary=state.get("summary", ""),
        tool_results=json.dumps(state.get("tool_results", {})),
        user_input=state.get("user_input", ""),
    )

    groq = get_groq_service()
    result = groq.chat(
        ChatRequest(
            messages=[
                ChatMessage(role="user", content=prompt),
            ],
        ),
    )

    logger.info("response_generated", length=len(result.content))

    return {"response": result.content.strip() if result.success else result.message}
