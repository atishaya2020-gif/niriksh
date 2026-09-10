import { apiGet, apiPost, apiPatch } from './api';

export const evidenceService = {
  getEvidenceList: async (caseId) => {
    if (!caseId) {
      throw { error: true, status: 400, message: 'Select a case to load evidence.' };
    }
    const response = await apiGet(`/evidence/cases/${caseId}/evidence`);
    const items = response.items || (Array.isArray(response) ? response : []);
    return items.map(mapEvidence);
  },

  addEvidence: async (data) => {
    if (!data.case_id) {
      throw { error: true, status: 400, message: 'A backend case ID is required to create evidence.' };
    }
    const response = await apiPost(`/evidence/cases/${data.case_id}/evidence`, {
      record_id: data.record_id || null,
      evidence_type: data.evidence_type,
      source: data.source,
      description: data.description,
      collection_timestamp: data.collection_timestamp || null,
      confidence: data.confidence ?? 0,
      evidence_metadata: data.evidence_metadata || null
    });
    return mapEvidence(response);
  },

  verifyEvidence: async (evidenceId, status) => {
    const response = await apiPatch(`/evidence/${evidenceId}/verify`, { status });
    return response.data || response;
  }
};

function mapEvidence(evidence) {
  return {
    ...evidence,
    title: evidence.description || evidence.source,
    type: evidence.evidence_type,
    status: evidence.verification_status || 'PENDING',
    created_at: evidence.created_at,
    _raw: evidence
  };
}

export default evidenceService;
