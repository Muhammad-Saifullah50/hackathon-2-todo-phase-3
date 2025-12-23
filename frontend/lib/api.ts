import axios from 'axios';
import { authClient } from './auth-client';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Standard Axios client for API requests.
 * Configured with base URL and interceptors for consistent error handling and auth.
 */
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  async (config) => {
    // Add auth token if available (Feature 3)
    const { data } = await authClient.token();
    if (data?.token) {
      config.headers.Authorization = `Bearer ${data.token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Standardized error handling following ADR-0004
    const message = error.response?.data?.message || 'An unexpected error occurred';
    console.error(`[API Error] ${message}`, error);
    
    // Handle 401 Unauthorized - trigger logout if needed
    if (error.response?.status === 401) {
      console.warn('Session expired or unauthorized. Please login again.');
    }
    
    return Promise.reject(error);
  }
);

export { api };
export default api;