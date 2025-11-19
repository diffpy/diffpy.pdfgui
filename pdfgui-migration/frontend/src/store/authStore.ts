/**
 * Authentication state store using Zustand.
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authApi } from '../services/api';

interface User {
  id: string;
  email: string;
  first_name?: string;
  last_name?: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, firstName?: string, lastName?: string) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authApi.login({ email, password });
          const { access_token, refresh_token } = response.data;

          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);

          // For now, we'll just store the email
          // In production, you'd decode the JWT or fetch user profile
          set({
            user: { id: '', email },
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error: any) {
          set({
            error: error.response?.data?.detail || 'Login failed',
            isLoading: false,
          });
          throw error;
        }
      },

      register: async (email: string, password: string, firstName?: string, lastName?: string) => {
        set({ isLoading: true, error: null });
        try {
          await authApi.register({
            email,
            password,
            first_name: firstName,
            last_name: lastName,
          });
          set({ isLoading: false });
        } catch (error: any) {
          set({
            error: error.response?.data?.detail || 'Registration failed',
            isLoading: false,
          });
          throw error;
        }
      },

      logout: async () => {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          try {
            await authApi.logout(refreshToken);
          } catch {
            // Ignore errors on logout
          }
        }

        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');

        set({
          user: null,
          isAuthenticated: false,
        });
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
