import axios from 'axios';
import envConfig from '../config/env';

const TOKEN_KEY = 'niriksh_auth_token';

const apiClient = axios.create({
  baseURL: envConfig.apiBaseUrl,
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 15000
});

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem('niriksh_current_user');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const apiGet = async (url, params = {}) => {
  try {
    const response = await apiClient.get(url, { params });
    return response.data;
  } catch (error) {
    throw normalizeError(error);
  }
};

export const apiPost = async (url, data = {}, config = {}) => {
  try {
    const response = await apiClient.post(url, data, config);
    return response.data;
  } catch (error) {
    throw normalizeError(error);
  }
};

export const apiUpload = async (url, formData) => {
  try {
    const response = await apiClient.post(url, formData, {
      headers: { 'Content-Type': undefined }
    });
    return response.data;
  } catch (error) {
    throw normalizeError(error);
  }
};

export const apiPatch = async (url, data = {}) => {
  try {
    const response = await apiClient.patch(url, data);
    return response.data;
  } catch (error) {
    throw normalizeError(error);
  }
};

export const apiPut = async (url, data = {}) => {
  try {
    const response = await apiClient.put(url, data);
    return response.data;
  } catch (error) {
    throw normalizeError(error);
  }
};

export const apiDelete = async (url) => {
  try {
    const response = await apiClient.delete(url);
    return response.data;
  } catch (error) {
    throw normalizeError(error);
  }
};

export const delay = (ms = 400) => new Promise((resolve) => setTimeout(resolve, ms));

export const handleApiError = (error) => {
  console.error('API Error:', error);
  return {
    error: true,
    message: error.message || 'A network error occurred. Please try again.',
    status: error.status || 500
  };
};

function normalizeError(error) {
  if (error.response) {
    const { status, data } = error.response;
    const message = data?.detail || data?.message || data?.error || `Request failed with status ${status}`;
    return { error: true, message, status };
  }
  if (error.request) {
    return { error: true, message: 'Network error. Backend may be unavailable.', status: 0 };
  }
  return { error: true, message: error.message || 'An unexpected error occurred.', status: 500 };
}

export { apiClient };
export default apiClient;
