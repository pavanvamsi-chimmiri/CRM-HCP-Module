from typing import TypedDict


class AgentState(TypedDict, total=False):
    """Shared state passed through the HCP interaction agent graph."""

    # Input
    user_input: str
    owner_id: str

    # Intent detection
    intent: str
    intent_confidence: float
    intent_reasoning: str

    # Entity extraction
    entities: dict

    # Validation
    is_valid: bool
    validation_errors: list[str]
    validation_warnings: list[str]

    # Recommendation
    recommendations: list[str]
    suggested_materials: list[str]
    followup_action: str | None

    # Persistence
    saved_interaction_id: str | None
    saved_hcp_id: str | None
    interaction_saved: bool

    # Output
    response: str
