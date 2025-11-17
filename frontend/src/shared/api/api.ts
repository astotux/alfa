import axios, { type CreateAxiosDefaults } from 'axios';

import {
  getAccessToken,
  getRefreshToken,
  removeTokenFromStorage,
  saveTokenStorage,
} from './services/auth/token.service';
import { ROUTES } from '../config/routes';
import { API_URL } from '../config/api-url';
import type { LoginResponse } from '../types/auth.type';

const options: CreateAxiosDefaults = {
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
};

export const axiosClassic = axios.create(options);
export const axiosWithAuth = axios.create(options);

axiosWithAuth.interceptors.request.use((config) => {
  const accessToken = getAccessToken();

  if (config?.headers && accessToken)
    config.headers.Authorization = `Bearer ${accessToken}`;

  return config;
});

axiosWithAuth.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error?.response?.status === 401 && !originalRequest._isRetry) {
      originalRequest._isRetry = true;

      const refreshToken = getRefreshToken();

      if (!refreshToken) {
        removeTokenFromStorage();
        window.location.href = ROUTES.LOGIN;
      }

      try {
        const response = await axios.post<LoginResponse>(
          import.meta.env.VITE_API_URL + API_URL.auth.refreshTokens(),
          {},
          {
            headers: {
              Authorization: `Bearer ${refreshToken}`,
            },
            withCredentials: true,
          }
        );

        const { access_token, refresh_token } = response.data;

        saveTokenStorage(access_token, refresh_token);

        return axiosWithAuth.request(originalRequest);
      } catch (error) {
        removeTokenFromStorage();
        window.location.href = ROUTES.LOGIN;
      }
    }

    throw error;
  }
);
