from uuid import UUID

from langchain_core.runnables import RunnableConfig
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.graph import compile_hcp_agent_graph
from app.ai.state import AgentState
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class HCPAgent:
    """HCP CRM AI agent powered by LangGraph and Groq."""

    def __init__(self) -> None:
        self._graph = compile_hcp_agent_graph()

    @property
    def graph(self):
        return self._graph

    async def run(
        self,
        *,
        user_input: str,
        owner_id: UUID,
        db: AsyncSession,
    ) -> AgentState:
        if not settings.AI_AGENT_ENABLED:
            return {
                "user_input": user_input,
                "owner_id": str(owner_id),
                "response": "AI agent is currently disabled.",
                "interaction_saved": False,
            }

        initial_state: AgentState = {
            "user_input": user_input,
            "owner_id": str(owner_id),
            "entities": {},
            "validation_errors": [],
            "validation_warnings": [],
            "recommendations": [],
            "suggested_materials": [],
            "interaction_saved": False,
        }

        config: RunnableConfig = {
            "configurable": {
                "db": db,
                "owner_id": str(owner_id),
            }
        }

        logger.info("hcp_agent_run_started", owner_id=str(owner_id))
        result = await self._graph.ainvoke(initial_state, config=config)
        logger.info(
            "hcp_agent_run_completed",
            intent=result.get("intent"),
            interaction_saved=result.get("interaction_saved"),
        )
        return result


def get_hcp_agent() -> HCPAgent:
    return HCPAgent()
