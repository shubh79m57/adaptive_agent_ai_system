"use client";

import { useState, useRef, useEffect } from 'react';

interface VoiceConfig {
  stt_provider: string;
  tts_provider: string;
  ai_model: string;
  sample_rate: number;
  voice_id: string;
}

interface VoiceResponse {
  success: boolean;
  transcription?: string;
  ai_response?: string | {
    text: string;
    agent_type: string;
    confidence: number;
  };
  audio_response?: string;
  note?: string;
  error?: string;
}

export default function VoicePage() {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [voiceResponse, setVoiceResponse] = useState<VoiceResponse | null>(null);
  const [conversationHistory, setConversationHistory] = useState<any[]>([]);
  const [voiceConfig, setVoiceConfig] = useState<VoiceConfig>({
    stt_provider: 'whisper',
    tts_provider: 'pyttsx3',
    ai_model: 'local',
    sample_rate: 16000,
    voice_id: 'alloy'
  });
  const [capabilities, setCapabilities] = useState<any>(null);
  const [isInitialized, setIsInitialized] = useState(false);
  
  // Session-based conversation state
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioRef = useRef<HTMLAudioElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  
  // Voice activity detection
  const vadAnalyserRef = useRef<AnalyserNode | null>(null);
  const silenceTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const vadContextRef = useRef<AudioContext | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const isSessionActiveRef = useRef<boolean>(false); // Ref to track session state for RAF loop
  const isSpeakingRef = useRef<boolean>(false); // Ref for RAF loop
  const isRecordingRef = useRef<boolean>(false); // Ref for RAF loop
  const isProcessingRef = useRef<boolean>(false); // Ref for RAF loop
  const isAISpeakingRef = useRef<boolean>(false); // Ref for RAF loop
  
  const [isAISpeaking, setIsAISpeaking] = useState(false);

  useEffect(() => {
    loadCapabilities();
    
    // Setup audio visualization when component mounts
    return () => {
      // Cleanup on unmount
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);

  const loadCapabilities = async () => {
    try {
      const response = await fetch('http://localhost:8001/voice/capabilities');
      const data = await response.json();
      setCapabilities(data);
    } catch (error) {
      console.error('Error loading capabilities:', error);
    }
  };

  const initializeVoiceAgent = async () => {
    try {
      setIsProcessing(true);
      const response = await fetch('http://localhost:8001/voice/initialize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(voiceConfig)
      });

      const data = await response.json();
      if (data.success) {
        setIsInitialized(true);
        alert('Voice AI Agent initialized successfully!');
      } else {
        alert(`Initialization failed: ${data.error || 'Unknown error'}`);
      }
    } catch (error) {
      alert(`Error initializing voice agent: ${error}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const simpleTest = async () => {
    setIsProcessing(true);
    try {
      console.log('Running simple voice test...');
      const response = await fetch('http://localhost:8001/voice/simple-test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      const data = await response.json();
      console.log('Simple test response:', data);
      setVoiceResponse(data);
      
      if (data.status === 'success') {
        const newEntry = {
          timestamp: new Date().toLocaleTimeString(),
          user_input: data.transcription || '⚡ Quick test',
          ai_response: typeof data.ai_response === 'object' ? data.ai_response.text : data.ai_response || '',
          has_audio: false
        };
        setConversationHistory(prev => [...prev, newEntry]);
      }
    } catch (error) {
      console.error('Simple test error:', error);
      setVoiceResponse({
        success: false,
        error: `Simple test error: ${error}`
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const testWithSampleAudio = async () => {
    setIsProcessing(true);
    try {
      // Test audio processing with sample text
      const response = await fetch('http://localhost:8001/voice/test-audio', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      const data = await response.json();
      setVoiceResponse(data);
      
      if (data.success) {
        const newEntry = {
          timestamp: new Date().toLocaleTimeString(),
          user_input: data.transcription || '🎵 Test audio input',
          ai_response: typeof data.ai_response === 'object' ? data.ai_response.text : data.ai_response || '',
          has_audio: !!data.audio_response
        };
        setConversationHistory(prev => [...prev, newEntry]);
      }
    } catch (error) {
      setVoiceResponse({
        success: false,
        error: `Test error: ${error}`
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const startRecording = async () => {
    try {
      console.log('🎤 Starting recording...');
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        } 
      });
      
      // Use MediaRecorder for more reliable recording
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm' // Most browsers support this
      });
      
      const audioChunks: Blob[] = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.push(event.data);
          console.log('📦 Audio chunk received:', event.data.size, 'bytes');
        }
      };
      
      mediaRecorder.onstop = async () => {
        console.log('⏹️ Recording stopped, processing...');
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        console.log('🎵 Total audio size:', audioBlob.size, 'bytes');
        
        // Clean up stream
        stream.getTracks().forEach(track => track.stop());
        
        // Process the recorded audio
        await processRecordedAudio(audioBlob);
      };
      
      mediaRecorder.start();
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = audioChunks;
      
      console.log('✅ Recording started with MediaRecorder');
      setIsRecording(true);
      
    } catch (error) {
      console.error('❌ Microphone access error:', error);
      alert(`Error accessing microphone: ${error}`);
    }
  };

  const stopRecording = async () => {
    if (!isRecording || !mediaRecorderRef.current) return;
    
    console.log('🛑 Stopping recording...');
    setIsRecording(false);
    
    if (mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
  };

  // === Session-based Continuous Voice Conversation ===
  
  const startVoiceSession = async () => {
    try {
      console.log('🎙️ Starting voice session...');
      
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        } 
      });
      
      streamRef.current = stream;
      
      // Setup voice activity detection
      vadContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      const source = vadContextRef.current.createMediaStreamSource(stream);
      vadAnalyserRef.current = vadContextRef.current.createAnalyser();
      vadAnalyserRef.current.fftSize = 2048;
      vadAnalyserRef.current.smoothingTimeConstant = 0.8;
      source.connect(vadAnalyserRef.current);
      
      setIsSessionActive(true);
      isSessionActiveRef.current = true; // Set ref immediately
      console.log('✅ Voice session started - speak anytime!');
      
      // Start monitoring for voice activity
      monitorVoiceActivity();
      
    } catch (error) {
      console.error('❌ Error starting voice session:', error);
      alert(`Error accessing microphone: ${error}`);
    }
  };
  
  const endVoiceSession = () => {
    console.log('🛑 Ending voice session...');
    
    // Stop session immediately (this will stop the RAF loop)
    isSessionActiveRef.current = false;
    setIsSessionActive(false);
    
    // Stop any ongoing recording
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
    
    // Clean up stream
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    
    // Clean up audio context
    if (vadContextRef.current) {
      vadContextRef.current.close();
      vadContextRef.current = null;
    }
    
    // Clear analyser
    vadAnalyserRef.current = null;
    
    // Clear timeouts
    if (silenceTimeoutRef.current) {
      clearTimeout(silenceTimeoutRef.current);
      silenceTimeoutRef.current = null;
    }
    
    // Reset all state refs
    isSpeakingRef.current = false;
    isRecordingRef.current = false;
    isProcessingRef.current = false;
    isAISpeakingRef.current = false;
    
    setIsSpeaking(false);
    setIsRecording(false);
    
    console.log('✅ Voice session ended');
  };
  
  const monitorVoiceActivity = () => {
    if (!vadAnalyserRef.current) return;
    
    const bufferLength = vadAnalyserRef.current.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    let frameCount = 0;
    let voiceStartTime: number | null = null;
    let peakVolume = 0; // Track peak volume during speech
    
    const checkVoiceActivity = () => {
      // Check if session has ended or analyser destroyed
      if (!isSessionActiveRef.current || !vadAnalyserRef.current) {
        console.log('🛑 Voice monitoring stopped');
        return;
      }
      
      vadAnalyserRef.current.getByteFrequencyData(dataArray);
      
      // Calculate average volume
      const average = dataArray.reduce((a, b) => a + b) / bufferLength;
      
      // Voice activity threshold (adjust based on testing)
      const VOICE_THRESHOLD = 35; // Lowered for maximum sensitivity
      const SILENCE_THRESHOLD = 20; // Relative drop to detect silence
      const SILENCE_DURATION = 1500; // ms of silence before auto-processing
      const MIN_RECORDING_DURATION = 300; // Minimum 300ms to allow shorter phrases
      
      // Log audio level every 30 frames (~0.5 seconds) to avoid console spam
      frameCount++;
      if (frameCount % 30 === 0) {
        console.log(`🎵 Audio level: ${average.toFixed(2)} (Threshold: ${VOICE_THRESHOLD}, Peak: ${peakVolume.toFixed(2)}) - Speaking: ${isSpeakingRef.current}, Recording: ${isRecordingRef.current}`);
      }
      
      if (average > VOICE_THRESHOLD) {
        // Voice detected
        if (!isSpeakingRef.current && !isRecordingRef.current && !isProcessingRef.current && !isAISpeakingRef.current) {
          console.log('🎤 Voice detected, starting recording...');
          voiceStartTime = Date.now();
          peakVolume = average;
          isSpeakingRef.current = true;
          setIsSpeaking(true);
          startAutoRecording();
        } else if (isSpeakingRef.current) {
          // Update peak volume while speaking
          if (average > peakVolume) {
            peakVolume = average;
          }
          
          // Log why recording is NOT starting every 30 frames (only when NOT already speaking)
          if (frameCount % 30 === 0 && !isSpeakingRef.current) {
            const blockers = [];
            if (isSpeakingRef.current) blockers.push('isSpeaking=true');
            if (isRecordingRef.current) blockers.push('isRecording=true');
            if (isProcessingRef.current) blockers.push('isProcessing=true');
            if (isAISpeakingRef.current) blockers.push('isAISpeaking=true');
            
            console.log(`❌ Voice level ${average.toFixed(2)} > ${VOICE_THRESHOLD} but NOT recording. Blocked by: ${blockers.join(', ')}`);
          }
          
          // Check if volume has dropped significantly from peak (silence detection)
          const volumeDrop = peakVolume - average;
          if (volumeDrop > SILENCE_THRESHOLD) {
            // Volume dropped significantly - possible silence
            // Only start timer if not already started
            if (!silenceTimeoutRef.current && !isProcessingRef.current) {
              const recordingDuration = voiceStartTime ? Date.now() - voiceStartTime : 0;
              
              if (recordingDuration < MIN_RECORDING_DURATION) {
                console.log(`⏭️ Recording too short (${recordingDuration}ms), ignoring...`);
                // Stop recording without processing
                if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
                  mediaRecorderRef.current.stop();
                }
                isSpeakingRef.current = false;
                isRecordingRef.current = false;
                setIsSpeaking(false);
                setIsRecording(false);
                voiceStartTime = null;
                peakVolume = 0;
              } else {
                // Start silence timer ONCE
                console.log(`🔕 Silence detected (level: ${average.toFixed(2)}, peak: ${peakVolume.toFixed(2)}, drop: ${volumeDrop.toFixed(2)}) - starting ${SILENCE_DURATION}ms timer...`);
                silenceTimeoutRef.current = setTimeout(() => {
                  console.log(`🔇 Silence confirmed after ${recordingDuration}ms, processing speech...`);
                  isSpeakingRef.current = false;
                  setIsSpeaking(false);
                  stopAutoRecording();
                  voiceStartTime = null;
                  peakVolume = 0;
                }, SILENCE_DURATION);
              }
            }
          } else {
            // Voice still strong, reset any pending silence timer
            if (silenceTimeoutRef.current) {
              clearTimeout(silenceTimeoutRef.current);
              silenceTimeoutRef.current = null;
            }
          }
        }
      }
      
      // Continue monitoring only if session is still active
      if (isSessionActiveRef.current) {
        requestAnimationFrame(checkVoiceActivity);
      }
    };
    
    checkVoiceActivity();
  };
  
  const startAutoRecording = async () => {
    if (!streamRef.current || isRecordingRef.current) return;
    
    try {
      const mediaRecorder = new MediaRecorder(streamRef.current, {
        mimeType: 'audio/webm'
      });
      
      const audioChunks: Blob[] = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.push(event.data);
          console.log('📦 Audio chunk captured:', event.data.size, 'bytes');
        }
      };
      
      mediaRecorder.onstop = async () => {
        console.log('🛑 Recording stopped, total chunks:', audioChunks.length);
        if (audioChunks.length === 0) {
          console.error('❌ No audio chunks captured!');
          return;
        }
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        console.log('🎵 Auto-recorded audio:', audioBlob.size, 'bytes');
        console.log('🚀 Calling processRecordedAudio NOW...');
        await processRecordedAudio(audioBlob);
        console.log('✅ processRecordedAudio completed');
      };
      
      // Start recording with timeslice to ensure ondataavailable fires
      mediaRecorder.start(100); // Collect data every 100ms
      mediaRecorderRef.current = mediaRecorder;
      isRecordingRef.current = true;
      setIsRecording(true);
      
    } catch (error) {
      console.error('❌ Auto-recording error:', error);
    }
  };
  
  const stopAutoRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      isRecordingRef.current = false;
      setIsRecording(false);
    }
  };

  const playAudioFromBase64 = async (base64Audio: string) => {
    try {
      if (!audioRef.current) {
        console.error('❌ Audio element not found!');
        return;
      }

      console.log('🔓 Decoding base64 audio...');
      
      // Set AI speaking flag IMMEDIATELY to prevent recording AI's voice
      isAISpeakingRef.current = true;
      setIsAISpeaking(true);
      
      const audioData = atob(base64Audio);
      const arrayBuffer = new ArrayBuffer(audioData.length);
      const uint8Array = new Uint8Array(arrayBuffer);
      
      for (let i = 0; i < audioData.length; i++) {
        uint8Array[i] = audioData.charCodeAt(i);
      }
      
      const audioBlob = new Blob([uint8Array], { type: 'audio/wav' });
      console.log('🎵 Decoded audio blob size:', audioBlob.size, 'bytes');
      const audioUrl = URL.createObjectURL(audioBlob);
      
      audioRef.current.src = audioUrl;
      console.log('🎯 Audio source set, attempting playback...');
      
      // Setup visualization before playing
      if (!analyserRef.current) {
        setupAudioVisualization(audioRef.current);
      }
      
      // Return a promise that resolves when audio finishes
      return new Promise<void>((resolve, reject) => {
        if (!audioRef.current) {
          reject(new Error('Audio element not found'));
          return;
        }

        audioRef.current.onended = () => {
          console.log('🎵 Audio playback ended - ready for next question');
          isAISpeakingRef.current = false;
          setIsAISpeaking(false);
          stopVisualization();
          resolve();
        };
        
        audioRef.current.onerror = (error) => {
          console.error('❌ Audio playback error:', error);
          isAISpeakingRef.current = false;
          setIsAISpeaking(false);
          stopVisualization();
          reject(error);
        };
        
        audioRef.current.play()
          .then(() => {
            console.log('✅ Audio playback started successfully!');
          })
          .catch((playError) => {
            console.error('❌ Playback error:', playError);
            isAISpeakingRef.current = false;
            setIsAISpeaking(false);
            stopVisualization();
            reject(playError);
          });
      });
    } catch (error) {
      console.error('❌ Error playing audio from base64:', error);
      isAISpeakingRef.current = false;
      setIsAISpeaking(false);
      throw error;
    }
  };

  const processRecordedAudio = async (audioBlob: Blob) => {
    isProcessingRef.current = true;
    setIsProcessing(true);
    try {
      console.log('🎯 Processing audio blob:', {
        size: audioBlob.size,
        type: audioBlob.type
      });

      const formData = new FormData();
      formData.append('audio_file', audioBlob, `recording.${audioBlob.type.includes('wav') ? 'wav' : 'webm'}`);

      console.log('📤 Sending audio to server...');
      
      // Add timeout to prevent hanging forever
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        console.log('⏰ Request timeout after 30s - aborting...');
        controller.abort();
      }, 30000); // 30 second timeout
      
      try {
        const response = await fetch('http://localhost:8001/voice/process-audio', {
          method: 'POST',
          body: formData,
          signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        const data = await response.json();
      console.log('📥 Server response:', data);
      setVoiceResponse(data);

      if (data.status === 'success') {
        // Check if this is a fallback transcription
        if (data.debug_info?.is_fallback) {
          console.warn('⚠️ Received fallback transcription - speech recognition may have failed');
        }
        
        const newEntry = {
          timestamp: new Date().toLocaleTimeString(),
          user_input: data.transcription || '🎤 Voice input',
          ai_response: typeof data.ai_response === 'object' ? data.ai_response.text : data.ai_response || '',
          has_audio: !!data.audio_response
        };
        setConversationHistory(prev => [...prev, newEntry]);

        // Play audio response if available (already in the response as base64)
        if (data.audio_response) {
          console.log('🔊 Playing AI audio response...');
          await playAudioFromBase64(data.audio_response);
          console.log('✅ AI finished speaking - listening for next question...');
        } else {
          console.log('⚠️ No audio response in server reply - generating TTS for text');
          // Backend didn't send audio, so generate it from text
          const responseText = typeof data.ai_response === 'object' ? data.ai_response.text : data.ai_response;
          if (responseText) {
            await playTTSResponse(responseText);
          }
        }
      } else {
        console.error('❌ Server returned error:', data.error || 'Unknown error');
      }
      } catch (error: any) {
        clearTimeout(timeoutId);
        if (error.name === 'AbortError') {
          console.error('⏰ Request timed out - backend is stuck (probably pyttsx3 TTS issue)');
          setVoiceResponse({
            success: false,
            error: 'Request timed out. The backend TTS is stuck. Please restart the backend server.'
          });
        } else {
          console.error('❌ Fetch error:', error);
          setVoiceResponse({
            success: false,
            error: `Network error: ${error.message}`
          });
        }
      }
    } catch (error) {
      console.error('❌ Audio processing error:', error);
      setVoiceResponse({
        success: false,
        error: `Recording processing failed: ${error}`
      });
    } finally {
      isProcessingRef.current = false;
      setIsProcessing(false);
    }
  };

  const setupAudioVisualization = (audioElement: HTMLAudioElement) => {
    try {
      // Create audio context if it doesn't exist
      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      }

      // Create analyser node
      if (!analyserRef.current) {
        analyserRef.current = audioContextRef.current.createAnalyser();
        analyserRef.current.fftSize = 256;
      }

      // Connect audio element to analyser
      const source = audioContextRef.current.createMediaElementSource(audioElement);
      source.connect(analyserRef.current);
      analyserRef.current.connect(audioContextRef.current.destination);

      // Start visualization
      visualizeAudio();
    } catch (error) {
      console.error('Error setting up audio visualization:', error);
    }
  };

  const visualizeAudio = () => {
    if (!analyserRef.current || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const bufferLength = analyserRef.current.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const draw = () => {
      animationFrameRef.current = requestAnimationFrame(draw);

      analyserRef.current!.getByteFrequencyData(dataArray);

      // Set canvas size
      const width = canvas.width;
      const height = canvas.height;

      // Clear canvas with gradient background
      const gradient = ctx.createLinearGradient(0, 0, 0, height);
      gradient.addColorStop(0, '#1a1a2e');
      gradient.addColorStop(1, '#0f3460');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, width, height);

      // Draw frequency bars
      const barWidth = (width / bufferLength) * 2.5;
      let barHeight;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        barHeight = (dataArray[i] / 255) * height * 0.8;

        // Create gradient for bars
        const barGradient = ctx.createLinearGradient(0, height - barHeight, 0, height);
        barGradient.addColorStop(0, '#00d4ff');
        barGradient.addColorStop(0.5, '#0ea5e9');
        barGradient.addColorStop(1, '#3b82f6');

        ctx.fillStyle = barGradient;
        ctx.fillRect(x, height - barHeight, barWidth, barHeight);

        // Add glow effect
        ctx.shadowBlur = 10;
        ctx.shadowColor = '#00d4ff';

        x += barWidth + 1;
      }

      // Reset shadow
      ctx.shadowBlur = 0;
    };

    draw();
  };

  const stopVisualization = () => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
    
    // Clear canvas
    if (canvasRef.current) {
      const ctx = canvasRef.current.getContext('2d');
      if (ctx) {
        ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
      }
    }
  };

  const playTTSResponse = async (text: string) => {
    try {
      console.log('🔊 Requesting TTS for:', text);
      
      // Check if audio element exists
      if (!audioRef.current) {
        console.error('❌ Audio element not found!');
        return;
      }
      
      const response = await fetch('http://localhost:8001/voice/text-to-speech', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });

      console.log('📡 Response status:', response.status);
      const contentType = response.headers.get('content-type');
      console.log('📄 Content-Type:', contentType);
      
      if (contentType && contentType.includes('audio')) {
        // Direct audio response
        console.log('📥 Received direct audio response');
        const audioBlob = await response.blob();
        console.log('🎵 Audio blob size:', audioBlob.size, 'bytes');
        const audioUrl = URL.createObjectURL(audioBlob);
        
        audioRef.current.src = audioUrl;
        console.log('🎯 Audio source set, attempting playback...');
        
        // Setup visualization before playing
        if (!analyserRef.current) {
          setupAudioVisualization(audioRef.current);
        }
        
        setIsAISpeaking(true);
        
        // Add event listeners
        audioRef.current.onended = () => {
          console.log('🎵 Audio playback ended - ready for next question');
          setIsAISpeaking(false);
          stopVisualization();
          // Voice monitoring will automatically resume since it's in a requestAnimationFrame loop
        };
        
        audioRef.current.onerror = () => {
          console.error('❌ Audio playback error');
          setIsAISpeaking(false);
          stopVisualization();
        };
        
        try {
          await audioRef.current.play();
          console.log('✅ Audio playback started successfully!');
        } catch (playError) {
          console.error('❌ Playback error:', playError);
          setIsAISpeaking(false);
          stopVisualization();
          alert('Audio playback failed. Please check browser permissions or click to play manually.');
        }
      } else {
        // JSON response (might have base64 audio or error)
        const data = await response.json();
        console.log('📥 TTS response:', data.status);
        
        if (data.status === 'success' && data.audio_response) {
          // Decode base64 audio and play
          console.log('🔓 Decoding base64 audio...');
          const audioData = atob(data.audio_response);
          const arrayBuffer = new ArrayBuffer(audioData.length);
          const uint8Array = new Uint8Array(arrayBuffer);
          
          for (let i = 0; i < audioData.length; i++) {
            uint8Array[i] = audioData.charCodeAt(i);
          }
          
          const audioBlob = new Blob([uint8Array], { type: 'audio/wav' });
          console.log('🎵 Decoded audio blob size:', audioBlob.size, 'bytes');
          const audioUrl = URL.createObjectURL(audioBlob);
          
          audioRef.current.src = audioUrl;
          console.log('🎯 Audio source set, attempting playback...');
          
          // Setup visualization before playing
          if (!analyserRef.current) {
            setupAudioVisualization(audioRef.current);
          }
          
          setIsAISpeaking(true);
          
          // Add event listeners
          audioRef.current.onended = () => {
            console.log('🎵 Audio playback ended - ready for next question');
            setIsAISpeaking(false);
            stopVisualization();
            // Voice monitoring will automatically resume since it's in a requestAnimationFrame loop
          };
          
          audioRef.current.onerror = () => {
            console.error('❌ Audio playback error');
            setIsAISpeaking(false);
            stopVisualization();
          };
          
          try {
            await audioRef.current.play();
            console.log('✅ Base64 audio playback started successfully!');
          } catch (playError) {
            console.error('❌ Playback error:', playError);
            setIsAISpeaking(false);
            stopVisualization();
            alert('Audio playback failed. Please check browser permissions or click to play manually.');
          }
        } else {
          console.log('⚠️ No audio in response:', data.status, data.message || data.text);
        }
      }
    } catch (error) {
      console.error('❌ TTS playback failed:', error);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsProcessing(true);
    try {
      const formData = new FormData();
      formData.append('audio_file', file);

      const response = await fetch('http://localhost:8001/voice/process-audio', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      setVoiceResponse(data);

      if (data.status === 'success') {
        const newEntry = {
          timestamp: new Date().toLocaleTimeString(),
          user_input: data.transcription || `📁 ${file.name}`,
          ai_response: typeof data.ai_response === 'object' ? data.ai_response.text : data.ai_response || '',
          has_audio: !!data.audio_response
        };
        setConversationHistory(prev => [...prev, newEntry]);

        // Play TTS response if available
        const responseText = typeof data.ai_response === 'object' ? data.ai_response.text : data.ai_response;
        if (responseText) {
          await playTTSResponse(responseText);
        }
      }
    } catch (error) {
      setVoiceResponse({
        success: false,
        error: `File upload failed: ${error}`
      });
    } finally {
      setIsProcessing(false);
      // Reset the input
      event.target.value = '';
    }
  };

  const clearConversation = async () => {
    try {
      await fetch('http://localhost:8001/voice/clear-conversation', { method: 'POST' });
      setConversationHistory([]);
      setVoiceResponse(null);
    } catch (error) {
      console.error('Error clearing conversation:', error);
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          🎙️ Voice AI Assistant
        </h1>
        <p className="text-gray-600">
          Real-time voice conversations with AI powered by speech recognition and synthesis
        </p>
      </div>

      {/* Capabilities Status */}
      {capabilities && (
        <div className="bg-blue-50 rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-blue-800 mb-4">System Capabilities</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <div className={`text-sm ${capabilities.voice_components_available ? 'text-green-600' : 'text-red-600'}`}>
                Voice Components: {capabilities.voice_components_available ? '✅ Available' : '❌ Not Available'}
              </div>
              <div className="text-sm text-gray-600">
                STT Providers: {capabilities.supported_stt_providers?.join(', ') || 'None'}
              </div>
              <div className="text-sm text-gray-600">
                TTS Providers: {capabilities.supported_tts_providers?.join(', ') || 'None'}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600">
                AI Models: {capabilities.supported_ai_models?.join(', ') || 'Local'}
              </div>
              <div className="text-sm text-gray-600">
                Features: {capabilities.features?.length || 0} available
              </div>
            </div>
          </div>
          
          {!capabilities.voice_components_available && (
            <div className="mt-4 p-4 bg-yellow-50 rounded-lg">
              <h4 className="font-medium text-yellow-800">🔧 Setup Required:</h4>
              <div className="text-sm text-yellow-700 mt-2">
                Install voice libraries: <code>pip install speechrecognition pyttsx3 openai-whisper soundfile librosa</code>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Voice Configuration */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">🔧 Voice Configuration</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Speech-to-Text Provider
            </label>
            <select
              value={voiceConfig.stt_provider}
              onChange={(e) => setVoiceConfig({...voiceConfig, stt_provider: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="whisper">Whisper (OpenAI)</option>
              <option value="google">Google Speech</option>
              <option value="azure">Azure Speech</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Text-to-Speech Provider
            </label>
            <select
              value={voiceConfig.tts_provider}
              onChange={(e) => setVoiceConfig({...voiceConfig, tts_provider: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="pyttsx3">PyTTSx3 (Local)</option>
              <option value="elevenlabs">ElevenLabs</option>
              <option value="azure">Azure Speech</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              AI Model
            </label>
            <select
              value={voiceConfig.ai_model}
              onChange={(e) => setVoiceConfig({...voiceConfig, ai_model: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="local">Local AI Agent</option>
              <option value="openai">OpenAI GPT</option>
              <option value="anthropic">Anthropic Claude</option>
            </select>
          </div>
        </div>
        
        <button
          onClick={initializeVoiceAgent}
          disabled={isProcessing || isInitialized}
          className={`px-6 py-3 rounded-lg text-white font-medium ${
            isInitialized 
              ? 'bg-green-500 cursor-default' 
              : isProcessing 
                ? 'bg-gray-400' 
                : 'bg-blue-500 hover:bg-blue-600'
          }`}
        >
          {isInitialized ? '✅ Initialized' : isProcessing ? 'Initializing...' : '🚀 Initialize Voice Agent'}
        </button>
      </div>

      {/* Voice Controls */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">🎙️ Voice Controls</h2>
        
        {/* Session Mode - Continuous Conversation */}
        <div className="mb-6 p-6 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border-2 border-purple-200">
          <h3 className="text-lg font-semibold text-purple-800 mb-3">💬 Continuous Voice Session</h3>
          <p className="text-sm text-gray-600 mb-4">
            Start a session and speak anytime - AI will automatically detect when you're talking!
          </p>
          
          <button
            onClick={isSessionActive ? endVoiceSession : startVoiceSession}
            disabled={isProcessing}
            className={`w-full px-8 py-4 text-white rounded-lg font-bold text-lg transition-all ${
              isSessionActive 
                ? 'bg-red-500 hover:bg-red-600 shadow-lg shadow-red-500/50' 
                : 'bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 shadow-lg shadow-purple-500/50'
            } disabled:bg-gray-400 disabled:shadow-none`}
          >
            {isSessionActive ? '⏹️ End Session' : '🎬 Start Voice Session'}
          </button>
          
          {isSessionActive && (
            <div className="mt-4 space-y-3">
              <div className="flex items-center justify-between p-3 bg-white rounded-lg shadow-sm">
                <span className="text-sm font-medium text-gray-700">Session Status:</span>
                <span className="flex items-center">
                  <span className="animate-pulse w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  <span className="text-green-600 font-semibold">Active - Speak Anytime!</span>
                </span>
              </div>
              
              {isSpeaking && (
                <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <span className="text-sm font-medium text-blue-700">You are:</span>
                  <span className="flex items-center">
                    <span className="animate-pulse w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                    <span className="text-blue-600 font-semibold">Speaking...</span>
                  </span>
                </div>
              )}
              
              {isRecording && !isSpeaking && (
                <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                  <span className="text-sm font-medium text-yellow-700">Status:</span>
                  <span className="flex items-center">
                    <span className="animate-pulse w-2 h-2 bg-yellow-500 rounded-full mr-2"></span>
                    <span className="text-yellow-600 font-semibold">Processing...</span>
                  </span>
                </div>
              )}
            </div>
          )}
        </div>
        
        {/* Manual Mode - Original Buttons */}
        <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Manual Recording Mode</h3>
          <div className="flex flex-wrap gap-4 mb-4">
          {/* Microphone Recording Button */}
          <button
            onClick={isRecording ? stopRecording : startRecording}
            disabled={isProcessing || isSessionActive}
            className={`px-6 py-3 text-white rounded-lg font-medium transition-colors ${
              isRecording 
                ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
                : 'bg-blue-500 hover:bg-blue-600'
            } disabled:bg-gray-400`}
          >
            {isRecording ? '🔴 Stop Recording' : '🎤 Start Recording'}
          </button>

          <button
            onClick={testWithSampleAudio}
            disabled={isProcessing || isSessionActive}
            className="px-6 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:bg-gray-400"
          >
            {isProcessing ? 'Processing...' : '🎵 Test Voice AI'}
          </button>

          <button
            onClick={simpleTest}
            disabled={isProcessing || isSessionActive}
            className="px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:bg-gray-400"
          >
            ⚡ Quick Test
          </button>
          
          <button
            onClick={clearConversation}
            className="px-6 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
          >
            🗑️ Clear History
          </button>
        </div>
        </div>

        {isRecording && !isSessionActive && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
            <div className="flex items-center">
              <div className="animate-pulse w-3 h-3 bg-red-500 rounded-full mr-3"></div>
              <span className="text-red-700 font-medium">🎙️ Recording... Speak now!</span>
            </div>
            <p className="text-sm text-red-600 mt-2">Click "Stop Recording" when you're done speaking.</p>
          </div>
        )}

        {/* AI Audio Visualizer */}
        <div className={`mt-6 rounded-lg overflow-hidden transition-all duration-300 ${
          isAISpeaking ? 'shadow-lg shadow-blue-500/50' : 'opacity-50'
        }`}>
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-white font-semibold flex items-center">
                🔊 AI Voice Assistant
                {isAISpeaking && (
                  <span className="ml-3 flex items-center">
                    <span className="animate-pulse w-2 h-2 bg-green-400 rounded-full mr-2"></span>
                    <span className="text-sm text-green-200">Speaking...</span>
                  </span>
                )}
              </h3>
            </div>
            <canvas
              ref={canvasRef}
              width={800}
              height={200}
              className="w-full rounded-lg bg-gradient-to-br from-slate-900 to-slate-800"
              style={{ maxHeight: '200px' }}
            />
            <p className="text-blue-100 text-xs mt-2 text-center">
              {isAISpeaking 
                ? '🎵 Real-time audio frequency visualization' 
                : '⏸️ Waiting for AI response...'}
            </p>
          </div>
        </div>

        {/* Audio File Upload */}
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
          <input
            type="file"
            accept="audio/*"
            onChange={handleFileUpload}
            disabled={isProcessing}
            className="hidden"
            id="audio-upload"
          />
          <label
            htmlFor="audio-upload"
            className={`cursor-pointer inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 ${
              isProcessing ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            📁 Upload Audio File
          </label>
          <p className="text-sm text-gray-500 mt-2">
            Upload .wav, .mp3, .m4a, or other audio files for processing
          </p>
        </div>
        
        {isProcessing && (
          <div className="text-center py-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
            <p className="text-gray-600 mt-2">Processing audio...</p>
          </div>
        )}
      </div>

      {/* Latest Response */}
      {voiceResponse && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">💬 Latest Response</h2>
          {voiceResponse.success ? (
            <div>
              {voiceResponse.transcription && (
                <div className="mb-4">
                  <h3 className="font-medium text-gray-700">🎙️ You said:</h3>
                  <p className="bg-blue-50 p-3 rounded-lg">{voiceResponse.transcription}</p>
                </div>
              )}
              {voiceResponse.ai_response && (
                <div className="mb-4">
                  <h3 className="font-medium text-gray-700">🤖 AI Response:</h3>
                  <p className="bg-green-50 p-3 rounded-lg">
                    {typeof voiceResponse.ai_response === 'object' 
                      ? voiceResponse.ai_response.text 
                      : voiceResponse.ai_response}
                  </p>
                  {typeof voiceResponse.ai_response === 'object' && (
                    <div className="text-xs text-gray-500 mt-2">
                      Agent: {voiceResponse.ai_response.agent_type} | 
                      Confidence: {(voiceResponse.ai_response.confidence * 100).toFixed(0)}%
                    </div>
                  )}
                </div>
              )}
              {voiceResponse.note && (
                <div className="text-sm text-yellow-600 bg-yellow-50 p-3 rounded-lg">
                  💡 {voiceResponse.note}
                </div>
              )}
            </div>
          ) : (
            <div className="text-red-600 bg-red-50 p-3 rounded-lg">
              ❌ Error: {voiceResponse.error}
            </div>
          )}
        </div>
      )}

      {/* Conversation History */}
      {conversationHistory.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">📝 Conversation History</h2>
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {conversationHistory.map((entry, index) => (
              <div key={index} className="border-l-4 border-blue-500 pl-4">
                <div className="text-sm text-gray-500">{entry.timestamp}</div>
                <div className="font-medium text-gray-700">You: {entry.user_input}</div>
                <div className="text-gray-600">AI: {entry.ai_response}</div>
                {entry.has_audio && (
                  <div className="text-sm text-green-600">🔊 Audio response available</div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Hidden audio element for playback */}
      <audio ref={audioRef} style={{ display: 'none' }} />

      {/* Voice AI Architecture */}
      <div className="bg-gray-50 rounded-lg p-6 mt-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">🏗️ Voice AI Architecture & Models</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-700 mb-2">🎯 Recommended Models</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• <strong>STT:</strong> OpenAI Whisper (best accuracy)</li>
              <li>• <strong>TTS:</strong> ElevenLabs (best quality)</li>
              <li>• <strong>AI:</strong> Local Agent (no API keys)</li>
              <li>• <strong>LiveKit:</strong> Real-time streaming</li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-700 mb-2">📋 Installation Commands</h4>
            <div className="text-xs bg-gray-100 p-2 rounded font-mono">
              pip install speechrecognition<br/>
              pip install pyttsx3<br/>
              pip install openai-whisper<br/>
              pip install soundfile librosa<br/>
              pip install elevenlabs<br/>
              pip install livekit livekit-agents
            </div>
          </div>
        </div>
        
        <div className="mt-4 p-4 bg-blue-50 rounded-lg">
          <h4 className="font-medium text-blue-800">🚀 Voice AI Workflow:</h4>
          <div className="text-sm text-blue-700 mt-2">
            <strong>Input Audio</strong> → <strong>Speech-to-Text</strong> → <strong>AI Processing</strong> → <strong>Text-to-Speech</strong> → <strong>Audio Output</strong>
          </div>
        </div>
      </div>
    </div>
  );
}