from uuid import uuid4

import pytest
from app.ai.tools import (
    EditInteractionInput,
    LogInteractionInput,
    MaterialRecommendationInput,
    RecommendFollowupInput,
    SearchHCPInput,
    SentimentInput,
    SummarizeInteractionInput,
    get_all_tools,
)
from app.ai.tools.base import ToolContext
from app.ai.tools.edit_interaction import EditInteractionTool
from app.ai.tools.log_interaction import LogInteractionTool
from app.ai.tools.material_recommendation import MaterialRecommendationTool
from app.ai.tools.recommend_followup import RecommendFollowupTool
from app.ai.tools.search_hcp import SearchHCPTool
from app.ai.tools.sentiment import SentimentTool
from app.ai.tools.summarize_interaction import SummarizeInteractionTool
from app.models import InteractionType
from pydantic import ValidationError


def test_all_tools_have_unique_names() -> None:
    names = [
        LogInteractionTool.name,
        EditInteractionTool.name,
        SearchHCPTool.name,
        SummarizeInteractionTool.name,
        RecommendFollowupTool.name,
        SentimentTool.name,
        MaterialRecommendationTool.name,
    ]
    assert len(names) == len(set(names))


def test_log_interaction_input_schema() -> None:
    data = LogInteractionInput(
        doctor_name="Dr. Smith",
        interaction_type=InteractionType.IN_PERSON,
        interaction_date="2026-07-13",
    )
    assert data.doctor_name == "Dr. Smith"
    assert data.interaction_type == InteractionType.IN_PERSON


def test_sentiment_input_requires_text() -> None:
    with pytest.raises(ValidationError):
        SentimentInput(text="")


def test_search_hcp_input_defaults() -> None:
    data = SearchHCPInput()
    assert data.limit == 20
    assert data.doctor_name is None


def test_tool_output_json_structure() -> None:
    from app.ai.tools.log_interaction import LogInteractionOutput

    output = LogInteractionOutput(success=True, message="ok")
    payload = output.model_dump()
    assert payload["success"] is True
    assert "errors" in payload
    assert "message" in payload


def test_get_all_tools_returns_seven() -> None:
    ctx = ToolContext.model_construct(db=object(), owner_id=uuid4())
    tools = get_all_tools(ctx)
    assert len(tools) == 7
    tool_names = {t.name for t in tools}
    assert "log_interaction" in tool_names
    assert "edit_interaction" in tool_names
    assert "search_hcp" in tool_names
    assert "summarize_interaction" in tool_names
    assert "recommend_followup" in tool_names
    assert "detect_sentiment" in tool_names
    assert "recommend_materials" in tool_names


def test_independent_input_schemas() -> None:
    schemas = [
        LogInteractionInput,
        EditInteractionInput,
        SearchHCPInput,
        SummarizeInteractionInput,
        RecommendFollowupInput,
        SentimentInput,
        MaterialRecommendationInput,
    ]
    assert len(schemas) == 7
    for schema in schemas:
        assert hasattr(schema, "model_json_schema")
