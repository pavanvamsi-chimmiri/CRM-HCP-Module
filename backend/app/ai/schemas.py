"""Pydantic schemas for structured LLM outputs."""

from datetime import date, time

from pydantic import BaseModel, Field

from app.models import InteractionType, Sentiment


class IntentResult(BaseModel):
    intent: str = Field(
        description="Detected intent: log_interaction, query_interaction, summarize_interaction, edit_interaction, schedule_followup, general"
    )
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str = ""


class ExtractedEntities(BaseModel):
    doctor_name: str | None = None
    interaction_type: InteractionType | None = None
    interaction_date: date | None = None
    interaction_time: time | None = None
    topics: list[str] = Field(default_factory=list)
    sentiment: Sentiment | None = None
    outcome: str | None = None
    samples: str | None = None
    materials: list[str] = Field(default_factory=list)
    followup_notes: str | None = None
    followup_date: date | None = None


class ValidationResult(BaseModel):
    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class RecommendationResult(BaseModel):
    recommendations: list[str] = Field(default_factory=list)
    suggested_materials: list[str] = Field(default_factory=list)
    followup_action: str | None = None
