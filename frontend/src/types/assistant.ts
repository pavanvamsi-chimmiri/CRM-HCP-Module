import type { InteractionType, Sentiment } from './index';

export interface AssistantMessage {
  role: 'user' | 'assistant';
  content: string;
  extractedFields?: AssistantFormFields;
  missingFields?: string[];
  followUpQuestions?: string[];
}

export interface AssistantFormFields {
  doctor_name?: string | null;
  interaction_type?: InteractionType | null;
  interaction_date?: string | null;
  interaction_time?: string | null;
  topics?: string[];
  materials_shared?: string | null;
  samples?: string | null;
  sentiment?: Sentiment | null;
  outcome?: string | null;
  follow_up?: string | null;
}

export interface AssistantParseResponse {
  message: string;
  form_fields: AssistantFormFields;
  extracted_fields: Record<string, unknown>;
  missing_fields: string[];
  follow_up_questions: string[];
  is_complete: boolean;
}
