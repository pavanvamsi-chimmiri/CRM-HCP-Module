from app.ai.graph import (
    ENTITY_EXTRACTION,
    GENERATE_RESPONSE,
    INTENT_DETECTION,
    RECOMMENDATION,
    SAVE_INTERACTION,
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
        RECOMMENDATION,
        SAVE_INTERACTION,
        GENERATE_RESPONSE,
    }
    assert expected.issubset(node_names)


def test_graph_compiles() -> None:
    compiled = compile_hcp_agent_graph()
    assert compiled is not None
    assert hasattr(compiled, "ainvoke")
