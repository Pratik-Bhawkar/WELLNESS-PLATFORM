import React, { useState, useRef } from 'react';
import styled from 'styled-components';
import { API_BASE_URL } from '../config/api';

const VoiceButton = styled.button<{ isRecording: boolean }>`
  background: ${props => props.isRecording ? '#ff4444' : '#4a90e2'};
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  color: white;
  cursor: pointer;
  margin-right: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  transition: all 0.3s ease;

  &:hover {
    transform: scale(1.1);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const StatusText = styled.div`
  font-size: 10px;
  color: #666;
  position: absolute;
  top: -20px;
  left: 0;
  white-space: nowrap;
`;

const VoiceContainer = styled.div`
  position: relative;
  display: inline-block;
`;

interface SimpleVoiceRecorderProps {
  onTranscription: (text: string) => void;
  disabled?: boolean;
}

const SimpleVoiceRecorder: React.FC<SimpleVoiceRecorderProps> = ({ onTranscription, disabled = false }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [status, setStatus] = useState('');
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
        } 
      });
      
      const mediaRecorder = new MediaRecorder(stream);
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
      
      mediaRecorder.start();
      setIsRecording(true);
      setStatus('Recording...');
      
    } catch (error) {
      console.error('Error accessing microphone:', error);
      setStatus('Mic access denied');
      setTimeout(() => setStatus(''), 3000);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setStatus('Processing...');
    }
  };

  const processRecording = async () => {
    if (audioChunksRef.current.length === 0) return;
    
    setIsProcessing(true);
    
    try {
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
      
      const formData = new FormData();
      formData.append('audio_file', audioBlob, 'recording.webm');
      formData.append('user_id', '1');
      formData.append('language', 'auto');

      const response = await fetch(`${API_BASE_URL}/api/voice/transcribe`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const result = await response.json();
      
      if (result.transcription && result.transcription.trim()) {
        onTranscription(result.transcription);
        setStatus('✓ Done');
      } else {
        setStatus('No speech detected');
      }
      
    } catch (error) {
      console.error('Error processing audio:', error);
      setStatus('Error processing audio');
    } finally {
      setIsProcessing(false);
      setTimeout(() => setStatus(''), 3000);
    }
  };

  const handleClick = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <VoiceContainer>
      {status && <StatusText>{status}</StatusText>}
      <VoiceButton
        isRecording={isRecording}
        onClick={handleClick}
        disabled={disabled || isProcessing}
        title={isRecording ? 'Stop Recording' : 'Start Voice Recording'}
      >
        {isProcessing ? '⏳' : isRecording ? '⏹️' : '🎤'}
      </VoiceButton>
    </VoiceContainer>
  );
};

export default SimpleVoiceRecorder;