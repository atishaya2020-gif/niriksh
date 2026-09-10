export const userService = {
  getUsers: async () => {
    return [];
  },

  updateUserStatus: async (userId, status) => {
    return { success: true, message: 'User management requires backend admin API.' };
  },

  updateUserRole: async (userId, role) => {
    return { success: true, message: 'User management requires backend admin API.' };
  }
};

export default userService;