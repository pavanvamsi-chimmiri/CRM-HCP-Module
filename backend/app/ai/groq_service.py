from datetime import date, time
from functools import lru_cache
from typing import Any, Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field, ValidationError

from app.ai.schemas import ExtractedEntities, RecommendationResult
from app.ai.utils import safe_parse_llm_json
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


# -----------------------------------------------------------------------------
# Request / Response schemas (structured JSON)
# -----------------------------------------------------------------------------


class GroqServiceError(BaseModel):
    code: str
    message: str


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1)
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, ge=1)


class ChatResponse(BaseModel):
    success: bool
    model: str
    content: str
    message: str = ""
    errors: list[GroqServiceError] = Field(default_factory=list)

    def to_json(self) -> str:
        return self.model_dump_json()


class SummarizeRequest(BaseModel):
    text: str = Field(min_length=1)
    doctor_name: str | None = None
    interaction_type: str | None = None
    interaction_date: str | None = None
    topics: list[str] = Field(default_factory=list)
    sentiment: str | None = None
    outcome: str | None = None
    samples: str | None = None


class SummarizeResponse(BaseModel):
    success: bool
    model: str
    summary: str = ""
    key_points: list[str] = Field(default_factory=list)
    outcome_highlight: str = ""
    message: str = ""
    errors: list[GroqServiceError] = Field(default_factory=list)

    def to_json(self) -> str:
        return self.model_dump_json()


class EntityExtractionRequest(BaseModel):
    text: str = Field(min_length=1)
    intent: str = "general"


class EntityExtractionResponse(BaseModel):
    success: bool
    model: str
    entities: dict[str, Any] = Field(default_factory=dict)
    message: str = ""
    errors: list[GroqServiceError] = Field(default_factory=list)

    def to_json(self) -> str:
        return self.model_dump_json()


class FollowupRecommendationRequest(BaseModel):
    doctor_name: str | None = None
    interaction_type: str | None = None
    interaction_date: str | None = None
    topics: list[str] = Field(default_factory=list)
    sentiment: str | None = None
    outcome: str | None = None
    samples: str | None = None


class FollowupRecommendationResponse(BaseModel):
    success: bool
    model: str
    recommendations: list[str] = Field(default_factory=list)
    suggested_date: str | None = None
    priority: str = "medium"
    rationale: str = ""
    message: str = ""
    errors: list[GroqServiceError] = Field(default_factory=list)

    def to_json(self) -> str:
        return self.model_dump_json()


# -----------------------------------------------------------------------------
# Prompts
# -----------------------------------------------------------------------------

CHAT_SYSTEM_PROMPT = (
    "You are an AI assistant for a Healthcare Professional (HCP) CRM system. "
    "Help sales representatives log interactions, search records, and plan follow-ups. "
    "Be concise and professional."
)

SUMMARIZE_PROMPT = """Summarize this healthcare professional (HCP) interaction.

Respond ONLY with valid JSON:
{{
  "summary": "<2-3 sentence summary>",
  "key_points": ["<point>"],
  "outcome_highlight": "<main outcome>"
}}

Doctor: {doctor_name}
Type: {interaction_type}
Date: {interaction_date}
Topics: {topics}
Sentiment: {sentiment}
Outcome: {outcome}
Samples: {samples}

Text:
{text}
"""

ENTITY_EXTRACTION_PROMPT = """Extract structured HCP interaction entities from the text.

Fields:
- doctor_name, interaction_type (in_person|phone_call|video_call|email|conference|other)
- interaction_date (YYYY-MM-DD), interaction_time (HH:MM:SS)
- topics (array), sentiment (positive|neutral|negative|mixed)
- outcome, samples, materials (array), followup_notes, followup_date (YYYY-MM-DD)

Respond ONLY with valid JSON. Use null for missing fields.

Intent: {intent}
Text:
{text}
"""

