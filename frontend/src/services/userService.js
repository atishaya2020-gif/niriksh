import {
  apiGet,
  apiPatch
} from './api';

const mapUser = (
  user
) => ({

  id:
    user.id,

  name:
    user.username,

  employee_id:
    `EMP-${String(
      user.id
    ).padStart(3, '0')}`,

  department:
    user.department ||
    'Investigation Unit',

  role:
    String(
      user.role ||
      'investigator'
    ).toUpperCase(),

  state:
    user.state ||
    'NATIONAL',

  status:
    user.is_active
      ? 'ACTIVE'
      : 'SUSPENDED',

  last_active:
    user.created_at
      ? new Date(
          user.created_at
        ).toLocaleDateString()
      : 'N/A'
});

export const userService = {

  getUsers:
    async () => {

      const response =
        await apiGet(
          '/admin/users'
        );

      const users =
        response?.data?.users ||
        response?.users ||
        [];

      return users.map(
        mapUser
      );
    },

  updateUserStatus:
    async (
      userId,
      status
    ) => {

      return apiPatch(
        `/admin/users/${userId}/status`,
        {
          status
        }
      );
    },

  updateUserRole:
    async (
      userId,
      role
    ) => {

      return apiPatch(
        `/admin/users/${userId}/role`,
        {
          role
        }
      );
    }
};

export default userService;