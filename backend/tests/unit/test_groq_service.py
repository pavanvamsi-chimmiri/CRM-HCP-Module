from app.ai.groq_service import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    EntityExtractionRequest,
    EntityExtractionResponse,
    FollowupRecommendationRequest,
    FollowupRecommendationResponse,
    GroqService,
    SummarizeRequest,
    SummarizeResponse,
)


def test_groq_service_uses_env_defaults() -> None:
    service = GroqService()
    assert service.model == "gemma2-9b-it"


def test_chat_request_schema() -> None:
    req = ChatRequest(messages=[ChatMessage(role="user", content="Hello")])
    assert req.messages[0].content == "Hello"


def test_chat_response_json() -> None:
    resp = ChatResponse(success=True, model="gemma2-9b-it", content="Hi")
    payload = resp.model_dump()
    assert payload["success"] is True
    assert payload["content"] == "Hi"
    assert resp.to_json().startswith("{")


def test_summarize_response_json() -> None:
    resp = SummarizeResponse(
        success=True,
        model="gemma2-9b-it",
        summary="Visit went well",
        key_points=["Discussed protocol"],
        outcome_highlight="Positive reception",
    )
    data = resp.model_dump()
    assert data["summary"] == "Visit went well"
    assert "key_points" in data


def test_entity_extraction_response_json() -> None:
    resp = EntityExtractionResponse(
        success=True,
        model="gemma2-9b-it",
        entities={"doctor_name": "Dr. Smith"},
    )
    assert resp.entities["doctor_name"] == "Dr. Smith"
    assert resp.to_json()


def test_followup_recommendation_response_json() -> None:
    resp = FollowupRecommendationResponse(
        success=True,
        model="gemma2-9b-it",
        recommendations=["Call in 2 weeks"],
        priority="high",
    )
    data = resp.model_dump()
    assert data["priority"] == "high"
    assert len(data["recommendations"]) == 1


def test_summarize_request_schema() -> None:
    req = SummarizeRequest(text="Doctor visit notes here")
    assert req.text == "Doctor visit notes here"


def test_entity_extraction_request_schema() -> None:
    req = EntityExtractionRequest(text="Met Dr. Lee today", intent="log_interaction")
    assert req.intent == "log_interaction"


def test_followup_recommendation_request_schema() -> None:
    req = FollowupRecommendationRequest(doctor_name="Dr. Lee", topics=["efficacy"])
    assert req.doctor_name == "Dr. Lee"
    assert req.topics == ["efficacy"]
