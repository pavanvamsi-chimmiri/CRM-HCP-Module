import { apiClient } from './client';
import type {
  Interaction,
  InteractionCreate,
  InteractionStats,
  InteractionSummarizeResponse,
  InteractionType,
  InteractionUpdate,
  PaginatedResponse,
  Sentiment,
} from '@/types';

export interface InteractionFilters {
  skip?: number;
  limit?: number;
  doctor_name?: string;
  interaction_type?: InteractionType;
  sentiment?: Sentiment;
  from_date?: string;
  to_date?: string;
}

export const interactionsApi = {
  getStats: async (): Promise<InteractionStats> => {
    const { data } = await apiClient.get<InteractionStats>('/interactions/stats');
    return data;
  },

  list: async (filters: InteractionFilters = {}): Promise<PaginatedResponse<Interaction>> => {
    const { data } = await apiClient.get<PaginatedResponse<Interaction>>('/interactions', {
      params: filters,
    });
    return data;
  },

  create: async (payload: InteractionCreate): Promise<Interaction> => {
    const { data } = await apiClient.post<Interaction>('/interactions', payload);
    return data;
  },

  get: async (id: string): Promise<Interaction> => {
    const { data } = await apiClient.get<Interaction>(`/interactions/${id}`);
    return data;
  },

  update: async (id: string, payload: InteractionUpdate): Promise<Interaction> => {
    const { data } = await apiClient.patch<Interaction>(`/interactions/${id}`, payload);
    return data;
  },

  summarize: async (text: string, doctorName?: string): Promise<InteractionSummarizeResponse> => {
    const { data } = await apiClient.post<InteractionSummarizeResponse>('/interactions/summarize', {
      text,
      doctor_name: doctorName,
    });
    return data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/interactions/${id}`);
  },
};
