import { apiGet } from './api';

export const dashboardService = {
  getStats: async () => {
    const response = await apiGet('/dashboard');
    const metrics = response.data?.metrics || {};

    return {
      activeCases: metrics.active_cases ?? 0,
      totalCases: metrics.total_cases ?? 0,
      totalRecords: metrics.total_records ?? 0,
      totalEntities: metrics.total_entities ?? 0,
      detectedRelationships: metrics.detected_relationships ?? 0,
      highRiskEntities: metrics.high_risk_entities ?? 0,
      activeAlerts: metrics.active_alerts ?? 0,
      riskDistribution: [],
      investigationStatus: [],
      entityDistribution: [],
      alertsOverTime: [],
      riskNote: response.data?.risk_note || null
    };
  },

  getRecentInvestigations: async () => {
    const response = await apiGet('/cases');
    return (Array.isArray(response) ? response : []).slice(0, 10).map((caseData) => ({
      id: caseData.id,
      case_number: caseData.case_number,
      title: caseData.title,
      description: caseData.description || '',
      created_at: caseData.created_at,
      last_updated: caseData.created_at ? new Date(caseData.created_at).toLocaleDateString() : 'Unavailable'
    }));
  },

  getRecentConnections: async () => []
};

export default dashboardService;
