// API configuration
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

// Helper function to make API calls
export const apiCall = (endpoint: string) => {
  return `${API_BASE_URL}${endpoint}`;
};