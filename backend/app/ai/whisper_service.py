from functools import lru_cache

import httpx
from pydantic import BaseModel

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

GROQ_TRANSCRIPTION_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
MAX_AUDIO_BYTES = 25 * 1024 * 1024  # 25 MB Groq limit

ALLOWED_AUDIO_TYPES = {
    "audio/mpeg",
    "audio/mp3",
    "audio/wav",
    "audio/x-wav",
    "audio/webm",
    "audio/ogg",
    "audio/mp4",
    "audio/x-m4a",
    "audio/m4a",
}


class TranscriptionResult(BaseModel):
    success: bool
    text: str = ""
    model: str = ""
    message: str = ""


class WhisperService:
    """Groq Whisper speech-to-text transcription."""

    def __init__(self, *, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key if api_key is not None else settings.GROQ_API_KEY
        self.model = model or settings.GROQ_WHISPER_MODEL

    async def transcribe(
        self,
        *,
        audio_bytes: bytes,
        filename: str,
        content_type: str,
    ) -> TranscriptionResult:
        if not self.api_key:
            return TranscriptionResult(
                success=False,
                message="GROQ_API_KEY is not configured",
            )

        if len(audio_bytes) > MAX_AUDIO_BYTES:
            return TranscriptionResult(
                success=False,
                message="Audio file exceeds 25 MB limit",
            )

        if content_type not in ALLOWED_AUDIO_TYPES:
            return TranscriptionResult(
                success=False,
                message=f"Unsupported audio type: {content_type}",
            )

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    GROQ_TRANSCRIPTION_URL,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    files={"file": (filename, audio_bytes, content_type)},
                    data={
                        "model": self.model,
                        "language": "en",
                        "response_format": "json",
                        "temperature": "0",
                    },
                )

            if response.status_code != 200:
                logger.error(
                    "whisper_transcription_failed",
                    status=response.status_code,
                    body=response.text[:500],
                )
                return TranscriptionResult(
                    success=False,
                    message=f"Transcription failed: {response.text[:200]}",
                )

            payload = response.json()
            text = payload.get("text", "").strip()

            logger.info("whisper_transcription_success", model=self.model, length=len(text))
            return TranscriptionResult(
                success=True,
                text=text,
                model=self.model,
                message="Transcription successful",
            )

        except Exception as exc:
            logger.error("whisper_transcription_error", error=str(exc))
            return TranscriptionResult(
                success=False,
                message=f"Transcription error: {exc}",
            )


@lru_cache
def get_whisper_service() -> WhisperService:
    return WhisperService()
