import { apiGet } from './api';
import { backendGraphToCytoscape } from '../utils/graphTransform';

export const networkService = {
  getGraph: async (caseId) => {
      if (!Number.isInteger(Number(caseId))) {
        throw { error: true, status: 400, message: 'Select a valid case before opening the network.' };
      }
      const response = await apiGet(`/network/${caseId}`);
      const data = response.data || response;
      const network = data.network || {};

      return {
        nodes: (network.nodes || []).map((n) => ({
          id: n.id,
          name: n.label || n.id,
          label: n.label || n.id,
          type: n.type || 'UNKNOWN',
          risk: n.risk || 'LOW',
          risk_score: n.risk_score || 0,
          confidence: 0.85,
          metadata: n.metadata || {},
          phone: n.metadata?.phone || null,
          location: n.metadata?.location || null,
          vehicle: n.metadata?.vehicle || null,
          account: n.metadata?.account || null,
          source: 'Graph Database',
          cases: [],
          potential_matches: []
        })),
        edges: (network.edges || []).map((e, idx) => ({
          id: e.id || `edge-${idx}`,
          source: e.source,
          target: e.target,
          type: (e.relationship_type || 'CONNECTED_TO').toUpperCase(),
          label: e.relationship_type || 'Connected',
          confidence: e.confidence || 0.85,
          evidence_id: null,
          timestamp: null,
          why_detected: e.reason || 'Connection detected in investigation network.'
        })),
        _raw: data
      };
  },

  getCytoscapeElements: async (caseId) => {
    const graphData = await networkService.getGraph(caseId);
    return backendGraphToCytoscape(graphData);
  },

  simulateDisruption: async (targetEntityId) => {
    return {
      targetEntityId,
      before: {
        totalNodes: 0,
        totalConnections: 0,
        networkDensity: 0,
        connectedComponents: 0,
        highRiskLinks: 0,
        keyHubCentrality: 0
      },
      after: {
        totalNodes: 0,
        totalConnections: 0,
        networkDensity: 0,
        connectedComponents: 0,
        highRiskLinks: 0,
        keyHubCentrality: 0
      },
      impactSummary: 'Disruption simulation requires backend analysis. Backend endpoint not yet implemented.'
    };
  }
};

export default networkService;
