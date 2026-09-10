import {
  apiPost,
  apiGet
} from './api';

const TOKEN_KEY =
  'niriksh_auth_token';

const USER_KEY =
  'niriksh_current_user';

export const authService = {

  login:
    async (
      credential,
      password
    ) => {

      try {

        const response =
          await apiPost(
            '/auth/login',
            {
              username:
                credential,

              password
            }
          );

        const token =
          response.access_token;

        localStorage.setItem(
          TOKEN_KEY,
          token
        );

        const user =
          await apiGet(
            '/auth/me'
          );

        localStorage.setItem(
          USER_KEY,
          JSON.stringify(user)
        );

        return {
          success: true,
          user,
          token
        };

      } catch (error) {

        return {
          success: false,

          message:
            error.message ||
            'Invalid credentials.'
        };
      }
    },

  logout:
    async () => {

      localStorage.removeItem(
        TOKEN_KEY
      );

      localStorage.removeItem(
        USER_KEY
      );

      return {
        success: true
      };
    },

  getCurrentUser:
    () => {

      try {

        const value =
          localStorage.getItem(
            USER_KEY
          );

        return value
          ? JSON.parse(value)
          : null;

      } catch {

        return null;
      }
    },

  setCurrentUser:
    (user) => {

      localStorage.setItem(
        USER_KEY,
        JSON.stringify(user)
      );
    },

  isAuthenticated:
    () =>
      Boolean(
        localStorage.getItem(
          TOKEN_KEY
        )
      ),

  getToken:
    () =>
      localStorage.getItem(
        TOKEN_KEY
      ),

  requestAccess:
    async (
      payload
    ) => {

      try {

        const response =
          await apiPost(
            '/access/request',
            payload
          );

        return {
          success:
            response?.success !==
            false,

          data:
            response?.data,

          message:
            response?.message ||
            'Access request submitted.'
        };

      } catch (error) {

        return {
          success: false,

          message:
            error.message ||
            'Unable to submit access request.'
        };
      }
    }
};

export default authService;