export const reportService = {
  getReports: async () => {
    return [];
  },

  generateReport: async (reportType, caseId) => {
    return {
      id: `RPT-${Date.now()}`,
      title: `${caseId || 'Case'} - ${reportType || 'Analysis'} Report`,
      report_type: reportType || 'Analysis Report',
      case_id: caseId,
      generated_by: 'System',
      generated_date: new Date().toISOString(),
      status: 'BACKEND_INTEGRATED',
      disclaimer: 'Report generation requires backend integration. This is a placeholder.',
      summary: 'Full report generation available through backend API.',
      sections: []
    };
  }
};

export default reportService;