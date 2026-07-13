"""Backward-compatible LLM accessor. Prefer app.ai.groq_service.get_groq_service()."""

from app.ai.groq_service import get_groq_service, get_llm

__all__ = ["get_llm", "get_groq_service"]
