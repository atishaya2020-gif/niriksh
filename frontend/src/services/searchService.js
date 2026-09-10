import { apiGet } from './api';

export const searchService = {
  search: async (query, limit = 20) => {
    try {
      const response = await apiGet('/search', { q: query, limit });
      const data = response.data || response;
      let results = Array.isArray(data.results) ? data.results : [];

      results = results.map((r) => ({
        entity_id: r.entity_id,
        entity_type: r.entity_type,
        label: r.label,
        risk: r.risk,
        risk_score: r.risk_score,
        case_ids: r.case_ids,
        record_count: r.record_count,
        cross_case: r.cross_case,
        type: r.entity_type,
        name: r.label,
        _raw: r
      }));

      return {
        query: data.query || query,
        results: results,
        count: data.count || results.length
      };
    } catch (error) {
      console.error('Search failed:', error);
      return {
        query: query,
        results: [],
        count: 0
      };
    }
  }
};

export default searchService;