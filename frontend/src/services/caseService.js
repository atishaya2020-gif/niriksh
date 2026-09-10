import { apiGet, apiPost } from './api';

const mapCase = (caseData = {}) => ({
  id: caseData.id,
  case_number: caseData.case_number || '',
  title: caseData.title || '',
  description: caseData.description || '',
  created_at: caseData.created_at || null,
  last_updated: caseData.created_at
    ? new Date(caseData.created_at).toLocaleDateString()
    : 'Unavailable'
});

export const caseService = {
  getCases: async (filters = {}) => {
    const response = await apiGet('/cases');

    const rawCases = Array.isArray(response)
      ? response
      : response?.data?.cases ||
        response?.data ||
        [];

    let cases = rawCases.map(mapCase);

    if (filters.search) {
      const query =
        filters.search.toLowerCase();

      cases = cases.filter(
        (item) =>
          item.case_number
            .toLowerCase()
            .includes(query) ||
          item.title
            .toLowerCase()
            .includes(query) ||
          item.description
            .toLowerCase()
            .includes(query)
      );
    }

    return cases;
  },

  getCase: async (caseId) => {
    const numericCaseId =
      Number(caseId);

    if (
      !Number.isInteger(
        numericCaseId
      ) ||
      numericCaseId <= 0
    ) {
      throw new Error(
        `Invalid database case ID: ${caseId}`
      );
    }

    const response =
      await apiGet(
        `/cases/${numericCaseId}/overview`
      );

    const overview =
      response?.data || response;

    const caseInfo =
      overview?.case || {};

    const metrics =
      overview?.metrics || {};

    const investigation =
      overview?.investigation || {};

    return {
      ...mapCase(caseInfo),

      risk:
        investigation.risk_level ||
        null,

      status:
        investigation.status ||
        null,

      records_count:
        metrics.records ?? 0,

      entities_count:
        metrics.entities ?? 0,

      relationships_count:
        metrics.relationships ?? 0,

      evidence_count:
        metrics.evidence ?? 0,

      alerts_count:
        metrics.active_alerts ?? 0,

      key_entities:
        Array.isArray(
          overview.key_entities
        )
          ? overview.key_entities
          : [],

      alerts:
        Array.isArray(
          overview.alerts
        )
          ? overview.alerts
          : [],

      analysis_note:
        overview.analysis_note ||
        null,

      _raw:
        overview
    };
  },

  getTimeline: async (
    caseId,
    params = {}
  ) => {
    const numericCaseId =
      Number(caseId);

    if (
      !Number.isInteger(
        numericCaseId
      ) ||
      numericCaseId <= 0
    ) {
      throw new Error(
        `Invalid database case ID: ${caseId}`
      );
    }

    return apiGet(
      `/cases/${numericCaseId}/timeline`,
      params
    );
  },

  createCase: async (
    caseData
  ) => {
    const response =
      await apiPost(
        '/cases',
        {
          case_number:
            caseData.case_number,

          title:
            caseData.title,

          description:
            caseData.description ||
            null
        }
      );

    return mapCase(
      response?.data ||
      response
    );
  }
};

export default caseService;