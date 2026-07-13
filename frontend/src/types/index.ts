export type InteractionType =
  | 'in_person'
  | 'phone_call'
  | 'video_call'
  | 'email'
  | 'conference'
  | 'other';

export type Sentiment = 'positive' | 'neutral' | 'negative' | 'mixed';

export interface Interaction {
  id: string;
  hcp_id: string;
  doctor_name: string;
  interaction_type: InteractionType;
  interaction_date: string;
  interaction_time: string;
  topics: string[];
  sentiment: Sentiment | null;
  outcome: string | null;
  samples: string | null;
  owner_id: string;
  created_at: string;
  updated_at: string;
}

export interface InteractionCreate {
  doctor_name: string;
  interaction_type: InteractionType;
  interaction_date: string;
  interaction_time: string;
  topics: string[];
  sentiment?: Sentiment | null;
  outcome?: string | null;
  samples?: string | null;
}

export interface InteractionStats {
  total_interactions: number;
  positive_sentiment: number;
  pending_followups: number;
  this_month: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface ApiError {
  detail: string | { msg: string }[];
}
