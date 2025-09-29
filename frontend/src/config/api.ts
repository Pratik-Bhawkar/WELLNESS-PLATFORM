// API Configuration for Mental Wellness Platform - Unified Service
// Single API endpoint architecture for simplified deployment

// Get unified API URL from environment or default to localhost:8000
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Unified service endpoints
export const API_ENDPOINTS = {
  // Base URL
  BASE: API_BASE_URL,
  
  // Health check
  HEALTH: `${API_BASE_URL}/health`,
  
  // Chat/LLM endpoints
  CHAT: `${API_BASE_URL}/api/chat`,
  
  // Intent classification endpoints
  CLASSIFY: `${API_BASE_URL}/api/classify`,
  
  // Analytics endpoints
  ANALYTICS: `${API_BASE_URL}/api/analytics`,
  MOOD_RECORD: `${API_BASE_URL}/api/mood/record`,
};

// Default request configuration
export const DEFAULT_REQUEST_CONFIG = {
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000, // 15 seconds timeout for LLM responses
};

// Environment info for debugging
export const ENV_INFO = {
  API_BASE_URL,
  UNIFIED_SERVICE: true,
  NODE_ENV: process.env.NODE_ENV || 'development',
};

console.log('API Configuration loaded (Unified Service):', ENV_INFO);