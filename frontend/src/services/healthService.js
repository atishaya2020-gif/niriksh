import { apiGet } from './api';

export const healthService = {
  checkHealth: async () => {
    try {
      const response = await apiGet('/health');
      return {
        status: response.status === 'ok' ? 'ONLINE' : 'ERROR',
        mode: 'BACKEND_INTEGRATED',
        version: '2.0.0-Integrated',
        backend: response.service || 'niriksh-backend',
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      return {
        status: 'OFFLINE',
        mode: 'BACKEND_UNAVAILABLE',
        version: '2.0.0-Integrated',
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }
};

export default healthService;