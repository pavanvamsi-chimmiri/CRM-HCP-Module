from app.ai.routing import (
    INTENT_EDIT,
    INTENT_FOLLOWUP,
    INTENT_LOG,
    INTENT_QUERY,
    INTENT_SUMMARIZE,
    route_after_recommendation,
    route_after_validation,
)


def test_route_log_interaction_to_recommend_tool_when_valid() -> None:
    assert (
        route_after_validation(
            {"intent": INTENT_LOG, "is_valid": True},
        )
        == "recommend_followup_tool"
    )


def test_route_log_interaction_to_response_when_invalid() -> None:
    assert (
        route_after_validation(
            {"intent": INTENT_LOG, "is_valid": False},
        )
        == "generate_response"
    )


def test_route_query_to_search_tool() -> None:
    assert route_after_validation({"intent": INTENT_QUERY, "is_valid": True}) == "search_hcp_tool"


def test_route_summarize_to_summarize_tool() -> None:
    assert (
        route_after_validation({"intent": INTENT_SUMMARIZE, "is_valid": True})
        == "summarize_interaction_tool"
    )


def test_route_edit_to_edit_tool() -> None:
    assert route_after_validation({"intent": INTENT_EDIT, "is_valid": True}) == "edit_interaction_tool"


def test_route_followup_to_recommend_tool() -> None:
    assert (
        route_after_validation({"intent": INTENT_FOLLOWUP, "is_valid": True})
        == "recommend_followup_tool"
    )


def test_route_after_recommendation_logs_when_logging() -> None:
    assert route_after_recommendation({"intent": INTENT_LOG}) == "log_interaction_tool"


def test_route_after_recommendation_responds_for_followup() -> None:
    assert route_after_recommendation({"intent": INTENT_FOLLOWUP}) == "generate_response"
