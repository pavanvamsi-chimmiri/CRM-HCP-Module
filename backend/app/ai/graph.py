from langgraph.graph import END, START, StateGraph

from app.ai.nodes import detect_intent, extract_entities, generate_response, validate_entities
from app.ai.nodes.tool_nodes import (
    run_edit_interaction_tool,
    run_log_interaction_tool,
    run_recommend_followup_tool,
    run_search_hcp_tool,
    run_summarize_interaction_tool,
)
from app.ai.routing import route_after_recommendation, route_after_validation
from app.ai.state import AgentState
from app.core.logging import get_logger

logger = get_logger(__name__)

# Node identifiers
INTENT_DETECTION = "intent_detection"
ENTITY_EXTRACTION = "entity_extraction"
VALIDATION = "validation"
RECOMMEND_FOLLOWUP_TOOL = "recommend_followup_tool"
LOG_INTERACTION_TOOL = "log_interaction_tool"
SEARCH_HCP_TOOL = "search_hcp_tool"
SUMMARIZE_INTERACTION_TOOL = "summarize_interaction_tool"
EDIT_INTERACTION_TOOL = "edit_interaction_tool"
GENERATE_RESPONSE = "generate_response"


def build_hcp_agent_graph() -> StateGraph:
    """
    Build the HCP interaction agent graph.

    Workflow:
        Intent Detection → Entity Extraction → Validation
        → (intent-based tool routing)
        → Generate Response

    Tools invoked by dedicated graph nodes:
        - LogInteractionTool
        - EditInteractionTool
        - SearchHCPTool
        - SummarizeInteractionTool
        - RecommendFollowupTool
    """
    graph = StateGraph(AgentState)

    graph.add_node(INTENT_DETECTION, detect_intent)
    graph.add_node(ENTITY_EXTRACTION, extract_entities)
    graph.add_node(VALIDATION, validate_entities)
    graph.add_node(RECOMMEND_FOLLOWUP_TOOL, run_recommend_followup_tool)
    graph.add_node(LOG_INTERACTION_TOOL, run_log_interaction_tool)
    graph.add_node(SEARCH_HCP_TOOL, run_search_hcp_tool)
    graph.add_node(SUMMARIZE_INTERACTION_TOOL, run_summarize_interaction_tool)
    graph.add_node(EDIT_INTERACTION_TOOL, run_edit_interaction_tool)
    graph.add_node(GENERATE_RESPONSE, generate_response)

    graph.add_edge(START, INTENT_DETECTION)
    graph.add_edge(INTENT_DETECTION, ENTITY_EXTRACTION)
    graph.add_edge(ENTITY_EXTRACTION, VALIDATION)
    graph.add_conditional_edges(
        VALIDATION,
        route_after_validation,
        {
            RECOMMEND_FOLLOWUP_TOOL: RECOMMEND_FOLLOWUP_TOOL,
            SEARCH_HCP_TOOL: SEARCH_HCP_TOOL,
            SUMMARIZE_INTERACTION_TOOL: SUMMARIZE_INTERACTION_TOOL,
            EDIT_INTERACTION_TOOL: EDIT_INTERACTION_TOOL,
            GENERATE_RESPONSE: GENERATE_RESPONSE,
        },
    )
    graph.add_conditional_edges(
        RECOMMEND_FOLLOWUP_TOOL,
        route_after_recommendation,
        {
            LOG_INTERACTION_TOOL: LOG_INTERACTION_TOOL,
            GENERATE_RESPONSE: GENERATE_RESPONSE,
        },
    )
    graph.add_edge(LOG_INTERACTION_TOOL, GENERATE_RESPONSE)
    graph.add_edge(SEARCH_HCP_TOOL, GENERATE_RESPONSE)
    graph.add_edge(SUMMARIZE_INTERACTION_TOOL, GENERATE_RESPONSE)
    graph.add_edge(EDIT_INTERACTION_TOOL, GENERATE_RESPONSE)
    graph.add_edge(GENERATE_RESPONSE, END)

    return graph


def compile_hcp_agent_graph():
    """Compile the HCP agent graph for execution."""
    graph = build_hcp_agent_graph()
    compiled = graph.compile()
    logger.info("hcp_agent_graph_compiled")
    return compiled
