from langgraph.graph import END, START, StateGraph

from app.ai.nodes import (
    detect_intent,
    extract_entities,
    generate_recommendations,
    generate_response,
    save_interaction,
    validate_entities,
)
from app.ai.state import AgentState
from app.core.logging import get_logger

logger = get_logger(__name__)

# Node identifiers
INTENT_DETECTION = "intent_detection"
ENTITY_EXTRACTION = "entity_extraction"
VALIDATION = "validation"
RECOMMENDATION = "recommendation"
SAVE_INTERACTION = "save_interaction"
GENERATE_RESPONSE = "generate_response"


def build_hcp_agent_graph() -> StateGraph:
    """
    Build the modular HCP interaction agent graph.

    Workflow:
        Intent Detection → Entity Extraction → Validation → Recommendation
        → Save Interaction → Generate Response
    """
    graph = StateGraph(AgentState)

    graph.add_node(INTENT_DETECTION, detect_intent)
    graph.add_node(ENTITY_EXTRACTION, extract_entities)
    graph.add_node(VALIDATION, validate_entities)
    graph.add_node(RECOMMENDATION, generate_recommendations)
    graph.add_node(SAVE_INTERACTION, save_interaction)
    graph.add_node(GENERATE_RESPONSE, generate_response)

    graph.add_edge(START, INTENT_DETECTION)
    graph.add_edge(INTENT_DETECTION, ENTITY_EXTRACTION)
    graph.add_edge(ENTITY_EXTRACTION, VALIDATION)
    graph.add_edge(VALIDATION, RECOMMENDATION)
    graph.add_edge(RECOMMENDATION, SAVE_INTERACTION)
    graph.add_edge(SAVE_INTERACTION, GENERATE_RESPONSE)
    graph.add_edge(GENERATE_RESPONSE, END)

    return graph


def compile_hcp_agent_graph():
    """Compile the HCP agent graph for execution."""
    graph = build_hcp_agent_graph()
    compiled = graph.compile()
    logger.info("hcp_agent_graph_compiled")
    return compiled
