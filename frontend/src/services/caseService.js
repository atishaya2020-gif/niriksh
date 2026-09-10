import { apiGet, apiPost } from './api';

const mapCase = (caseData) => ({
  id: caseData.id,
  case_number: caseData.case_number,
  title: caseData.title,
  description: caseData.description || '',
  created_at: caseData.created_at,
  last_updated: caseData.created_at ? new Date(caseData.created_at).toLocaleDateString() : 'Unavailable'
});

export const caseService = {
  getCases: async (filters = {}) => {
    const response = await apiGet('/cases');
    let cases = (Array.isArray(response) ? response : []).map(mapCase);

    if (filters.search) {
      const q = filters.search.toLowerCase();
      cases = cases.filter(
        (c) =>
          c.case_number.toLowerCase().includes(q) ||
          c.title.toLowerCase().includes(q) ||
          c.description.toLowerCase().includes(q)
      );
    }

    return cases;
  },

  getCase: async (caseId) => {
    const response = await apiGet(`/cases/${caseId}/overview`);
    const overview = response.data || response;
    const caseInfo = overview.case || {};
    const metrics = overview.metrics || {};
    const investigation = overview.investigation || {};

    return {
      ...mapCase(caseInfo),
      risk: investigation.risk_level || null,
      status: investigation.status || null,
      entities_count: metrics.entities ?? 0,
      relationships_count: metrics.relationships ?? 0,
      evidence_count: null,
      alerts_count: metrics.active_alerts ?? 0,
      key_entities: overview.key_entities || [],
      alerts: overview.alerts || [],
      analysis_note: overview.analysis_note || null,
      _raw: overview
    };
  },

  getTimeline: async (caseId, params = {}) => {
    return apiGet(`/cases/${caseId}/timeline`, params);
  },

  createCase: async (caseData) => {
    const response = await apiPost('/cases', {
      case_number: caseData.case_number,
      title: caseData.title,
      description: caseData.description || null
    });
    return mapCase(response);
  }
};

export default caseService;
