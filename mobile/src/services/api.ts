import axios from 'axios';
import { useAuthStore } from '../store/authStore';
import { Asset, AuthTokens, Highlight, PriceHistoryPoint, Quote, User } from '../types';

/**
 * Para iOS Simulator: localhost funciona diretamente.
 * Para dispositivo físico: substitua localhost pelo IP da sua máquina.
 * Ex: http://192.168.1.100:8000/api/v1
 */
const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

// Injeta o token Bearer em todas as requisições autenticadas
apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ── Auth ──────────────────────────────────────────────────────────────────────

export const authApi = {
  register: (email: string, password: string) =>
    apiClient.post<User>('/auth/register', { email, password }),

  login: (email: string, password: string) =>
    apiClient.post<AuthTokens>('/auth/login', { email, password }),
};

// ── Assets ────────────────────────────────────────────────────────────────────

export const assetsApi = {
  list: () => apiClient.get<Asset[]>('/assets'),

  getById: (id: number) => apiClient.get<Asset>(`/assets/${id}`),

  create: (symbol: string, name: string) =>
    apiClient.post<Asset>('/assets', { symbol, name }),

  update: (id: number, data: Partial<Pick<Asset, 'symbol' | 'name'>>) =>
    apiClient.put<Asset>(`/assets/${id}`, data),

  remove: (id: number) => apiClient.delete(`/assets/${id}`),
};

// ── Quotes ────────────────────────────────────────────────────────────────────

export const quotesApi = {
  getQuote: (symbol: string) =>
    apiClient.get<Quote>(`/quotes/${symbol}`),

  getHighlight: () =>
    apiClient.get<Highlight>('/quotes/highlight'),

  getHistory: (symbol: string) =>
    apiClient.get<PriceHistoryPoint[]>(`/quotes/${symbol}/history`),
};
