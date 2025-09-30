import styled, { createGlobalStyle } from 'styled-components';

// ChatGPT-like Dark Theme Colors
export const theme = {
  // Background colors
  bg: {
    primary: '#212121',      // Main background (ChatGPT dark)
    secondary: '#171717',    // Sidebar/header background
    chat: '#212121',         // Chat area background
    message: '#2f2f2f',      // Message bubble background
    input: '#40414f',        // Input field background
    hover: '#2a2b32',        // Hover states
  },
  
  // Text colors
  text: {
    primary: '#ececf1',      // Main text (white-ish)
    secondary: '#c5c5d2',    // Secondary text
    muted: '#8e8ea0',        // Muted text
    accent: '#10a37f',       // Accent color (ChatGPT green)
    user: '#ececf1',         // User message text
    assistant: '#ececf1',    // Assistant message text
  },
  
  // Border colors
  border: {
    primary: '#565869',      // Main borders
    secondary: '#40414f',    // Secondary borders
    hover: '#676767',        // Hover borders
  },
  
  // Button colors
  button: {
    primary: '#10a37f',      // Primary button (ChatGPT green)
    primaryHover: '#0d8a6b', // Primary button hover
    secondary: '#40414f',    // Secondary button
    secondaryHover: '#565869', // Secondary button hover
    disabled: '#2f2f2f',     // Disabled button
  },
  
  // Voice/Recording colors
  voice: {
    recording: '#ef4444',    // Recording state (red)
    inactive: '#10a37f',     // Inactive microphone
    processing: '#f59e0b',   // Processing state (orange)
  },
  
  // Status colors
  status: {
    success: '#22c55e',      // Success green
    error: '#ef4444',        // Error red  
    warning: '#f59e0b',      // Warning orange
    info: '#3b82f6',         // Info blue
  }
};

// Global styles matching ChatGPT exactly
export const GlobalStyle = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  html, body {
    height: 100%;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
    background-color: ${theme.bg.primary};
    color: ${theme.text.primary};
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  #root {
    height: 100%;
    width: 100%;
  }

  /* Scrollbar styling like ChatGPT */
  ::-webkit-scrollbar {
    width: 8px;
  }

  ::-webkit-scrollbar-track {
    background: ${theme.bg.secondary};
  }

  ::-webkit-scrollbar-thumb {
    background: ${theme.border.primary};
    border-radius: 4px;
  }

  ::-webkit-scrollbar-thumb:hover {
    background: ${theme.border.hover};
  }

  /* Remove default button and input styles */
  button {
    border: none;
    background: none;
    cursor: pointer;
    font-family: inherit;
  }

  input, textarea {
    border: none;
    outline: none;
    font-family: inherit;
    color: inherit;
    background: transparent;
  }

  /* Selection color */
  ::selection {
    background-color: ${theme.button.primary}40;
    color: ${theme.text.primary};
  }
`;

// ChatGPT-like Layout Components
export const AppContainer = styled.div`
  display: flex;
  height: 100vh;
  width: 100vw;
  background-color: ${theme.bg.primary};
`;

export const MainContent = styled.main`
  display: flex;
  flex-direction: column;
  flex: 1;
  height: 100vh;
  background-color: ${theme.bg.primary};
`;

export const Header = styled.header`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 16px;
  background-color: ${theme.bg.secondary};
  border-bottom: 1px solid ${theme.border.secondary};
  position: sticky;
  top: 0;
  z-index: 10;
`;

export const HeaderTitle = styled.h1`
  font-size: 14px;
  font-weight: 600;
  color: ${theme.text.primary};
  margin: 0;
`;

export const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  flex: 1;
  max-width: 768px;
  width: 100%;
  margin: 0 auto;
  height: 100%;
`;

export const MessagesArea = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 24px 0;
  display: flex;
  flex-direction: column;
`;

export const MessageContainer = styled.div<{ sender: 'user' | 'assistant' }>`
  display: flex;
  padding: 24px;
  background-color: ${props => props.sender === 'assistant' ? theme.bg.message : 'transparent'};
  border-bottom: ${props => props.sender === 'assistant' ? `1px solid ${theme.border.secondary}` : 'none'};
`;

export const MessageContent = styled.div`
  max-width: 100%;
  width: 100%;
  display: flex;
  gap: 24px;
`;

export const Avatar = styled.div<{ sender: 'user' | 'assistant' }>`
  width: 30px;
  height: 30px;
  border-radius: 2px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 16px;
  font-weight: 600;
  background-color: ${props => props.sender === 'user' ? theme.button.primary : theme.bg.secondary};
  color: ${theme.text.primary};
`;

export const MessageText = styled.div`
  color: ${theme.text.primary};
  line-height: 1.75;
  font-size: 16px;
  word-wrap: break-word;
  min-width: 0;
  
  p {
    margin-bottom: 16px;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
`;

export const InputArea = styled.div`
  padding: 24px;
  background-color: ${theme.bg.primary};
`;

export const InputContainer = styled.div`
  max-width: 768px;
  width: 100%;
  margin: 0 auto;
  position: relative;
`;

export const InputWrapper = styled.div`
  display: flex;
  flex-direction: column;
  background-color: ${theme.bg.input};
  border-radius: 12px;
  border: 1px solid ${theme.border.secondary};
  min-height: 52px;
  
  &:focus-within {
    border-color: ${theme.border.hover};
  }
`;

export const VoiceInputRow = styled.div`
  display: flex;
  align-items: center;
  padding: 8px 16px;
  gap: 12px;
  border-bottom: 1px solid ${theme.border.secondary};
`;

export const TextInputRow = styled.div`
  display: flex;
  align-items: center;
  padding: 12px 16px;
  gap: 12px;
`;

export const TextInput = styled.textarea`
  flex: 1;
  background: transparent;
  color: ${theme.text.primary};
  font-size: 16px;
  line-height: 1.5;
  resize: none;
  min-height: 24px;
  max-height: 200px;
  
  &::placeholder {
    color: ${theme.text.muted};
  }
`;

export const VoiceButton = styled.button<{ isRecording?: boolean; isProcessing?: boolean }>`
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  transition: all 0.2s ease;
  background-color: ${props => 
    props.isRecording ? theme.voice.recording : 
    props.isProcessing ? theme.voice.processing : 
    theme.voice.inactive
  };
  color: white;
  
  &:hover {
    opacity: 0.8;
    transform: scale(1.05);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
`;

export const SendButton = styled.button<{ disabled?: boolean }>`
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  background-color: ${props => props.disabled ? theme.button.disabled : theme.button.primary};
  color: white;
  transition: all 0.2s ease;
  
  &:hover:not(:disabled) {
    background-color: ${theme.button.primaryHover};
  }
  
  &:disabled {
    cursor: not-allowed;
  }
`;

export const StatusText = styled.div`
  font-size: 12px;
  color: ${theme.text.muted};
  text-align: center;
  margin-top: 8px;
`;

export const LoadingDots = styled.div`
  display: inline-flex;
  gap: 4px;
  
  &::after {
    content: '';
    display: inline-block;
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background-color: ${theme.text.muted};
    animation: loading 1.4s infinite ease-in-out both;
  }
  
  &::before {
    content: '';
    display: inline-block;
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background-color: ${theme.text.muted};
    animation: loading 1.4s infinite ease-in-out both;
    animation-delay: -0.16s;
    margin-right: 4px;
  }
  
  @keyframes loading {
    0%, 80%, 100% {
      opacity: 0.3;
    }
    40% {
      opacity: 1;
    }
  }
`;