export const envConfig = {
  useMockData: import.meta.env.VITE_USE_MOCK_DATA === 'true',
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api',
  appTitle: 'NIRIKSH',
  appTagline: 'AI-Powered Criminal Network Analysis System',
  platformNotice: 'Secure Investigation Intelligence Platform | Synthetic Data Prototype'
};

export default envConfig;
