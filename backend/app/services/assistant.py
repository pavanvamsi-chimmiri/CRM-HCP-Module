from uuid import UUID

from app.ai.agents.assistant_agent import get_form_assistant_agent
from app.models import User
from app.schemas.assistant import AssistantFormFields, AssistantParseRequest, AssistantParseResponse


class AssistantService:
    def _entities_to_form_fields(self, entities: dict) -> AssistantFormFields:
        materials = entities.get("materials") or []
        if isinstance(materials, list):
            materials_shared = ", ".join(str(m) for m in materials) if materials else None
        else:
            materials_shared = str(materials) if materials else None

        follow_up_parts: list[str] = []
        if entities.get("follow_up"):
            follow_up_parts.append(str(entities["follow_up"]))
        if entities.get("followup_notes"):
            follow_up_parts.append(str(entities["followup_notes"]))
        if entities.get("followup_date"):
            follow_up_parts.append(f"Follow up on {entities['followup_date']}")
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


assistant_service = AssistantService()
