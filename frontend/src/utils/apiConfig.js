// Centralized API configuration
const API_CONFIG = {
  // Use environment variable if set, otherwise default to localhost for development
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  
  // Helper function to build full API URLs
  buildUrl: (endpoint) => {
    const baseUrl = API_CONFIG.BASE_URL.replace(/\/$/, ''); // Remove trailing slash
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`; // Ensure leading slash
    return `${baseUrl}${cleanEndpoint}`;
  },
  
  // Common endpoints
  ENDPOINTS: {
    USER_STATE: (userId) => `/api/user/${userId}/state`,
    USER_CHAT: (userId) => `/api/user/${userId}/chat`,
    USER_RANK: (userId) => `/api/user/${userId}/rank`,
    USER_FEEDBACK: (userId) => `/api/user/${userId}/feedback`,
    MANAGER_FEEDBACK: (userId) => `/api/manager/${userId}/feedback`,
    PERFORMANCE_GOALS: (userId) => `/api/performance/users/${userId}/goals`,
    PERFORMANCE_INSIGHT: (userId) => `/api/performance/users/${userId}/latest-insight`,
    PERFORMANCE_REPORTS: (userId) => `/api/performance/users/${userId}/direct-reports`,
    FEEDBACK_ANALYZE: '/api/feedback/analyze-and-update-goals',
    PROGRESS_UPDATE: (userId) => `/api/progress/update/${userId}`,
  }
};

export default API_CONFIG;
