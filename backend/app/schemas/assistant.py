from pydantic import BaseModel, Field

from app.models import InteractionType, Sentiment


class AssistantMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1)


class AssistantParseRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_history: list[AssistantMessage] = Field(default_factory=list)


class AssistantFormFields(BaseModel):
    doctor_name: str | None = None
    interaction_type: InteractionType | None = None
    interaction_date: str | None = None
    interaction_time: str | None = None
    topics: list[str] = Field(default_factory=list)
    materials_shared: str | None = None
    samples: str | None = None
    sentiment: Sentiment | None = None
    outcome: str | None = None
    follow_up: str | None = None


class AssistantParseResponse(BaseModel):
    message: str
    form_fields: AssistantFormFields
    extracted_fields: dict = Field(default_factory=dict)
    missing_fields: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)
    is_complete: bool = False


class VoiceUploadResponse(BaseModel):
    transcript: str
    summary: str
    key_points: list[str] = Field(default_factory=list)
    outcome_highlight: str = ""
    message: str
    form_fields: AssistantFormFields
    extracted_fields: dict = Field(default_factory=dict)
    missing_fields: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)
    is_complete: bool = False
