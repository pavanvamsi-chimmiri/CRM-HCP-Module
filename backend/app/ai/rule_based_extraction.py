"""Rule-based entity extraction when Groq is unavailable."""

import re
from datetime import date, timedelta

from app.models import InteractionType, Sentiment

_DOCTOR_PATTERNS = [
    re.compile(
        r"(?:met|visited|saw|with|called|spoke(?:\s+with)?)\s+(?:Dr\.?|Doctor)\s+"
        r"([A-Z][a-zA-Z]+)",
        re.IGNORECASE,
    ),
    re.compile(r"(?:Dr\.?|Doctor)\s+([A-Z][a-zA-Z]+)", re.IGNORECASE),
]

_TOPIC_PATTERNS = [
    re.compile(r"discussed\s+(.+?)(?:\.|$)", re.IGNORECASE),
    re.compile(r"topics?\s*(?:were|:)\s*(.+?)(?:\.|$)", re.IGNORECASE),
    re.compile(r"talked\s+about\s+(.+?)(?:\.|$)", re.IGNORECASE),
]

_MATERIAL_PATTERNS = [
    re.compile(r"shared\s+(.+?)(?:\.|$)", re.IGNORECASE),
    re.compile(r"(?:left|gave|provided|handed)\s+(.+?)(?:\.|$)", re.IGNORECASE),
]

_FOLLOWUP_PATTERNS = [
    re.compile(r"follow[\s-]?up\s+(.+?)(?:\.|$)", re.IGNORECASE),
    re.compile(r"call\s+(?:after|in)\s+(.+?)(?:\.|$)", re.IGNORECASE),
    re.compile(r"(?:next|in)\s+(?:week|month|\d+\s+weeks?)", re.IGNORECASE),
]

_SENTIMENT_KEYWORDS: dict[Sentiment, tuple[str, ...]] = {
    Sentiment.POSITIVE: (
        "positive",
        "interested",
        "enthusiastic",
        "receptive",
        "supportive",
        "agreed",
        "keen",
    ),
    Sentiment.NEGATIVE: ("negative", "uninterested", "declined", "resistant", "skeptical"),
    Sentiment.NEUTRAL: ("neutral", "noncommittal"),
    Sentiment.MIXED: ("mixed",),
}

_INTERACTION_TYPE_KEYWORDS: dict[InteractionType, tuple[str, ...]] = {
    InteractionType.IN_PERSON: ("in person", "in-person", "visit", "met at", "clinic", "hospital"),
    InteractionType.PHONE_CALL: ("phone call", "called", "spoke on phone", "telephone"),
    InteractionType.VIDEO_CALL: ("video call", "zoom", "teams", "virtual meeting"),
    InteractionType.EMAIL: ("email", "e-mail"),
    InteractionType.CONFERENCE: ("conference", "symposium", "congress"),
}


def _first_match(patterns: list[re.Pattern[str]], text: str) -> str | None:
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            value = match.group(1).strip().rstrip(".")
            if value:
                return value
    return None


def _extract_doctor_name(text: str) -> str | None:
    for pattern in _DOCTOR_PATTERNS:
        match = pattern.search(text)
        if match:
            name = match.group(1).strip()
            if name:
                return f"Dr. {name}" if not name.lower().startswith("dr") else name
    return None


def _extract_topics(text: str) -> list[str]:
    topics: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        lowered = line.lower()
        if lowered.startswith("discussed "):
            topic = line.split(None, 1)[1].strip().rstrip(".")
            if topic:
                topics.append(topic)
                continue
        for pattern in _TOPIC_PATTERNS:
            match = pattern.search(line)
            if match:
                topic = match.group(1).strip().rstrip(".")
                if topic and topic not in topics:
                    topics.append(topic)

    if not topics:
        topic = _first_match(_TOPIC_PATTERNS, text)
        if topic:
            topics.append(topic)

    return topics


def _extract_materials(text: str) -> list[str]:
    materials: list[str] = []
    for line in text.splitlines():
        for pattern in _MATERIAL_PATTERNS:
            match = pattern.search(line)
            if match:
                material = match.group(1).strip().rstrip(".")
                if material and material not in materials:
                    materials.append(material)

    if not materials:
        material = _first_match(_MATERIAL_PATTERNS, text)
        if material:
            materials.append(material)

    return materials


def _extract_sentiment(text: str) -> str | None:
    lowered = text.lower()
    for sentiment, keywords in _SENTIMENT_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            return sentiment.value
    return None


def _extract_interaction_type(text: str) -> str | None:
    lowered = text.lower()
    for interaction_type, keywords in _INTERACTION_TYPE_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            return interaction_type.value
    if "met " in lowered or "visit" in lowered:
        return InteractionType.IN_PERSON.value
    return None


def _extract_outcome(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        lowered = stripped.lower()
        if any(
            phrase in lowered
            for phrase in ("interested", "outcome", "agreed", "declined", "prescrib", "will try")
        ):
            return stripped.rstrip(".")
    return None


def _extract_followup(text: str) -> tuple[str | None, str | None]:
    lowered = text.lower()
    notes: list[str] = []
    followup_date: str | None = None

    if "two weeks" in lowered or "2 weeks" in lowered:
        followup_date = (date.today() + timedelta(weeks=2)).isoformat()
        notes.append("Call after two weeks")
    elif "next week" in lowered:
        followup_date = (date.today() + timedelta(weeks=1)).isoformat()
        notes.append("Follow up next week")
    else:
        for pattern in _FOLLOWUP_PATTERNS:
            match = pattern.search(text)
            if match:
                note = match.group(0).strip().rstrip(".")
                if note and note not in notes:
                    notes.append(note)

    followup_notes = notes[0] if notes else None
    return followup_notes, followup_date


def extract_entities_rule_based(text: str) -> dict:
    """Extract HCP interaction fields using regex and keyword rules."""
    doctor_name = _extract_doctor_name(text)
    topics = _extract_topics(text)
    materials = _extract_materials(text)
    sentiment = _extract_sentiment(text)
    interaction_type = _extract_interaction_type(text)
    outcome = _extract_outcome(text)
    followup_notes, followup_date = _extract_followup(text)

    entities: dict = {
        "doctor_name": doctor_name,
        "interaction_type": interaction_type,
        "topics": topics,
        "sentiment": sentiment,
        "outcome": outcome,
        "materials": materials,
        "followup_notes": followup_notes,
        "followup_date": followup_date,
    }

    return {key: value for key, value in entities.items() if value not in (None, [], "")}
