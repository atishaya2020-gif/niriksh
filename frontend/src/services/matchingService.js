import { apiGet, apiPatch, apiPost } from './api';

export const matchingService = {
  getMatches: async (filters = {}) => {
    const params = {};
    if (filters.case_id) params.case_id = filters.case_id;
    if (filters.status && filters.status !== 'ALL') params.status = filters.status;
    params.page = filters.page || 1;
    params.page_size = filters.page_size || 50;

    const response = await apiGet('/matches', params);
    const items = response.items || (Array.isArray(response) ? response : []);

    return {
      items: items.map(mapMatch),
      total: response.total || items.length,
      page: response.page || 1,
      page_size: response.page_size || 50
    };
  },

  getMatch: async (matchId) => {
    try {
      const response = await apiGet(`/matches/${matchId}`);
      return mapMatch(response);
    } catch (error) {
      console.error('Failed to fetch match:', error);
      throw error;
    }
  },

  reviewMatch: async (matchId, status) => {
    const response = await apiPatch(`/matches/${matchId}/review`, { status });
    return { success: true, data: mapMatch(response.data || response) };
  },

  generateMatches: async (caseId) => {
    try {
      const response = await apiPost(`/matches/cases/${caseId}/generate`);
      const data = response.data || response;
      return {
        success: true,
        generated_count: data.generated_count || 0,
        matches: (data.matches || []).map(mapMatch)
      };
    } catch (error) {
      console.error('Failed to generate matches:', error);
      throw error;
    }
  }
};

function mapMatch(m) {
  return {
    id: m.id,
    case_id: m.case_id,
    source_entity_id: m.source_entity_id,
    candidate_entity_id: m.candidate_entity_id,
    source_entity_type: m.source_entity_type,
    candidate_entity_type: m.candidate_entity_type,
    match_score: m.match_score || 0,
    confidence: m.confidence || 0,
    matching_factors: m.matching_factors || {},
    status: m.status || 'PENDING_REVIEW',
    reviewed_by: m.reviewed_by,
    reviewed_at: m.reviewed_at,
    created_at: m.created_at,
    updated_at: m.updated_at,
    _raw: m
  };
}

export default matchingService;