from uuid import UUID

from app.ai.assistant_state import AssistantState
from app.ai.graphs.assistant_graph import compile_assistant_graph
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class FormAssistantAgent:
    """LangGraph-powered assistant for natural-language form filling."""

    def __init__(self) -> None:
        self._graph = compile_assistant_graph()

    async def run(
        self,
        *,
        message: str,
        owner_id: UUID,
        conversation_history: list[dict[str, str]] | None = None,
    ) -> AssistantState:
        if not settings.AI_AGENT_ENABLED:
            return {
                "user_input": message,
                "owner_id": str(owner_id),
                "entities": {},
                "missing_fields": ["doctor_name"],
                "follow_up_questions": ["Which doctor did you meet with?"],
                "response": "AI assistant is currently disabled. Please fill the form manually.",
                "is_valid": False,
            }

        context_parts: list[str] = []
        for entry in conversation_history or []:
            role = entry.get("role", "user").capitalize()
            content = entry.get("content", "")
            if content:
                context_parts.append(f"{role}: {content}")

        conversation_context = "\n".join(context_parts)
        full_input = message
        if conversation_context:
            full_input = f"{conversation_context}\nUser: {message}"

        initial_state: AssistantState = {
            "user_input": full_input,
            "conversation_context": conversation_context,
            "owner_id": str(owner_id),
            "entities": {},
            "validation_errors": [],
            "validation_warnings": [],
            "missing_fields": [],
            "follow_up_questions": [],
        }

        logger.info("assistant_agent_run_started", owner_id=str(owner_id))
        result = await self._graph.ainvoke(initial_state)
        logger.info(
            "assistant_agent_run_completed",
            missing=len(result.get("missing_fields", [])),
        )
        return result


def get_form_assistant_agent() -> FormAssistantAgent:
    return FormAssistantAgent()
