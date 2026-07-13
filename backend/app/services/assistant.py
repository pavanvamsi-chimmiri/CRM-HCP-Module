from uuid import UUID

from fastapi import HTTPException, status

from app.ai.agents.assistant_agent import get_form_assistant_agent
from app.ai.groq_service import SummarizeRequest, get_groq_service
from app.ai.whisper_service import ALLOWED_AUDIO_TYPES, MAX_AUDIO_BYTES, get_whisper_service
from app.models import User
from app.schemas.assistant import (
    AssistantFormFields,
    AssistantParseRequest,
    AssistantParseResponse,
    VoiceUploadResponse,
)


class AssistantService:
    def _entities_to_form_fields(self, entities: dict) -> AssistantFormFields:
        materials = entities.get("materials") or []
        if isinstance(materials, list):
            materials_shared = ", ".join(str(m) for m in materials) if materials else None
        else:
            materials_shared = str(materials) if materials else None

        follow_up_parts: list[str] = []
        follow_up_value = entities.get("follow_up")
        followup_notes = entities.get("followup_notes")
        followup_date = entities.get("followup_date")

        if follow_up_value:
            follow_up_parts.append(str(follow_up_value))
        elif followup_notes:
            follow_up_parts.append(str(followup_notes))

        if followup_date:
            follow_up_parts.append(f"Follow up on {followup_date}")

        follow_up = ". ".join(follow_up_parts) if follow_up_parts else None

        interaction_time = entities.get("interaction_time")
        if interaction_time and len(str(interaction_time)) >= 5:
            interaction_time = str(interaction_time)[:5]

        return AssistantFormFields(
            doctor_name=entities.get("doctor_name"),
            interaction_type=entities.get("interaction_type"),
            interaction_date=entities.get("interaction_date"),
            interaction_time=interaction_time,
            topics=entities.get("topics") or [],
            materials_shared=materials_shared or entities.get("materials_shared"),
            samples=entities.get("samples"),
            sentiment=entities.get("sentiment"),
            outcome=entities.get("outcome"),
            follow_up=follow_up,
        )

    async def parse_message(
        self,
        *,
        request: AssistantParseRequest,
        owner: User,
    ) -> AssistantParseResponse:
        agent = get_form_assistant_agent()
        history = [msg.model_dump() for msg in request.conversation_history]

        result = await agent.run(
            message=request.message,
            owner_id=UUID(str(owner.id)),
            conversation_history=history,
        )

        entities = result.get("entities", {})
        missing_fields = result.get("missing_fields", [])
        follow_up_questions = result.get("follow_up_questions", [])
        form_fields = self._entities_to_form_fields(entities)

        is_complete = len(missing_fields) == 0 and bool(form_fields.doctor_name)

        return AssistantParseResponse(
            message=result.get("response", "I've updated the form with what I could extract."),
            form_fields=form_fields,
            extracted_fields=entities,
            missing_fields=missing_fields,
            follow_up_questions=follow_up_questions,
            is_complete=is_complete and bool(form_fields.doctor_name),
        )

    async def process_voice_upload(
        self,
        *,
        audio_bytes: bytes,
        filename: str,
        content_type: str,
        owner: User,
    ) -> VoiceUploadResponse:
        if len(audio_bytes) > MAX_AUDIO_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Audio file exceeds 25 MB limit",
            )

        if content_type not in ALLOWED_AUDIO_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Unsupported audio format. Allowed: mp3, wav, m4a, webm, ogg",
            )

        whisper = get_whisper_service()
        transcription = await whisper.transcribe(
            audio_bytes=audio_bytes,
            filename=filename,
            content_type=content_type,
        )

        if not transcription.success or not transcription.text:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=transcription.message or "Failed to transcribe audio",
            )

        transcript = transcription.text

        groq = get_groq_service()
        summary_result = groq.summarize(
            SummarizeRequest(text=transcript),
        )

        summary = summary_result.summary if summary_result.success else transcript
        key_points = summary_result.key_points
        outcome_highlight = summary_result.outcome_highlight

        agent = get_form_assistant_agent()
        result = await agent.run(
            message=transcript,
            owner_id=UUID(str(owner.id)),
            conversation_history=[],
        )

        entities = result.get("entities", {})
        missing_fields = result.get("missing_fields", [])
        follow_up_questions = result.get("follow_up_questions", [])
        form_fields = self._entities_to_form_fields(entities)

        if outcome_highlight and not form_fields.outcome:
            form_fields.outcome = outcome_highlight
        if key_points and not form_fields.topics:
            form_fields.topics = key_points

        is_complete = len(missing_fields) == 0 and bool(form_fields.doctor_name)

        message_parts = [
            "I've transcribed your voice note and filled in the form.",
            f"Summary: {summary}" if summary else "",
        ]
        if follow_up_questions:
            message_parts.append(follow_up_questions[0])

        return VoiceUploadResponse(
            transcript=transcript,
            summary=summary,
            key_points=key_points,
            outcome_highlight=outcome_highlight,
            message=" ".join(part for part in message_parts if part),
            form_fields=form_fields,
            extracted_fields=entities,
            missing_fields=missing_fields,
            follow_up_questions=follow_up_questions,
            is_complete=is_complete and bool(form_fields.doctor_name),
        )


assistant_service = AssistantService()
