from collections.abc import Callable, Coroutine
from typing import Any

from langchain_core.tools import StructuredTool
from pydantic import BaseModel

from app.ai.tools.base import ToolContext
from app.ai.tools.edit_interaction import (
    EditInteractionInput,
    EditInteractionOutput,
    EditInteractionTool,
)
from app.ai.tools.log_interaction import (
    LogInteractionInput,
    LogInteractionOutput,
    LogInteractionTool,
)
from app.ai.tools.material_recommendation import (
    MaterialRecommendationInput,
    MaterialRecommendationOutput,
    MaterialRecommendationTool,
)
from app.ai.tools.recommend_followup import (
    RecommendFollowupInput,
    RecommendFollowupOutput,
    RecommendFollowupTool,
)
from app.ai.tools.search_hcp import SearchHCPInput, SearchHCPOutput, SearchHCPTool
from app.ai.tools.sentiment import SentimentInput, SentimentOutput, SentimentTool
from app.ai.tools.summarize_interaction import (
    SummarizeInteractionInput,
    SummarizeInteractionOutput,
    SummarizeInteractionTool,
)

ToolExecutor = Callable[[ToolContext, Any], Coroutine[Any, Any, BaseModel]]


def _wrap_tool(
    *,
    tool_cls: type,
    input_schema: type[BaseModel],
    executor: ToolExecutor,
    ctx: ToolContext,
) -> StructuredTool:
    async def _run(**kwargs: Any) -> str:
        input_data = input_schema(**kwargs)
        output = await executor(ctx, input_data)
        return output.model_dump_json()

    return StructuredTool.from_function(
        coroutine=_run,
        name=tool_cls.name,
        description=tool_cls.description,
        args_schema=input_schema,
    )


def get_all_tools(ctx: ToolContext) -> list[StructuredTool]:
    """Create LangGraph-compatible StructuredTool instances bound to a context."""
    return [
        _wrap_tool(
            tool_cls=LogInteractionTool,
            input_schema=LogInteractionInput,
            executor=LogInteractionTool.execute,
            ctx=ctx,
        ),
        _wrap_tool(
            tool_cls=EditInteractionTool,
            input_schema=EditInteractionInput,
            executor=EditInteractionTool.execute,
            ctx=ctx,
        ),
        _wrap_tool(
            tool_cls=SearchHCPTool,
            input_schema=SearchHCPInput,
            executor=SearchHCPTool.execute,
            ctx=ctx,
        ),
        _wrap_tool(
            tool_cls=SummarizeInteractionTool,
            input_schema=SummarizeInteractionInput,
            executor=SummarizeInteractionTool.execute,
            ctx=ctx,
        ),
        _wrap_tool(
            tool_cls=RecommendFollowupTool,
            input_schema=RecommendFollowupInput,
            executor=RecommendFollowupTool.execute,
            ctx=ctx,
        ),
        _wrap_tool(
            tool_cls=SentimentTool,
            input_schema=SentimentInput,
            executor=SentimentTool.execute,
            ctx=ctx,
        ),
        _wrap_tool(
            tool_cls=MaterialRecommendationTool,
            input_schema=MaterialRecommendationInput,
            executor=MaterialRecommendationTool.execute,
            ctx=ctx,
        ),
    ]


__all__ = [
    "LogInteractionTool",
    "LogInteractionInput",
    "LogInteractionOutput",
    "EditInteractionTool",
    "EditInteractionInput",
    "EditInteractionOutput",
    "SearchHCPTool",
    "SearchHCPInput",
    "SearchHCPOutput",
    "SummarizeInteractionTool",
    "SummarizeInteractionInput",
    "SummarizeInteractionOutput",
    "RecommendFollowupTool",
    "RecommendFollowupInput",
    "RecommendFollowupOutput",
    "SentimentTool",
    "SentimentInput",
    "SentimentOutput",
    "MaterialRecommendationTool",
    "MaterialRecommendationInput",
    "MaterialRecommendationOutput",
    "get_all_tools",
]
