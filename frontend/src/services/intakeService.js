import { apiGet } from './api';

export const intakeService = {
  startAnalysis: async (fileInfo, caseId, sourceType) => {
    return {
      jobId: `JOB-${Date.now()}`,
      fileInfo,
      caseId: caseId || '3',
      sourceType: sourceType || 'FIR',
      status: 'BACKEND_INTEGRATED',
      startedAt: new Date().toISOString(),
      message: 'Data ingestion is handled by the backend system. Use the backend upload endpoint for file processing.'
    };
  },

  getProcessingResults: async (jobId) => {
    return {
      jobId,
      status: 'COMPLETED',
      results: 'Processing results available through backend API.'
    };
  }
};

export default intakeService;