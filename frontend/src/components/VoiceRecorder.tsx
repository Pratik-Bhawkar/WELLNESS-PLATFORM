import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { API_BASE_URL } from '../config/api';

const VoiceContainer = styled.div`
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-bottom: 20px;
`;

const RecordButton = styled.button<{ isRecording: boolean }>`
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: none;
  background: ${props => props.isRecording ? '#ff4444' : '#4a90e2'};
  color: white;
  font-size: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin: 10px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);

  &:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 20px rgba(0,0,0,0.3);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const StatusText = styled.div`
  text-align: center;
  margin: 10px 0;
  font-weight: 500;
  color: #333;
`;

const TranscriptionBox = styled.div`
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  margin: 15px 0;
  border-left: 4px solid #4a90e2;
  font-style: italic;
  color: #555;
  min-height: 60px;
  display: flex;
  align-items: center;
`;

const ControlsContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin: 20px 0;
`;

const FileUpload = styled.div`
  margin: 20px 0;
  text-align: center;
`;

const FileInput = styled.input`
  display: none;
`;

const FileButton = styled.label`
  background: #28a745;
  color: white;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  display: inline-block;
  transition: background 0.3s ease;

  &:hover {
    background: #218838;
  }
`;

const LoadingSpinner = styled.div`
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #4a90e2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 10px;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

interface VoiceRecorderProps {
  onTranscription: (text: string, emotion?: string) => void;
  disabled?: boolean;
}

const VoiceRecorder: React.FC<VoiceRecorderProps> = ({ onTranscription, disabled = false }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcription, setTranscription] = useState('');
  const [status, setStatus] = useState('Click microphone to start recording');
  const [recordingTime, setRecordingTime] = useState(0);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, []);

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
      
      mediaRecorder.start(100); // Collect data every 100ms
      setIsRecording(true);
      setStatus('Recording... Click to stop');
      setRecordingTime(0);
      
      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 0.1);
      }, 100);
      
    } catch (error) {
      console.error('Error accessing microphone:', error);
      setStatus('Microphone access denied. Please enable microphone permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setStatus('Processing audio...');
      
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  const processRecording = async () => {
    if (audioChunksRef.current.length === 0) return;
    
    setIsProcessing(true);
    
    try {
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
      await uploadAudio(audioBlob, 'recording');
    } catch (error) {
      console.error('Error processing recording:', error);
      setStatus('Error processing recording. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Check file type
    const allowedTypes = ['audio/wav', 'audio/mp3', 'audio/flac', 'audio/m4a', 'audio/ogg', 'audio/webm'];
    if (!allowedTypes.includes(file.type) && !file.name.match(/\.(wav|mp3|flac|m4a|ogg|webm)$/i)) {
      setStatus('Unsupported file format. Please use WAV, MP3, FLAC, M4A, OGG, or WEBM.');
      return;
    }

    setIsProcessing(true);
    setStatus('Processing uploaded file...');
    
    try {
      await uploadAudio(file, file.name);
    } catch (error) {
      console.error('Error processing file:', error);
      setStatus('Error processing file. Please try again.');
    } finally {
      setIsProcessing(false);
      // Reset file input
      event.target.value = '';
    }
  };

  const uploadAudio = async (audioData: Blob | File, filename: string) => {
    const formData = new FormData();
    formData.append('audio_file', audioData, filename);
    formData.append('user_id', '1');
    formData.append('language', 'auto');

    try {
      const response = await fetch(`${API_BASE_URL}/api/voice/transcribe`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      setTranscription(result.transcription);
      setStatus(`Transcribed successfully (${result.language})`);
      
      // Pass transcription to parent component
      onTranscription(result.transcription, result.emotional_tone);
      
    } catch (error) {
      console.error('Error uploading audio:', error);
      setStatus('Failed to transcribe audio. Please check your connection and try again.');
    }
  };

  const handleRecordClick = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <VoiceContainer>
      <h3>🎤 Voice Input</h3>
      
      <ControlsContainer>
        <RecordButton
          isRecording={isRecording}
          onClick={handleRecordClick}
          disabled={disabled || isProcessing}
          title={isRecording ? 'Stop Recording' : 'Start Recording'}
        >
          {isProcessing ? '⏳' : isRecording ? '⏹️' : '🎤'}
        </RecordButton>
        
        {isRecording && (
          <div>
            <strong>{recordingTime.toFixed(1)}s</strong>
          </div>
        )}
        
        {isProcessing && <LoadingSpinner />}
      </ControlsContainer>

      <StatusText>
        {isProcessing && <LoadingSpinner />}
        {status}
      </StatusText>

      <FileUpload>
        <FileButton htmlFor="audio-upload">
          📁 Upload Audio File
        </FileButton>
        <FileInput
          id="audio-upload"
          type="file"
          accept=".wav,.mp3,.flac,.m4a,.ogg,.webm,audio/*"
          onChange={handleFileUpload}
          disabled={disabled || isProcessing}
        />
      </FileUpload>

      {transcription && (
        <TranscriptionBox>
          <strong>Transcription:</strong> "{transcription}"
        </TranscriptionBox>
      )}
    </VoiceContainer>
  );
};

export default VoiceRecorder;