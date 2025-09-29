import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { API_ENDPOINTS, DEFAULT_REQUEST_CONFIG } from '../config/api';

// Types following the API specifications
interface Message {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  intent?: string;
  confidence?: number;
}

// Removed unused ChatResponse interface

// Styled components for mental wellness theme
const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 800px;
  margin: 0 auto;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
`;

const Header = styled.div`
  background: rgba(255, 255, 255, 0.1);
  padding: 1rem;
  text-align: center;
  color: white;
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const MessageBubble = styled.div<{ sender: 'user' | 'assistant' }>`
  max-width: 70%;
  padding: 1rem;
  border-radius: 18px;
  align-self: ${(props) => (props.sender === 'user' ? 'flex-end' : 'flex-start')};
  background: ${(props) =>
    props.sender === 'user'
      ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      : 'rgba(255, 255, 255, 0.9)'};
  color: ${(props) => (props.sender === 'user' ? 'white' : '#333')};
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  word-wrap: break-word;
`;

const InputContainer = styled.div`
  display: flex;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  gap: 1rem;
`;

const MessageInput = styled.input`
  flex: 1;
  padding: 1rem;
  border: none;
  border-radius: 25px;
  background: rgba(255, 255, 255, 0.9);
  font-size: 1rem;
  outline: none;
  
  &::placeholder {
    color: #666;
  }
`;

const SendButton = styled.button`
  padding: 1rem 2rem;
  border: none;
  border-radius: 25px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: bold;
  cursor: pointer;
  transition: transform 0.2s;
  
  &:hover {
    transform: translateY(-2px);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const StatusIndicator = styled.div<{ connected: boolean }>`
  padding: 0.5rem 1rem;
  border-radius: 15px;
  background: ${(props) => (props.connected ? '#4CAF50' : '#f44336')};
  color: white;
  font-size: 0.8rem;
  margin-bottom: 1rem;
`;

// Main ChatInterface Component
const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize services connection check
  useEffect(() => {
    const checkServices = async () => {
      try {
        // Check if unified API service is running
        console.log('Checking unified service at:', API_ENDPOINTS.HEALTH);
        
        const healthResponse = await fetch(API_ENDPOINTS.HEALTH);
        
        if (healthResponse.ok) {
          const healthData = await healthResponse.json();
          setIsConnected(true);
          console.log('Connected to unified wellness service:', healthData);
          
          // Add welcome message only if no messages exist
          if (messages.length === 0) {
            const welcomeMessage: Message = {
              id: Date.now().toString(),
              content: "Hello! I'm your wellness assistant powered by Phi-3-mini. I'm here to help you with mental health support. How are you feeling today?",
              sender: 'assistant',
              timestamp: new Date()
            };
            setMessages([welcomeMessage]);
          }
        } else {
          setIsConnected(false);
          console.log('Unified service health check failed');
        }
      } catch (error) {
        setIsConnected(false);
        console.log('Unified service not available yet, error:', error);
      }
    };

    checkServices();
    // Check every 5 seconds
    const interval = setInterval(checkServices, 5000);

    return () => clearInterval(interval);
  }, [messages.length]); // Added messages.length dependency

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Send message function - Unified API service
  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages((prev) => [...prev, userMessage]);
    const messageText = inputValue;
    setInputValue('');
    setIsLoading(true);

    try {
      // Step 1: Classify intent using unified API
      console.log('Sending intent request to:', API_ENDPOINTS.CLASSIFY);
      const intentResponse = await fetch(API_ENDPOINTS.CLASSIFY, {
        method: 'POST',
        ...DEFAULT_REQUEST_CONFIG,
        body: JSON.stringify({
          message: messageText,
          user_id: 1
        }),
      });

      if (!intentResponse.ok) {
        throw new Error(`Intent classification failed: ${intentResponse.status} ${intentResponse.statusText}`);
      }

      const intentData = await intentResponse.json();
      console.log('Intent classified:', intentData);

      // Step 2: Get response from unified LLM API
      console.log('Sending LLM request to:', API_ENDPOINTS.CHAT);
      const llmResponse = await fetch(API_ENDPOINTS.CHAT, {
        method: 'POST',
        ...DEFAULT_REQUEST_CONFIG,
        body: JSON.stringify({
          message: messageText,
          user_id: 1,
          conversation_history: messages.slice(-10).map(m => ({
            role: m.sender === 'user' ? 'user' : 'assistant',
            content: m.content
          }))
        }),
      });

      if (llmResponse.ok) {
        const llmData = await llmResponse.json();
        const assistantMessage: Message = {
          id: Date.now().toString(),
          content: llmData.response,
          sender: 'assistant',
          timestamp: new Date(),
          intent: intentData.intent,
          confidence: intentData.confidence
        };
        
        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        throw new Error(`LLM service failed: ${llmResponse.status} ${llmResponse.statusText}`);
      }
      setIsLoading(false);
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Fallback response with detailed error information
      const errorMessage: Message = {
        id: Date.now().toString(),
        content: `I'm having trouble connecting to the wellness service. Error: ${error}. Please ensure the unified service is running at: ${API_ENDPOINTS.BASE}`,
        sender: 'assistant',
        timestamp: new Date()
      };
      
      setMessages((prev) => [...prev, errorMessage]);
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  return (
    <ChatContainer>
      <Header>
        <h1>🧠 Mental Wellness AI Platform</h1>
        <p>Phase 2: Pure Python Architecture with Phi-3-mini</p>
        <StatusIndicator connected={isConnected}>
          {isConnected ? '🟢 Connected to Python Services' : '🔴 Connecting to Python Services...'}
        </StatusIndicator>
      </Header>

      <MessagesContainer>
        {messages.map((message) => (
          <MessageBubble key={message.id} sender={message.sender}>
            <div>{message.content}</div>
            {message.intent && (
              <div style={{ fontSize: '0.8rem', opacity: 0.7, marginTop: '0.5rem' }}>
                Intent: {message.intent}
              </div>
            )}
          </MessageBubble>
        ))}
        {isLoading && (
          <MessageBubble sender="assistant">
            <div>🤔 Thinking...</div>
          </MessageBubble>
        )}
        <div ref={messagesEndRef} />
      </MessagesContainer>

      <InputContainer>
        <MessageInput
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="How are you feeling today? Type your message..."
          disabled={isLoading}
        />
        <SendButton onClick={sendMessage} disabled={isLoading || !inputValue.trim()}>
          {isLoading ? '...' : 'Send'}
        </SendButton>
      </InputContainer>
    </ChatContainer>
  );
};

export default ChatInterface;