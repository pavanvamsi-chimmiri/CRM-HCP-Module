import { apiClient } from './client';
import type { AssistantMessage, AssistantParseResponse } from '@/types/assistant';

export const assistantApi = {
  parse: async (
    message: string,
    conversationHistory: AssistantMessage[] = []
  ): Promise<AssistantParseResponse> => {
    const { data } = await apiClient.post<AssistantParseResponse>('/assistant/parse', {
      message,
      conversation_history: conversationHistory.map((m) => ({
        role: m.role,
        content: m.content,
      })),
    });
    return data;
  },
};
