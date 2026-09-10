import { apiGet } from './api';

export const entityService = {
  getEntities: async (filters = {}) => {
      const params = {};
      if (filters.search) params.search = filters.search;
      if (filters.type && filters.type !== 'ALL') params.entity_type = filters.type;
      params.limit = 200;

      const response = await apiGet('/entities', params);
      let entities = Array.isArray(response) ? response : [];

      entities = entities.map((e) => ({
        id: e.id,
        name: e.label || e.id,
        type: (e.type || 'UNKNOWN').toUpperCase(),
        risk: 'LOW',
        confidence: 0.85,
        primary_case: 'N/A',
        source: 'Graph Database',
        last_seen: 'N/A',
        phone: e.properties?.phone || null,
        location: e.properties?.location || null,
        vehicle: e.properties?.vehicle || null,
        account: e.properties?.account || null,
        cases: [],
        potential_matches: [],
        _raw: e
      }));

      if (filters.risk && filters.risk !== 'ALL') {
        entities = entities.filter((e) => e.risk === filters.risk);
      }

      return entities;
  },

  getEntity: async (entityId) => {
    try {
      const decoded = decodeURIComponent(entityId);
      const response = await apiGet(`/entities/${decoded}`);
      const data = response.data || response;
      const entity = data.entity || {};
      const risk = data.risk || {};
      const cases = data.cases || {};
      const connections = data.connections || {};

      return {
        id: entity.id || decoded,
        name: entity.label || entity.id || decoded,
        type: (entity.type || 'UNKNOWN').toUpperCase(),
        risk: risk.level || 'LOW',
        confidence: risk.confidence || 0.85,
        primary_case: cases.items?.[0]?.case_number || 'N/A',
        source: 'Graph Database',
        last_seen: 'N/A',
        phone: entity.properties?.phone || null,
        location: entity.properties?.location || null,
        vehicle: entity.properties?.vehicle || null,
        account: entity.properties?.account || null,
        cases: cases.items?.map((c) => c.case_number) || [],
        potential_matches: [],
        _raw: data
      };
    } catch (error) {
      console.error('Failed to fetch entity:', error);
      throw error;
    }
  },

  getConnections: async (entityId) => {
      const decoded = decodeURIComponent(entityId);
      const response = await apiGet(`/entities/${decoded}/connections`);
      const connections = Array.isArray(response) ? response : [];

      return connections.map((conn, idx) => ({
        id: `rel-${decoded}-${idx}`,
        source: decoded,
        target: conn.id || '',
        type: (conn.relationship_type || 'CONNECTED_TO').toUpperCase(),
        label: conn.relationship_type || 'Connected',
        confidence: 0.85,
        evidence_id: null,
        timestamp: null,
        why_detected: 'Connection detected in investigation graph.',
        _raw: conn
      }));
  },

  confirmMatch: async (entityId, matchId) => {
    const { apiPatch } = await import('./api');
    await apiPatch(`/matches/${matchId}/review`, { status: 'CONFIRMED' });
    return {
      success: true,
      message: 'Potential entity match confirmed by investigator. Unification registered in audit trail.'
    };
  },

  rejectMatch: async (entityId, matchId) => {
    const { apiPatch } = await import('./api');
    await apiPatch(`/matches/${matchId}/review`, { status: 'REJECTED' });
    return {
      success: true,
      message: 'Entity match candidate rejected. Entity records maintained separately.'
    };
  }
};

export default entityService;
