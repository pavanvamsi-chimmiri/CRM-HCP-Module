import json

from app.ai.groq_service import get_groq_service
from app.ai.prompts.hcp_agent import VALIDATION_PROMPT
from app.ai.schemas import ValidationResult
from app.ai.state import AgentState
from app.core.logging import get_logger
from app.models import InteractionType, Sentiment

logger = get_logger(__name__)

REQUIRED_FIELDS = ("doctor_name", "interaction_type", "interaction_date", "interaction_time")


def _rule_based_validation(intent: str, entities: dict) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    if intent != "log_interaction":
        return ValidationResult(is_valid=True, errors=[], warnings=["Non-log intent skips strict validation"])

    for field in REQUIRED_FIELDS:
        if not entities.get(field):
            errors.append(f"Missing required field: {field}")

    interaction_type = entities.get("interaction_type")
    if interaction_type:
        try:
            InteractionType(interaction_type)
        except ValueError:
            errors.append(f"Invalid interaction_type: {interaction_type}")

    sentiment = entities.get("sentiment")
    if sentiment:
        try:
            Sentiment(sentiment)
        except ValueError:
            errors.append(f"Invalid sentiment: {sentiment}")

    if not entities.get("topics"):
        warnings.append("No topics recorded")
    if not entities.get("outcome"):
        warnings.append("No outcome recorded")

    return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)


def validate_entities(state: AgentState) -> dict:
    """Validate extracted entities using rules and LLM review."""
    intent = state.get("intent", "general")
    entities = state.get("entities", {})

    rule_result = _rule_based_validation(intent, entities)

    if intent != "log_interaction":
        return {
            "is_valid": rule_result.is_valid,
            "validation_errors": rule_result.errors,
            "validation_warnings": rule_result.warnings,
        }

    groq = get_groq_service()
    prompt = VALIDATION_PROMPT.format(
        intent=intent,
        entities=json.dumps(entities, indent=2),
    )
    parsed = groq.invoke_json(prompt, fallback={})

    try:
        llm_result = ValidationResult.model_validate(parsed)
    except Exception:
        logger.warning("llm_validation_parse_failed", parsed=parsed)
        llm_result = ValidationResult(is_valid=rule_result.is_valid, errors=[], warnings=[])

    merged_errors = list(dict.fromkeys(rule_result.errors + llm_result.errors))
    merged_warnings = list(dict.fromkeys(rule_result.warnings + llm_result.warnings))
    is_valid = len(merged_errors) == 0 and (rule_result.is_valid or llm_result.is_valid)

    logger.info("entities_validated", is_valid=is_valid, error_count=len(merged_errors))

    return {
        "is_valid": is_valid,
        "validation_errors": merged_errors,
        "validation_warnings": merged_warnings,
    }
