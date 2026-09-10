export const notificationService = {
  getNotifications: async () => {
    return [];
  },

  markAsRead: async (id) => {
    return { success: true };
  },

  markAllAsRead: async () => {
    return { success: true };
  }
};

export default notificationService;