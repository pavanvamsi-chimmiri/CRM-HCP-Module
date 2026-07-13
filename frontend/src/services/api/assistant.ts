import { apiClient } from './client';
import type { AssistantMessage, AssistantParseResponse, VoiceUploadResponse } from '@/types/assistant';

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

  uploadVoice: async (file: File): Promise<VoiceUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const { data } = await apiClient.post<VoiceUploadResponse>('/assistant/voice', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },
};
