import AsyncStorage from '@react-native-async-storage/async-storage';
import { create } from 'zustand';

const TOKEN_KEY = '@finance_token';

interface AuthState {
  token: string | null;
  isLoading: boolean;
  setToken: (token: string) => Promise<void>;
  clearToken: () => Promise<void>;
  loadToken: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  isLoading: true,

  setToken: async (token) => {
    await AsyncStorage.setItem(TOKEN_KEY, token);
    set({ token });
  },

  clearToken: async () => {
    await AsyncStorage.removeItem(TOKEN_KEY);
    set({ token: null });
  },

  loadToken: async () => {
    const token = await AsyncStorage.getItem(TOKEN_KEY);
    set({ token, isLoading: false });
  },
}));
