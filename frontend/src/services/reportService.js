import { apiGet } from './api';

const buildReport = (
  reportType,
  caseId,
  overview
) => {

  const caseInfo =
    overview?.case || {};

  const metrics =
    overview?.metrics || {};

  const investigation =
    overview?.investigation || {};

  const entities =
    Array.isArray(
      overview?.key_entities
    )
      ? overview.key_entities
      : [];

  const alerts =
    Array.isArray(
      overview?.alerts
    )
      ? overview.alerts
      : [];

  return {

    id:
      `RPT-${Date.now()}`,

    title:
      `${caseInfo.case_number || caseId} - ${reportType}`,

    report_type:
      reportType,

    case_id:
      caseInfo.id || caseId,

    generated_by:
      'NIRIKSH ANALYTICAL ENGINE',

    generated_date:
      new Date().toLocaleString(),

    status:
      'GENERATED',

    disclaimer:
      'Analytical signals require human verification and do not independently establish guilt or identity.',

    summary:
      `The case contains ${
        metrics.records ?? 0
      } records, ${
        metrics.entities ?? 0
      } entities and ${
        metrics.relationships ?? 0
      } relationships.`,

    sections: [

      {
        heading:
          'CASE INFORMATION',

        content:
          `${caseInfo.title || 'Untitled Case'} — ${
            caseInfo.description ||
            'No case description available.'
          }`
      },

      {
        heading:
          'INVESTIGATION STATUS',

        content:
          `Status: ${
            investigation.status ||
            'UNKNOWN'
          }. Risk Level: ${
            investigation.risk_level ||
            'UNKNOWN'
          }.`
      },

      {
        heading:
          'NETWORK METRICS',

        content:
          `Records: ${
            metrics.records ?? 0
          }; Entities: ${
            metrics.entities ?? 0
          }; Relationships: ${
            metrics.relationships ?? 0
          }; Evidence: ${
            metrics.evidence ?? 0
          }; Active Alerts: ${
            metrics.active_alerts ?? 0
          }.`
      },

      {
        heading:
          'KEY ENTITIES',

        content:
          entities.length
            ? entities
                .map(
                  (entity) =>
                    `${entity.label || entity.id} — ${
                      entity.entity_type ||
                      entity.type ||
                      'Entity'
                    }`
                )
                .join('; ')
            : 'No key entities identified.'
      },

      {
        heading:
          'ALERT SUMMARY',

        content:
          alerts.length
            ? alerts
                .map(
                  (alert) =>
                    `${alert.alert_type || 'Alert'}: ${
                      alert.risk_level ||
                      'UNKNOWN'
                    } risk — ${
                      alert.reason ||
                      'No reason supplied'
                    }`
                )
                .join('; ')
            : 'No active alerts found.'
      }

    ]
  };
};

export const reportService = {

  getReports:
    async () => {
      return [];
    },

  generateReport:
    async (
      reportType,
      caseId
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
          `Invalid case ID: ${caseId}`
        );
      }

      const response =
        await apiGet(
          `/cases/${numericCaseId}/overview`
        );

      const overview =
        response?.data ||
        response;

      return buildReport(
        reportType,
        numericCaseId,
        overview
      );
    }
};

export default reportService;