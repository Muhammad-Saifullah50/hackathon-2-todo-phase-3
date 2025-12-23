/**
 * API client instance for making HTTP requests.
 * Used across different API modules.
 */

import axios from 'axios';
import { authClient } from './auth-client';

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for Better Auth cookies
});

// Add request interceptor for authentication
apiClient.interceptors.request.use(
  async (config) => {
    // Get JWT token from Better Auth
    if (typeof window !== 'undefined') {
      try {
        const { data, error } = await authClient.token();
        if (data?.token && !error) {
          config.headers.Authorization = `Bearer ${data.token}`;
        }
      } catch (error) {
        console.error('Failed to get JWT token:', error);
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - redirect to login
      if (typeof window !== 'undefined' && !window.location.pathname.includes('/sign-in')) {
        window.location.href = '/sign-in';
      }
    }
    return Promise.reject(error);
  }
);
