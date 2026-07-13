from datetime import date, datetime, time
from uuid import UUID

from langchain_core.runnables import RunnableConfig

from app.ai.state import AgentState
from app.ai.tools.context import get_tool_context
from app.ai.tools.edit_interaction import EditInteractionInput, EditInteractionTool
from app.ai.tools.log_interaction import LogInteractionInput, LogInteractionTool
from app.ai.tools.recommend_followup import RecommendFollowupInput, RecommendFollowupTool
from app.ai.tools.search_hcp import SearchHCPInput, SearchHCPTool
from app.ai.tools.summarize_interaction import SummarizeInteractionInput, SummarizeInteractionTool
from app.core.logging import get_logger
from app.crud import followup as followup_crud
from app.models import FollowupStatus, InteractionType, Sentiment

logger = get_logger(__name__)


def _parse_date(value: str | date | None) -> date | None:
    if not value:
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def _parse_time(value: str | time | None) -> time | None:
    if not value:
        return None
    if isinstance(value, time):
        return value
    text = str(value)
    if len(text) == 5:
        text = f"{text}:00"
    return time.fromisoformat(text)


def _parse_uuid(value: str | UUID | None) -> UUID | None:
    if not value:
        return None
    if isinstance(value, UUID):
        return value
    return UUID(str(value))


async def run_log_interaction_tool(state: AgentState, config: RunnableConfig) -> dict:
    """Persist a validated interaction via LogInteractionTool."""
    intent = state.get("intent", "general")
    is_valid = state.get("is_valid", False)
    entities = state.get("entities", {})

    if intent != "log_interaction" or not is_valid:
        logger.info("log_interaction_tool_skipped", intent=intent, is_valid=is_valid)
        return {
            "interaction_saved": False,
            "saved_interaction_id": None,
            "saved_hcp_id": None,
            "tool_results": {**state.get("tool_results", {}), LogInteractionTool.name: {"skipped": True}},
        }

    try:
        ctx = get_tool_context(config)
        tool_input = LogInteractionInput(
            doctor_name=entities["doctor_name"],
            interaction_type=InteractionType(entities["interaction_type"]),
            interaction_date=_parse_date(entities.get("interaction_date")) or date.today(),
            interaction_time=_parse_time(entities.get("interaction_time")) or datetime.now().time(),
            topics=entities.get("topics") or [],
            sentiment=Sentiment(entities["sentiment"]) if entities.get("sentiment") else None,
            outcome=entities.get("outcome"),
            samples=entities.get("samples"),
            materials=entities.get("materials") or [],
        )
        result = await LogInteractionTool.execute(ctx, tool_input)

        followup_date = _parse_date(entities.get("followup_date"))
        followup_notes = entities.get("followup_notes") or state.get("followup_action")
        if result.success and result.interaction_id and (followup_date or followup_notes):
            await followup_crud.create(
                ctx.db,
                obj_in={
                    "interaction_id": result.interaction_id,
                    "followup_date": followup_date or date.today(),
                    "followup_time": None,
                    "notes": followup_notes,
                    "status": FollowupStatus.PENDING,
                    "owner_id": ctx.owner_id,
                },
            )

        return {
            "interaction_saved": result.success,
            "saved_interaction_id": str(result.interaction_id) if result.interaction_id else None,
            "saved_hcp_id": str(result.hcp_id) if result.hcp_id else None,
            "tool_results": {
                **state.get("tool_results", {}),
                LogInteractionTool.name: result.model_dump(mode="json"),
            },
            "validation_errors": state.get("validation_errors", [])
            + [err.message for err in result.errors],
        }
    except Exception as exc:
        logger.error("log_interaction_tool_failed", error=str(exc))
        return {
            "interaction_saved": False,
            "saved_interaction_id": None,
            "saved_hcp_id": None,
            "validation_errors": state.get("validation_errors", []) + [str(exc)],
        }


async def run_recommend_followup_tool(state: AgentState, config: RunnableConfig) -> dict:
    """Generate follow-up recommendations via RecommendFollowupTool."""
    entities = state.get("entities", {})

    try:
        ctx = get_tool_context(config)
        tool_input = RecommendFollowupInput(
            interaction_id=_parse_uuid(entities.get("interaction_id")),
            doctor_name=entities.get("doctor_name"),
            topics=entities.get("topics") or [],
            outcome=entities.get("outcome"),
            sentiment=entities.get("sentiment"),
        )
        result = await RecommendFollowupTool.execute(ctx, tool_input)

        return {
            "recommendations": result.recommendations,
            "suggested_materials": [],
            "followup_action": result.rationale or None,
            "tool_results": {
                **state.get("tool_results", {}),
                RecommendFollowupTool.name: result.model_dump(mode="json"),
            },
        }
    except Exception as exc:
        logger.error("recommend_followup_tool_failed", error=str(exc))
        return {
            "recommendations": [],
            "suggested_materials": [],
            "followup_action": None,
            "validation_errors": state.get("validation_errors", []) + [str(exc)],
        }


