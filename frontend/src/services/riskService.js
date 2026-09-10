import { apiGet } from './api';

export const riskService = {
  calculateEntityRisk: async (entityId) => {
    try {
      const decoded = decodeURIComponent(entityId);
      const response = await apiGet(`/entities/${decoded}`);
      const data = response.data || response;
      const risk = data.risk || {};

      return {
        entityId: decoded,
        score: risk.score || 0,
        level: risk.level || 'LOW',
        factors: risk.supporting_signals || risk.reasons || [
          { factor: 'Network Analysis', weight: '100%', score: risk.score || 0 }
        ],
        _raw: risk
      };
    } catch (error) {
      console.error('Risk calculation failed:', error);
      return {
        entityId,
        score: 0,
        level: 'LOW',
        factors: [{ factor: 'Error in risk calculation', weight: '100%', score: 0 }]
      };
    }
  }
};

export default riskService;