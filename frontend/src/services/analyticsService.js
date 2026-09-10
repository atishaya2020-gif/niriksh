import { apiGet } from './api';

export const analyticsService = {
  getAnalytics: async () => {
    const responses = await Promise.allSettled([
      apiGet('/analytics/key-people'),
      apiGet('/analytics/communities'),
      apiGet('/analytics/hidden-links'),
      apiGet('/analytics/suspicious-patterns'),
      apiGet('/analytics/cross-case-links')
    ]);

    const labels = ['keyPeople', 'communities', 'hiddenLinks', 'suspiciousPatterns', 'crossCaseLinks'];
    return responses.reduce((analytics, result, index) => {
      analytics[labels[index]] = result.status === 'fulfilled' ? result.value : null;
      analytics.errors[labels[index]] = result.status === 'rejected' ? result.reason : null;
      return analytics;
    }, { errors: {} });
  },

  getSystemAnalytics: async () => {
    return analyticsService.getAnalytics();
  }
};

export default analyticsService;
