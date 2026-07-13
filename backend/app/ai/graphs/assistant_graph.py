from langgraph.graph import END, START, StateGraph

from app.ai.assistant_state import AssistantState
from app.ai.nodes.assistant_nodes import (
    generate_assistant_response,
    identify_missing_fields,
    prepare_context,
)
from app.ai.nodes.entity_extraction import extract_entities
from app.ai.nodes.intent_detection import detect_intent
from app.ai.nodes.validation import validate_entities
from app.core.logging import get_logger

logger = get_logger(__name__)

INTENT_DETECTION = "intent_detection"
ENTITY_EXTRACTION = "entity_extraction"
PREPARE_CONTEXT = "prepare_context"
VALIDATION = "validation"
IDENTIFY_MISSING = "identify_missing"
GENERATE_RESPONSE = "generate_response"


def build_assistant_graph() -> StateGraph:
    """
    LangGraph workflow for the form assistant panel.

    Extracts entities from natural language, validates, identifies gaps,
    and generates follow-up questions — without saving to the database.
    """
    graph = StateGraph(AssistantState)

    graph.add_node(INTENT_DETECTION, detect_intent)
    graph.add_node(ENTITY_EXTRACTION, extract_entities)
    graph.add_node(PREPARE_CONTEXT, prepare_context)
    graph.add_node(VALIDATION, validate_entities)
    graph.add_node(IDENTIFY_MISSING, identify_missing_fields)
    graph.add_node(GENERATE_RESPONSE, generate_assistant_response)

    graph.add_edge(START, INTENT_DETECTION)
    graph.add_edge(INTENT_DETECTION, ENTITY_EXTRACTION)
    graph.add_edge(ENTITY_EXTRACTION, PREPARE_CONTEXT)
    graph.add_edge(PREPARE_CONTEXT, VALIDATION)
    graph.add_edge(VALIDATION, IDENTIFY_MISSING)
    graph.add_edge(IDENTIFY_MISSING, GENERATE_RESPONSE)
    graph.add_edge(GENERATE_RESPONSE, END)

    return graph


def compile_assistant_graph():
    graph = build_assistant_graph()
    compiled = graph.compile()
    logger.info("assistant_graph_compiled")
    return compiled