async def run_search_hcp_tool(state: AgentState, config: RunnableConfig) -> dict:
    """Search prior interactions via SearchHCPTool."""
    entities = state.get("entities", {})

    try:
        ctx = get_tool_context(config)
        tool_input = SearchHCPInput(
            doctor_name=entities.get("doctor_name"),
            specialty=entities.get("specialty"),
            interaction_type=(
                InteractionType(entities["interaction_type"])
                if entities.get("interaction_type")
                else None
            ),
            sentiment=Sentiment(entities["sentiment"]) if entities.get("sentiment") else None,
            from_date=_parse_date(entities.get("from_date")),
            to_date=_parse_date(entities.get("to_date")),
        )
        result = await SearchHCPTool.execute(ctx, tool_input)

        return {
            "search_results": [item.model_dump(mode="json") for item in result.results],
            "tool_results": {
                **state.get("tool_results", {}),
                SearchHCPTool.name: result.model_dump(mode="json"),
            },
        }
    except Exception as exc:
        logger.error("search_hcp_tool_failed", error=str(exc))
        return {
            "search_results": [],
            "validation_errors": state.get("validation_errors", []) + [str(exc)],
        }


async def run_summarize_interaction_tool(state: AgentState, config: RunnableConfig) -> dict:
    """Summarize interaction notes via SummarizeInteractionTool."""
    entities = state.get("entities", {})

    try:
        ctx = get_tool_context(config)
        tool_input = SummarizeInteractionInput(
            interaction_id=_parse_uuid(entities.get("interaction_id")),
            text=entities.get("summary_text") or state.get("user_input"),
            doctor_name=entities.get("doctor_name"),
            topics=entities.get("topics") or [],
            outcome=entities.get("outcome"),
        )
        result = await SummarizeInteractionTool.execute(ctx, tool_input)

        return {
            "summary": result.summary,
            "summary_key_points": result.key_points,
            "summary_outcome_highlight": result.outcome_highlight,
            "tool_results": {
                **state.get("tool_results", {}),
                SummarizeInteractionTool.name: result.model_dump(mode="json"),
            },
        }
    except Exception as exc:
        logger.error("summarize_interaction_tool_failed", error=str(exc))
        return {
            "summary": "",
            "summary_key_points": [],
            "summary_outcome_highlight": "",
            "validation_errors": state.get("validation_errors", []) + [str(exc)],
        }


async def run_edit_interaction_tool(state: AgentState, config: RunnableConfig) -> dict:
    """Update an existing interaction via EditInteractionTool."""
    entities = state.get("entities", {})
    interaction_id = _parse_uuid(entities.get("interaction_id"))

    if not interaction_id:
        return {
            "interaction_saved": False,
            "validation_errors": state.get("validation_errors", [])
            + ["interaction_id is required to edit an interaction"],
        }

    try:
        ctx = get_tool_context(config)
        tool_input = EditInteractionInput(
            interaction_id=interaction_id,
            doctor_name=entities.get("doctor_name"),
            interaction_type=(
                InteractionType(entities["interaction_type"])
                if entities.get("interaction_type")
                else None
            ),
            interaction_date=_parse_date(entities.get("interaction_date")),
            interaction_time=_parse_time(entities.get("interaction_time")),
            topics=entities.get("topics"),
            sentiment=Sentiment(entities["sentiment"]) if entities.get("sentiment") else None,
            outcome=entities.get("outcome"),
            samples=entities.get("samples"),
            materials=entities.get("materials"),
        )
        result = await EditInteractionTool.execute(ctx, tool_input)

        return {
            "interaction_saved": result.success,
            "saved_interaction_id": str(result.interaction_id) if result.interaction_id else None,
            "tool_results": {
                **state.get("tool_results", {}),
                EditInteractionTool.name: result.model_dump(mode="json"),
            },
            "validation_errors": state.get("validation_errors", [])
            + [err.message for err in result.errors],
        }
    except Exception as exc:
        logger.error("edit_interaction_tool_failed", error=str(exc))
        return {
            "interaction_saved": False,
            "validation_errors": state.get("validation_errors", []) + [str(exc)],
        }
