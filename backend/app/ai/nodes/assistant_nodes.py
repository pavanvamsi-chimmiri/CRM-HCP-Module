import json
from datetime import date, datetime

from app.ai.assistant_state import AssistantState
from app.ai.groq_service import ChatMessage, ChatRequest, get_groq_service
from app.ai.prompts.assistant import ASSISTANT_MISSING_FIELDS_PROMPT, ASSISTANT_RESPONSE_PROMPT
from app.core.logging import get_logger

logger = get_logger(__name__)

FIELD_QUESTIONS = {
    "doctor_name": "Which doctor or HCP did you meet with?",
    "topics": "What topics were discussed during the visit?",
    "outcome": "What was the outcome of the interaction?",
    "sentiment": "How would you describe the doctor's sentiment — positive, neutral, negative, or mixed?",
    "follow_up": "Is there a follow-up action planned, such as a callback or sample delivery?",
    "interaction_type": "Was this an in-person visit, phone call, video call, or email?",
    "interaction_date": "What date did this interaction take place?",
    "interaction_time": "What time did the interaction occur?",
}


def _normalize_entities(entities: dict) -> dict:
    """Apply sensible defaults for form auto-fill."""
    normalized = dict(entities)

    if not normalized.get("interaction_date"):
        normalized["interaction_date"] = date.today().isoformat()

    if not normalized.get("interaction_time"):
        normalized["interaction_time"] = datetime.now().strftime("%H:%M:%S")

    if not normalized.get("interaction_type"):
        normalized["interaction_type"] = "in_person"

    if normalized.get("followup_notes") and not normalized.get("follow_up"):
        normalized["follow_up"] = normalized["followup_notes"]

    return normalized


def _rule_based_missing(entities: dict) -> tuple[list[str], list[str]]:
    missing: list[str] = []
    questions: list[str] = []

    if not entities.get("doctor_name"):
        missing.append("doctor_name")
        questions.append(FIELD_QUESTIONS["doctor_name"])

    if not entities.get("topics"):
        missing.append("topics")
        questions.append(FIELD_QUESTIONS["topics"])

    if not entities.get("outcome"):
        missing.append("outcome")
        questions.append(FIELD_QUESTIONS["outcome"])

    if not entities.get("sentiment"):
        missing.append("sentiment")
        questions.append(FIELD_QUESTIONS["sentiment"])

    follow_up = entities.get("follow_up") or entities.get("followup_notes") or entities.get("followup_date")
    if not follow_up:
        missing.append("follow_up")
        questions.append(FIELD_QUESTIONS["follow_up"])

    return missing, questions[:3]


def prepare_context(state: AssistantState) -> dict:
    """Normalize entities and apply defaults before validation."""
    entities = _normalize_entities(state.get("entities", {}))
    return {"entities": entities}


def identify_missing_fields(state: AssistantState) -> dict:
    """Identify missing fields and generate follow-up questions."""
    entities = state.get("entities", {})
    validation_errors = state.get("validation_errors", [])

    rule_missing, rule_questions = _rule_based_missing(entities)

    groq = get_groq_service()
    prompt = ASSISTANT_MISSING_FIELDS_PROMPT.format(
        entities=json.dumps(entities, indent=2),
        validation_errors=json.dumps(validation_errors),
    )
    parsed = groq.invoke_json(
        prompt,
        fallback={"missing_fields": rule_missing, "follow_up_questions": rule_questions},
    )

    missing_fields = parsed.get("missing_fields") or rule_missing
    follow_up_questions = parsed.get("follow_up_questions") or rule_questions

    if not follow_up_questions and missing_fields:
        follow_up_questions = [
            FIELD_QUESTIONS.get(field, f"Could you provide the {field.replace('_', ' ')}?")
            for field in missing_fields[:3]
        ]

    is_valid = "doctor_name" not in missing_fields

    logger.info(
        "assistant_missing_identified",
        missing_count=len(missing_fields),
        question_count=len(follow_up_questions),
    )

    return {
        "entities": entities,
        "missing_fields": missing_fields,
        "follow_up_questions": follow_up_questions,
        "is_valid": is_valid,
    }


def generate_assistant_response(state: AssistantState) -> dict:
    """Generate a conversational assistant reply."""
    entities = state.get("entities", {})
    missing_fields = state.get("missing_fields", [])
    follow_up_questions = state.get("follow_up_questions", [])

    groq = get_groq_service()
    prompt = ASSISTANT_RESPONSE_PROMPT.format(
        user_input=state.get("user_input", ""),
        entities=json.dumps(entities, indent=2),
        missing_fields=json.dumps(missing_fields),
        follow_up_questions=json.dumps(follow_up_questions),
    )

    result = groq.chat(
        ChatRequest(
            messages=[ChatMessage(role="user", content=prompt)],
        )
    )

    response = result.content.strip() if result.success else _fallback_response(entities, follow_up_questions)

    return {"response": response}


def _fallback_response(entities: dict, questions: list[str]) -> str:
    parts = []
    if entities.get("doctor_name"):
        parts.append(f"I've captured your visit with {entities['doctor_name']}.")
    else:
        parts.append("I've started filling in the interaction form.")

    if entities.get("topics"):
        parts.append(f"Topics noted: {', '.join(entities['topics'])}.")

    if questions:
        parts.append(questions[0])

    return " ".join(parts) if parts else "I've processed your message and updated the form where possible."