FOLLOWUP_PROMPT = """Generate follow-up recommendations for this HCP interaction.

Respond ONLY with valid JSON:
{{
  "recommendations": ["<action>"],
  "suggested_date": "YYYY-MM-DD or null",
  "priority": "high|medium|low",
  "rationale": "<brief rationale>"
}}

Doctor: {doctor_name}
Type: {interaction_type}
Date: {interaction_date}
Topics: {topics}
Sentiment: {sentiment}
Outcome: {outcome}
Samples: {samples}
"""


# -----------------------------------------------------------------------------
# Service
# -----------------------------------------------------------------------------


class GroqService:
    """Centralized Groq API service using gemma2-9b-it with structured JSON outputs."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL
        self.temperature = temperature if temperature is not None else settings.GROQ_TEMPERATURE
        self.max_tokens = max_tokens if max_tokens is not None else settings.GROQ_MAX_TOKENS

        if not self.api_key:
            logger.warning("groq_api_key_missing")

    def _build_client(self, *, temperature: float | None = None, max_tokens: int | None = None) -> ChatGroq:
        return ChatGroq(
            model=self.model,
            groq_api_key=self.api_key or None,
            temperature=temperature if temperature is not None else self.temperature,
            max_tokens=max_tokens if max_tokens is not None else self.max_tokens,
        )

    def _invoke_text(self, prompt: str, *, system_prompt: str | None = None) -> str:
        messages: list[SystemMessage | HumanMessage] = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))

        client = self._build_client()
        response = client.invoke(messages)
        content = response.content
        return content if isinstance(content, str) else str(content)

    def invoke_json(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        fallback: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Invoke Groq and parse a JSON object from the response."""
        raw = self._invoke_text(prompt, system_prompt=system_prompt)
        return safe_parse_llm_json(raw, fallback=fallback or {})

    @staticmethod
    def _serialize_entities(entities: ExtractedEntities) -> dict[str, Any]:
        data = entities.model_dump()
        for field in ("interaction_date", "followup_date"):
            if data.get(field) and isinstance(data[field], date):
                data[field] = data[field].isoformat()
        if data.get("interaction_time") and isinstance(data["interaction_time"], time):
            data["interaction_time"] = data["interaction_time"].isoformat()
        return data

    def chat(self, request: ChatRequest) -> ChatResponse:
        """Multi-turn chat completion via Groq."""
        try:
            lc_messages: list[SystemMessage | HumanMessage | AIMessage] = []
            has_system = any(m.role == "system" for m in request.messages)

            if not has_system:
                lc_messages.append(SystemMessage(content=CHAT_SYSTEM_PROMPT))

            for msg in request.messages:
                if msg.role == "system":
                    lc_messages.append(SystemMessage(content=msg.content))
                elif msg.role == "user":
                    lc_messages.append(HumanMessage(content=msg.content))
                else:
                    lc_messages.append(AIMessage(content=msg.content))

            client = self._build_client(
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
            response = client.invoke(lc_messages)
            content = response.content
            text = content if isinstance(content, str) else str(content)

            logger.info("groq_chat_success", model=self.model)
            return ChatResponse(
                success=True,
                model=self.model,
                content=text.strip(),
                message="Chat completion successful",
            )

        except Exception as exc:
            logger.error("groq_chat_failed", error=str(exc))
            return ChatResponse(
                success=False,
                model=self.model,
                content="",
                message="Chat completion failed",
                errors=[GroqServiceError(code="CHAT_FAILED", message=str(exc))],
            )

    def summarize(self, request: SummarizeRequest) -> SummarizeResponse:
        """Summarize an HCP interaction and return structured JSON."""
        try:
            prompt = SUMMARIZE_PROMPT.format(
                doctor_name=request.doctor_name or "Unknown",
                interaction_type=request.interaction_type or "unknown",
                interaction_date=request.interaction_date or "unknown",
                topics=", ".join(request.topics) if request.topics else "None",
                sentiment=request.sentiment or "unknown",
                outcome=request.outcome or "None",
                samples=request.samples or "None",
                text=request.text,
            )
            parsed = self.invoke_json(prompt, fallback={"summary": "", "key_points": [], "outcome_highlight": ""})

            response = SummarizeResponse(
                success=bool(parsed.get("summary")),
                model=self.model,
                summary=parsed.get("summary", ""),
                key_points=parsed.get("key_points", []),
                outcome_highlight=parsed.get("outcome_highlight", ""),
                message="Summarization successful" if parsed.get("summary") else "Empty summary returned",
            )

            if not response.success:
                response.errors.append(
                    GroqServiceError(code="EMPTY_SUMMARY", message="Model returned empty summary")
                )

            logger.info("groq_summarize_success", model=self.model)
            return response

        except Exception as exc:
            logger.error("groq_summarize_failed", error=str(exc))
            return SummarizeResponse(
                success=False,
                model=self.model,
                message="Summarization failed",
                errors=[GroqServiceError(code="SUMMARIZE_FAILED", message=str(exc))],
            )

    def extract_entities(self, request: EntityExtractionRequest) -> EntityExtractionResponse:
        """Extract HCP interaction entities and return structured JSON."""
        try:
            prompt = ENTITY_EXTRACTION_PROMPT.format(intent=request.intent, text=request.text)
            parsed = self.invoke_json(prompt, fallback={})

            try:
                entities = ExtractedEntities.model_validate(parsed)
                serialized = self._serialize_entities(entities)
                success = True
            except ValidationError:
                entities = ExtractedEntities()
                serialized = self._serialize_entities(entities)
                success = bool(parsed)

            logger.info("groq_entity_extraction_success", model=self.model)

            return EntityExtractionResponse(
                success=success,
                model=self.model,
                entities=serialized,
                message="Entity extraction successful",
            )

        except Exception as exc:
            logger.error("groq_entity_extraction_failed", error=str(exc))
            return EntityExtractionResponse(
                success=False,
                model=self.model,
                message="Entity extraction failed",
                errors=[GroqServiceError(code="ENTITY_EXTRACTION_FAILED", message=str(exc))],
            )

    def recommend_followup(self, request: FollowupRecommendationRequest) -> FollowupRecommendationResponse:
        """Generate follow-up recommendations and return structured JSON."""
        try:
            prompt = FOLLOWUP_PROMPT.format(
                doctor_name=request.doctor_name or "Unknown",
                interaction_type=request.interaction_type or "unknown",
                interaction_date=request.interaction_date or "unknown",
                topics=", ".join(request.topics) if request.topics else "None",
                sentiment=request.sentiment or "unknown",
                outcome=request.outcome or "None",
                samples=request.samples or "None",
            )
            parsed = self.invoke_json(
                prompt,
                fallback={
                    "recommendations": ["Schedule a follow-up call to discuss outcomes"],
                    "suggested_date": None,
                    "priority": "medium",
                    "rationale": "",
                },
            )

            try:
                result = RecommendationResult.model_validate(
                    {
                        "recommendations": parsed.get("recommendations", []),
                        "suggested_materials": [],
                        "followup_action": parsed.get("rationale"),
                    }
                )
            except ValidationError:
                result = RecommendationResult(
                    recommendations=parsed.get("recommendations", []),
                )

            logger.info("groq_followup_recommendation_success", model=self.model)

            return FollowupRecommendationResponse(
                success=True,
                model=self.model,
                recommendations=result.recommendations,
                suggested_date=parsed.get("suggested_date"),
                priority=parsed.get("priority", "medium"),
                rationale=parsed.get("rationale", ""),
                message="Follow-up recommendations generated",
            )

        except Exception as exc:
            logger.error("groq_followup_recommendation_failed", error=str(exc))
            return FollowupRecommendationResponse(
                success=False,
                model=self.model,
                message="Follow-up recommendation failed",
                errors=[GroqServiceError(code="FOLLOWUP_FAILED", message=str(exc))],
            )

    def get_langchain_client(self) -> ChatGroq:
        """Expose underlying LangChain client for advanced integrations."""
        return self._build_client()


@lru_cache
def get_groq_service() -> GroqService:
    return GroqService()


def get_llm() -> ChatGroq:
    """Backward-compatible LLM accessor."""
    return get_groq_service().get_langchain_client()
