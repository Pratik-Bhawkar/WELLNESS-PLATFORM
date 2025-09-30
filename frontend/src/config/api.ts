// API Configuration for Mental Wellness Platform - Unified Environment
// All configuration from single root .env file

// API Configuration - All from unified environment variables
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_TIMEOUT = parseInt(process.env.REACT_APP_API_TIMEOUT || '15000');

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
  
  // Voice processing endpoints
  VOICE_TRANSCRIBE: `${API_BASE_URL}/api/voice/transcribe`,
  VOICE_CHAT: `${API_BASE_URL}/api/voice/chat`,
};

// Voice Configuration
const VOICE_ENABLED = process.env.REACT_APP_VOICE_ENABLED === 'true';
const VOICE_TIMEOUT = parseInt(process.env.REACT_APP_VOICE_TIMEOUT || '30000');
const VOICE_LANGUAGE = process.env.REACT_APP_VOICE_LANGUAGE || 'auto';

// UI Configuration
const THEME = process.env.REACT_APP_THEME || 'dark';
const APP_NAME = process.env.REACT_APP_APP_NAME || 'Mental Wellness AI';
const MAX_MESSAGE_HISTORY = parseInt(process.env.REACT_APP_MAX_MESSAGE_HISTORY || '50');

// Features Configuration
const ANALYTICS_ENABLED = process.env.REACT_APP_ANALYTICS_ENABLED === 'true';
const MOOD_TRACKING_ENABLED = process.env.REACT_APP_MOOD_TRACKING_ENABLED === 'true';
const INTENT_CLASSIFICATION_ENABLED = process.env.REACT_APP_INTENT_CLASSIFICATION_ENABLED === 'true';

// Performance Configuration
const MESSAGE_BATCH_SIZE = parseInt(process.env.REACT_APP_MESSAGE_BATCH_SIZE || '10');
const AUTO_SCROLL_ENABLED = process.env.REACT_APP_AUTO_SCROLL_ENABLED === 'true';
const TYPING_INDICATOR_ENABLED = process.env.REACT_APP_TYPING_INDICATOR_ENABLED === 'true';

// Default request configuration
export const DEFAULT_REQUEST_CONFIG = {
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: API_TIMEOUT,
};

// Unified configuration object
export const CONFIG = {
  API_BASE_URL,
  API_TIMEOUT,
  VOICE_ENABLED,
  VOICE_TIMEOUT,
  VOICE_LANGUAGE,
  THEME,
  APP_NAME,
  MAX_MESSAGE_HISTORY,
  ANALYTICS_ENABLED,
  MOOD_TRACKING_ENABLED,
  INTENT_CLASSIFICATION_ENABLED,
  MESSAGE_BATCH_SIZE,
  AUTO_SCROLL_ENABLED,
  TYPING_INDICATOR_ENABLED,
};

// Export API_BASE_URL for backward compatibility
export { API_BASE_URL };

// Environment info for debugging
export const ENV_INFO = {
  ...CONFIG,
  UNIFIED_ENV: true,
  NODE_ENV: process.env.NODE_ENV || 'development',
};

console.log('API Configuration loaded (Unified Environment):', ENV_INFO);