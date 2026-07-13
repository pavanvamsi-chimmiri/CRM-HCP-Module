import json
import re
from typing import Any

from app.core.logging import get_logger

logger = get_logger(__name__)


def parse_llm_json(content: str) -> dict[str, Any]:
    """Extract and parse a JSON object from an LLM response."""
    text = content.strip()

    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1)
    else:
        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
        if brace_match:
            text = brace_match.group(0)

    return json.loads(text)


def safe_parse_llm_json(content: str, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        return parse_llm_json(content)
    except (json.JSONDecodeError, TypeError) as exc:
        logger.warning("llm_json_parse_failed", error=str(exc), content_preview=content[:200])
        return fallback or {}
