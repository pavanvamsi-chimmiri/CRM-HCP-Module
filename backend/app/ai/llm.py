from functools import lru_cache

from langchain_groq import ChatGroq

from app.core.config import settings


@lru_cache
def get_llm() -> ChatGroq:
    return ChatGroq(
        model=settings.GROQ_MODEL,
        groq_api_key=settings.GROQ_API_KEY or None,
        temperature=settings.GROQ_TEMPERATURE,
        max_tokens=settings.GROQ_MAX_TOKENS,
    )
