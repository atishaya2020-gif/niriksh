import { apiPost, apiGet } from './api';

const TOKEN_KEY = 'niriksh_auth_token';
const USER_KEY = 'niriksh_current_user';

export const authService = {
  login: async (credential, password) => {
    try {
      const response = await apiPost('/auth/login', {
        username: credential,
        password: password
      });

      const token = response.access_token;
      localStorage.setItem(TOKEN_KEY, token);

      const user = await apiGet('/auth/me');
      localStorage.setItem(USER_KEY, JSON.stringify(user));

      return { success: true, user, token };
    } catch (error) {
      return {
        success: false,
        message: error.message || 'Invalid credentials. Please try again.'
      };
    }
  },

  logout: async () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    return { success: true };
  },

  getCurrentUser: () => {
    try {
      const userStr = localStorage.getItem(USER_KEY);
      if (!userStr) return null;
      return JSON.parse(userStr);
    } catch (e) {
      return null;
    }
  },

  setCurrentUser: (user) => {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },

  isAuthenticated: () => {
    return !!localStorage.getItem(TOKEN_KEY);
  },

  getToken: () => {
    return localStorage.getItem(TOKEN_KEY);
  },

  requestAccess: async () => ({
    success: false,
    message: 'Access requests are not supported by the current backend API.'
  })
};

export default authService;
