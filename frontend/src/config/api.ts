// API Configuration for Mental Wellness Platform
// This file centralizes all service endpoints to avoid hardcoded URLs

// Get base URL from environment or default to localhost
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost';

// Get service ports from environment or use defaults
const LLM_SERVICE_PORT = process.env.REACT_APP_LLM_SERVICE_PORT || '8000';
const INTENT_SERVICE_PORT = process.env.REACT_APP_INTENT_SERVICE_PORT || '8001';
const ANALYTICS_SERVICE_PORT = process.env.REACT_APP_ANALYTICS_SERVICE_PORT || '8002';

// Service URLs
export const API_ENDPOINTS = {
  // LLM Service
  LLM_BASE: `${API_BASE_URL}:${LLM_SERVICE_PORT}`,
  LLM_HEALTH: `${API_BASE_URL}:${LLM_SERVICE_PORT}/health`,
  LLM_CHAT: `${API_BASE_URL}:${LLM_SERVICE_PORT}/chat`,
  
  // Intent Classification Service
  INTENT_BASE: `${API_BASE_URL}:${INTENT_SERVICE_PORT}`,
  INTENT_HEALTH: `${API_BASE_URL}:${INTENT_SERVICE_PORT}/health`,
  INTENT_CLASSIFY: `${API_BASE_URL}:${INTENT_SERVICE_PORT}/classify`,
  
  // Analytics Service
  ANALYTICS_BASE: `${API_BASE_URL}:${ANALYTICS_SERVICE_PORT}`,
  ANALYTICS_HEALTH: `${API_BASE_URL}:${ANALYTICS_SERVICE_PORT}/health`,
  ANALYTICS_MOOD: `${API_BASE_URL}:${ANALYTICS_SERVICE_PORT}/mood`,
  ANALYTICS_REPORT: `${API_BASE_URL}:${ANALYTICS_SERVICE_PORT}/report`,
};

// Default request configuration
export const DEFAULT_REQUEST_CONFIG = {
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds timeout
};

// Environment info for debugging
export const ENV_INFO = {
  API_BASE_URL,
  LLM_SERVICE_PORT,
  INTENT_SERVICE_PORT,
  ANALYTICS_SERVICE_PORT,
  NODE_ENV: process.env.NODE_ENV || 'development',
};

console.log('API Configuration loaded:', ENV_INFO);