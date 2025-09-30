import React, { useState, useEffect, useRef } from 'react';
import { API_ENDPOINTS, CONFIG } from '../config/api';
import {
  GlobalStyle,
  AppContainer,
  MainContent,
  Header,
  HeaderTitle,
  ChatContainer,
  MessagesArea,
  MessageContainer,
  MessageContent,
  Avatar,
  MessageText,
  InputArea,
  InputContainer,
  InputWrapper,
  VoiceInputRow,
  TextInputRow,
  TextInput,
  VoiceButton,
  SendButton,
  StatusText,
  LoadingDots
} from '../styles/GlobalStyles';

// Types
interface Message {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  intent?: string;
  confidence?: number;
}

const ChatGPTInterface: React.FC = () => {
  // Helper function for API requests with timeout - longer timeout for LLM responses
  const fetchWithTimeout = async (url: string, options: RequestInit = {}, timeout: number = CONFIG.API_TIMEOUT) => {
    const controller = new AbortController();
    
    // Use longer timeout for chat requests (LLM takes time to generate)
    const actualTimeout = url.includes('/api/chat') ? 60000 : timeout; // 60 seconds for chat
    
    const timeoutId = setTimeout(() => {
      console.log(`⏰ Request timeout after ${actualTimeout}ms for ${url}`);
      controller.abort();
    }, actualTimeout);
    
    try {
      console.log(`🔄 Starting request to ${url} with ${actualTimeout}ms timeout`);
      const response = await fetch(url, {
        ...options,
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      console.log(`✅ Request completed to ${url}`);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error(`Request timeout after ${actualTimeout}ms - The AI is taking longer than expected to respond.`);
      }
      throw error;
    }
  };

  // State management
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  
  // Voice recording state
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessingVoice, setIsProcessingVoice] = useState(false);
  const [voiceStatus, setVoiceStatus] = useState('');
  
  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check API connection
  useEffect(() => {
    const checkConnection = async () => {
      try {
        const response = await fetchWithTimeout(API_ENDPOINTS.HEALTH);
        if (response.ok) {
          setIsConnected(true);
          if (messages.length === 0) {
            // Add welcome message
            const welcomeMessage: Message = {
              id: Date.now().toString(),
              content: `Hello! I'm your ${CONFIG.APP_NAME} Assistant. I'm here to support you with stress, anxiety, and mental health guidance. How are you feeling today?`,
              sender: 'assistant',
              timestamp: new Date()
            };
            setMessages([welcomeMessage]);
          }
        } else {
          setIsConnected(false);
        }
      } catch (error) {
        setIsConnected(false);
      }
    };

    checkConnection();
    const interval = setInterval(checkConnection, 10000); // Check every 10 seconds
    return () => clearInterval(interval);
  }, [messages.length]);

  // Handle text input auto-resize
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);
    
    // Auto-resize textarea
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
  };

  // Send message function
  const sendMessage = async (messageText?: string) => {
    const messageToSend = messageText || inputValue.trim();
    if (!messageToSend || isLoading) return;

    // Create user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content: messageToSend,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // Add "AI is thinking" message
    const thinkingMessage: Message = {
      id: 'thinking-' + Date.now(),
      content: '🤔 AI is thinking...',
      sender: 'assistant',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, thinkingMessage]);

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }

    try {
      // Send to unified API
      const response = await fetchWithTimeout(API_ENDPOINTS.CHAT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: messageToSend,
          user_id: 1,
          conversation_history: messages.slice(-CONFIG.MAX_MESSAGE_HISTORY).map(m => ({
            role: m.sender === 'user' ? 'user' : 'assistant',
            content: m.content
          })),
          context: `${CONFIG.APP_NAME} conversation`
        })
      });

      console.log('🔍 Chat API Response:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok,
        url: response.url
      });

      if (response.ok) {
        const data = await response.json();
        console.log('✅ Chat API Data:', data);
        
        const assistantMessage: Message = {
          id: Date.now().toString(),
          content: data.response || data.message || 'No response received',
          sender: 'assistant',
          timestamp: new Date(),
          confidence: data.confidence
        };

        // Replace thinking message with actual response
        setMessages(prev => prev.filter(m => !m.id.startsWith('thinking-')).concat(assistantMessage));
      } else {
        const errorText = await response.text();
        console.error('❌ API Error:', {
          status: response.status,
          statusText: response.statusText,
          body: errorText
        });
        throw new Error(`API Error: ${response.status} - ${errorText}`);
      }
    } catch (error) {
      console.error('💥 Chat error:', error);
      
      const errorMessage: Message = {
        id: Date.now().toString(),
        content: `Connection error: ${error instanceof Error ? error.message : 'Unknown error'}. Please check the console for details.`,
        sender: 'assistant',
        timestamp: new Date()
      };

      // Remove thinking message and add error message
      setMessages(prev => prev.filter(m => !m.id.startsWith('thinking-')).concat(errorMessage));
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Enter key
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Voice recording functions
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100
        } 
      });
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorder.onstop = () => {
        stream.getTracks().forEach(track => track.stop());
        processRecording();
      };
      
      mediaRecorder.start(100);
      setIsRecording(true);
      setVoiceStatus('Recording...');
      
    } catch (error) {
      console.error('Error accessing microphone:', error);
      setVoiceStatus('Microphone access denied');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setVoiceStatus('Processing...');
    }
  };

  const processRecording = async () => {
    if (audioChunksRef.current.length === 0) return;
    
    setIsProcessingVoice(true);
    
    try {
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
      const formData = new FormData();
      formData.append('audio_file', audioBlob, 'recording.webm');
      formData.append('user_id', '1');
      formData.append('language', 'auto');

      const response = await fetchWithTimeout(API_ENDPOINTS.VOICE_TRANSCRIBE, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setVoiceStatus(`Transcribed: "${result.transcription}"`);
        
        // Send transcribed message
        setTimeout(() => {
          sendMessage(result.transcription);
          setVoiceStatus('');
        }, 1000);
      } else {
        throw new Error(`Transcription failed: ${response.status}`);
      }
    } catch (error) {
      console.error('Voice processing error:', error);
      setVoiceStatus('Voice processing failed');
      setTimeout(() => setVoiceStatus(''), 3000);
    } finally {
      setIsProcessingVoice(false);
    }
  };

  const handleVoiceClick = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <>
      <GlobalStyle />
      <AppContainer>
        <MainContent>
          <Header>
            <HeaderTitle>{CONFIG.APP_NAME}</HeaderTitle>
          </Header>

          <ChatContainer>
            <MessagesArea>
              {messages.map((message, index) => (
                <MessageContainer key={message.id} sender={message.sender}>
                  <MessageContent>
                    <Avatar sender={message.sender}>
                      {message.sender === 'user' ? 'U' : 'AI'}
                    </Avatar>
                    <MessageText>
                      {message.content}
                      {message.confidence && (
                        <div style={{ fontSize: '12px', opacity: 0.6, marginTop: '8px' }}>
                          Confidence: {Math.round(message.confidence * 100)}%
                        </div>
                      )}
                    </MessageText>
                  </MessageContent>
                </MessageContainer>
              ))}
              
              {isLoading && (
                <MessageContainer sender="assistant">
                  <MessageContent>
                    <Avatar sender="assistant">AI</Avatar>
                    <MessageText>
                      <LoadingDots />
                    </MessageText>
                  </MessageContent>
                </MessageContainer>
              )}
              
              <div ref={messagesEndRef} />
            </MessagesArea>

            <InputArea>
              <InputContainer>
                <InputWrapper>
                  {/* Voice Input Row - Conditional based on environment */}
                  {CONFIG.VOICE_ENABLED && (
                    <VoiceInputRow>
                      <VoiceButton
                        onClick={handleVoiceClick}
                        disabled={isProcessingVoice || isLoading}
                        isRecording={isRecording}
                        isProcessing={isProcessingVoice}
                        title={isRecording ? 'Stop Recording' : 'Start Voice Recording'}
                      >
                        {isProcessingVoice ? '⏳' : isRecording ? '⏹️' : '🎤'}
                      </VoiceButton>
                    
                      <StatusText style={{ fontSize: '12px', color: '#8e8ea0', flex: 1 }}>
                        {voiceStatus || (isConnected ? 'Voice input available' : 'Connecting...')}
                      </StatusText>
                    </VoiceInputRow>
                  )}

                  {/* Text Input Row */}
                  <TextInputRow>
                    <TextInput
                      ref={textareaRef}
                      value={inputValue}
                      onChange={handleInputChange}
                      onKeyDown={handleKeyDown}
                      placeholder={`Message ${CONFIG.APP_NAME}...`}
                      disabled={isLoading}
                      rows={1}
                    />
                    
                    <SendButton
                      onClick={() => sendMessage()}
                      disabled={isLoading || !inputValue.trim()}
                      title="Send message"
                    >
                      {isLoading ? '⏳' : '↑'}
                    </SendButton>
                  </TextInputRow>
                </InputWrapper>
              </InputContainer>
            </InputArea>
          </ChatContainer>
        </MainContent>
      </AppContainer>
    </>
  );
};

export default ChatGPTInterface;