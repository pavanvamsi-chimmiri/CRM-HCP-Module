import { apiClient } from './client';
import type { AuthTokens, LoginCredentials, User } from '@/types';

export const authApi = {
  login: async (credentials: LoginCredentials): Promise<AuthTokens> => {
    const { data } = await apiClient.post<AuthTokens>('/auth/login/json', credentials);
    return data;
  },

  register: async (payload: {
    email: string;
    password: string;
    full_name: string;
  }): Promise<User> => {
    const { data } = await apiClient.post<User>('/auth/register', payload);
    return data;
  },

  getMe: async (): Promise<User> => {
    const { data } = await apiClient.get<User>('/auth/me');
    return data;
  },
};
