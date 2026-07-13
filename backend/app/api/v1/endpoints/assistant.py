from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.schemas.assistant import AssistantParseRequest, AssistantParseResponse
from app.services.assistant import assistant_service

router = APIRouter(prefix="/assistant", tags=["AI Assistant"])


@router.post("/parse", response_model=AssistantParseResponse)
async def parse_assistant_message(
    current_user: CurrentUser,
    body: AssistantParseRequest,
) -> AssistantParseResponse:
    """Parse natural-language interaction notes and return form field extractions."""
    return await assistant_service.parse_message(request=body, owner=current_user)
