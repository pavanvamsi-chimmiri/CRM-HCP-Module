from app.ai.state import AgentState

INTENT_LOG = "log_interaction"
INTENT_QUERY = "query_interaction"
INTENT_FOLLOWUP = "schedule_followup"
INTENT_EDIT = "edit_interaction"
INTENT_SUMMARIZE = "summarize_interaction"


def route_after_validation(state: AgentState) -> str:
    """Route the graph to the correct LangGraph tool node based on detected intent."""
    intent = state.get("intent", "general")
    is_valid = state.get("is_valid", False)

    if intent == INTENT_LOG:
        return "recommend_followup_tool" if is_valid else "generate_response"
    if intent == INTENT_QUERY:
        return "search_hcp_tool"
    if intent == INTENT_FOLLOWUP:
        return "recommend_followup_tool"
    if intent == INTENT_EDIT:
        return "edit_interaction_tool"
    if intent == INTENT_SUMMARIZE:
        return "summarize_interaction_tool"
    return "generate_response"


def route_after_recommendation(state: AgentState) -> str:
    """Only log_interaction flows persist data after recommendations."""
    if state.get("intent") == INTENT_LOG:
        return "log_interaction_tool"
    return "generate_response"
