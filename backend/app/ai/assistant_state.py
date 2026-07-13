"""State for the form-assistant LangGraph workflow."""

from typing import TypedDict


class AssistantState(TypedDict, total=False):
    """State for the HCP form assistant (extract + clarify, no auto-save)."""

    user_input: str
    conversation_context: str
    owner_id: str

    intent: str
    intent_confidence: float

    entities: dict

    is_valid: bool
    validation_errors: list[str]
    validation_warnings: list[str]

    missing_fields: list[str]
    follow_up_questions: list[str]

    response: str
