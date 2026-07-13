from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from app.ai.nodes.tool_nodes import (
    run_edit_interaction_tool,
    run_log_interaction_tool,
    run_recommend_followup_tool,
    run_search_hcp_tool,
    run_summarize_interaction_tool,
)
from app.ai.tools.base import ToolContext
from app.ai.tools.edit_interaction import EditInteractionOutput
from app.ai.tools.log_interaction import LogInteractionOutput
from app.ai.tools.recommend_followup import RecommendFollowupOutput
from app.ai.tools.search_hcp import SearchHCPOutput
from app.ai.tools.summarize_interaction import SummarizeInteractionOutput


@pytest.fixture
def graph_config() -> dict:
    return {
        "configurable": {
            "db": MagicMock(),
            "owner_id": str(uuid4()),
        }
    }


@pytest.fixture
def tool_context(graph_config: dict) -> ToolContext:
    return ToolContext.model_construct(
        db=graph_config["configurable"]["db"],
        owner_id=uuid4(),
    )


@pytest.mark.asyncio
async def test_run_log_interaction_tool_calls_log_interaction_tool(
    graph_config: dict,
    tool_context: ToolContext,
) -> None:
    with (
        patch("app.ai.nodes.tool_nodes.get_tool_context", return_value=tool_context),
        patch(
            "app.ai.nodes.tool_nodes.LogInteractionTool.execute",
            new_callable=AsyncMock,
        ) as mock_execute,
    ):
        mock_execute.return_value = LogInteractionOutput(
            success=True,
            message="ok",
            interaction_id=uuid4(),
            hcp_id=uuid4(),
        )
        result = await run_log_interaction_tool(
            {
                "intent": "log_interaction",
                "is_valid": True,
                "entities": {
                    "doctor_name": "Dr. Smith",
                    "interaction_type": "in_person",
                    "interaction_date": "2026-07-13",
                    "interaction_time": "10:00:00",
                    "topics": ["diabetes"],
                    "sentiment": "positive",
                },
            },
            graph_config,
        )

    mock_execute.assert_awaited_once()
    assert result["interaction_saved"] is True
    assert "log_interaction" in result["tool_results"]


@pytest.mark.asyncio
async def test_run_recommend_followup_tool_calls_recommend_tool(
    graph_config: dict,
    tool_context: ToolContext,
) -> None:
    with (
        patch("app.ai.nodes.tool_nodes.get_tool_context", return_value=tool_context),
        patch(
            "app.ai.nodes.tool_nodes.RecommendFollowupTool.execute",
            new_callable=AsyncMock,
        ) as mock_execute,
    ):
        mock_execute.return_value = RecommendFollowupOutput(
            success=True,
            message="ok",
            recommendations=["Call in two weeks"],
            rationale="Doctor showed interest",
        )
        result = await run_recommend_followup_tool(
            {"entities": {"doctor_name": "Dr. Smith", "topics": ["diabetes"]}},
            graph_config,
        )

    mock_execute.assert_awaited_once()
    assert result["recommendations"] == ["Call in two weeks"]
    assert "recommend_followup" in result["tool_results"]


@pytest.mark.asyncio
async def test_run_search_hcp_tool_calls_search_tool(
    graph_config: dict,
    tool_context: ToolContext,
) -> None:
    with (
        patch("app.ai.nodes.tool_nodes.get_tool_context", return_value=tool_context),
        patch(
            "app.ai.nodes.tool_nodes.SearchHCPTool.execute",
            new_callable=AsyncMock,
        ) as mock_execute,
    ):
        mock_execute.return_value = SearchHCPOutput(success=True, message="ok", total=0, results=[])
        result = await run_search_hcp_tool(
            {"entities": {"doctor_name": "Dr. Smith"}},
            graph_config,
        )

    mock_execute.assert_awaited_once()
    assert result["search_results"] == []
    assert "search_hcp" in result["tool_results"]


@pytest.mark.asyncio
async def test_run_summarize_interaction_tool_calls_summarize_tool(
    graph_config: dict,
    tool_context: ToolContext,
) -> None:
    with (
        patch("app.ai.nodes.tool_nodes.get_tool_context", return_value=tool_context),
        patch(
            "app.ai.nodes.tool_nodes.SummarizeInteractionTool.execute",
            new_callable=AsyncMock,
        ) as mock_execute,
    ):
        mock_execute.return_value = SummarizeInteractionOutput(
            success=True,
            message="ok",
            summary="Positive visit",
            key_points=["diabetes"],
            outcome_highlight="Interested",
        )
        result = await run_summarize_interaction_tool(
            {
                "user_input": "Discussed diabetes with Dr. Smith",
                "entities": {"doctor_name": "Dr. Smith"},
            },
            graph_config,
        )

    mock_execute.assert_awaited_once()
    assert result["summary"] == "Positive visit"
    assert "summarize_interaction" in result["tool_results"]


@pytest.mark.asyncio
async def test_run_edit_interaction_tool_calls_edit_tool(
    graph_config: dict,
    tool_context: ToolContext,
) -> None:
    interaction_id = uuid4()
    with (
        patch("app.ai.nodes.tool_nodes.get_tool_context", return_value=tool_context),
        patch(
            "app.ai.nodes.tool_nodes.EditInteractionTool.execute",
            new_callable=AsyncMock,
        ) as mock_execute,
    ):
        mock_execute.return_value = EditInteractionOutput(
            success=True,
            message="ok",
            interaction_id=interaction_id,
            updated_fields=["outcome"],
        )
        result = await run_edit_interaction_tool(
            {
                "entities": {
                    "interaction_id": str(interaction_id),
                    "outcome": "Doctor agreed to trial",
                }
            },
            graph_config,
        )

    mock_execute.assert_awaited_once()
    assert result["interaction_saved"] is True
    assert "edit_interaction" in result["tool_results"]
