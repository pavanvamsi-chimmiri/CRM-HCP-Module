from app.ai.graph import (
    EDIT_INTERACTION_TOOL,
    ENTITY_EXTRACTION,
    GENERATE_RESPONSE,
    INTENT_DETECTION,
    LOG_INTERACTION_TOOL,
    RECOMMEND_FOLLOWUP_TOOL,
    SEARCH_HCP_TOOL,
    SUMMARIZE_INTERACTION_TOOL,
    VALIDATION,
    build_hcp_agent_graph,
    compile_hcp_agent_graph,
)


def test_graph_has_all_nodes() -> None:
    graph = build_hcp_agent_graph()
    node_names = set(graph.nodes.keys())
    expected = {
        INTENT_DETECTION,
        ENTITY_EXTRACTION,
        VALIDATION,
        RECOMMEND_FOLLOWUP_TOOL,
        LOG_INTERACTION_TOOL,
        SEARCH_HCP_TOOL,
        SUMMARIZE_INTERACTION_TOOL,
        EDIT_INTERACTION_TOOL,
        GENERATE_RESPONSE,
    }
    assert expected.issubset(node_names)


def test_graph_compiles() -> None:
    compiled = compile_hcp_agent_graph()
    assert compiled is not None
    assert hasattr(compiled, "ainvoke")
