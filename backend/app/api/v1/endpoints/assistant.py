from fastapi import APIRouter, File, UploadFile

from app.api.deps import CurrentUser
from app.schemas.assistant import AssistantParseRequest, AssistantParseResponse, VoiceUploadResponse
from app.services.assistant import assistant_service

router = APIRouter(prefix="/assistant", tags=["AI Assistant"])


@router.post("/parse", response_model=AssistantParseResponse)
async def parse_assistant_message(
    current_user: CurrentUser,
    body: AssistantParseRequest,
) -> AssistantParseResponse:
    """Parse natural-language interaction notes and return form field extractions."""
    return await assistant_service.parse_message(request=body, owner=current_user)


@router.post("/voice", response_model=VoiceUploadResponse)
async def upload_voice_note(
    current_user: CurrentUser,
    file: UploadFile = File(...),
) -> VoiceUploadResponse:
    """
    Upload audio, transcribe with Groq Whisper, summarize, extract fields,
    and return structured form data.
    """
    content_type = file.content_type or "application/octet-stream"
    audio_bytes = await file.read()

    return await assistant_service.process_voice_upload(
        audio_bytes=audio_bytes,
        filename=file.filename or "recording.webm",
        content_type=content_type,
        owner=current_user,
    )
