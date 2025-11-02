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

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    loadCapabilities();
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
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          sampleRate: 16000,  // Use 16kHz for better speech recognition
          channelCount: 1,    // Mono audio
          echoCancellation: true,
          noiseSuppression: true
        } 
      });
      
      // Use Web Audio API to convert to WAV format
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const source = audioContext.createMediaStreamSource(stream);
      const processor = audioContext.createScriptProcessor(4096, 1, 1);
      
      const audioChunks: Float32Array[] = [];
      
      processor.onaudioprocess = (event) => {
        const inputData = event.inputBuffer.getChannelData(0);
        audioChunks.push(new Float32Array(inputData));
      };
      
      source.connect(processor);
      processor.connect(audioContext.destination);
      
      console.log('✅ Recording started with Web Audio API (16kHz mono WAV)');
      setIsRecording(true);
      
      // Store references for stopping
      (window as any).audioContext = audioContext;
      (window as any).audioChunks = audioChunks;
      (window as any).audioStream = stream;
      
    } catch (error) {
      console.error('Microphone access error:', error);
      alert(`Error accessing microphone: ${error}`);
    }
  };

  const stopRecording = async () => {
    if (!isRecording) return;
    
    setIsRecording(false);
    
    try {
      // Get audio data from Web Audio API
      const audioChunks = (window as any).audioChunks;
      const audioContext = (window as any).audioContext;
      const stream = (window as any).audioStream;
      
      if (!audioChunks || audioChunks.length === 0) {
        console.error('No audio data recorded');
        return;
      }
      
      // Combine all audio chunks
      const totalLength = audioChunks.reduce((acc: number, chunk: Float32Array) => acc + chunk.length, 0);
      const combinedAudio = new Float32Array(totalLength);
      let offset = 0;
      
      for (const chunk of audioChunks) {
        combinedAudio.set(chunk, offset);
        offset += chunk.length;
      }
      
      console.log(`🎵 Recorded ${combinedAudio.length} audio samples`);
      
      // Convert Float32Array to WAV format
      const wavBuffer = float32ArrayToWav(combinedAudio, 16000);
      const wavBlob = new Blob([wavBuffer], { type: 'audio/wav' });
      
      console.log(`✅ Created WAV blob: ${wavBlob.size} bytes`);
      
      // Clean up
      stream.getTracks().forEach((track: MediaStreamTrack) => track.stop());
      audioContext.close();
      
      // Process the WAV audio
      await processRecordedAudio(wavBlob);
      
    } catch (error) {
      console.error('Error stopping recording:', error);
    }
  };

  // Helper function to convert Float32Array to WAV format
  const float32ArrayToWav = (float32Array: Float32Array, sampleRate: number): ArrayBuffer => {
    const length = float32Array.length;
    const buffer = new ArrayBuffer(44 + length * 2);
    const view = new DataView(buffer);
    
    // WAV header
    const writeString = (offset: number, string: string) => {
      for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
      }
    };
    
    writeString(0, 'RIFF');
    view.setUint32(4, 36 + length * 2, true);
    writeString(8, 'WAVE');
    writeString(12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, 1, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * 2, true);
    view.setUint16(32, 2, true);
    view.setUint16(34, 16, true);
    writeString(36, 'data');
    view.setUint32(40, length * 2, true);
    
    // Convert float samples to 16-bit PCM
    let offset = 44;
    for (let i = 0; i < length; i++) {
      const sample = Math.max(-1, Math.min(1, float32Array[i]));
      view.setInt16(offset, sample * 0x7FFF, true);
      offset += 2;
    }
    
    return buffer;
  };

  const processRecordedAudio = async (audioBlob: Blob) => {
    setIsProcessing(true);
    try {
      console.log('Processing audio blob:', {
        size: audioBlob.size,
        type: audioBlob.type
      });

      const formData = new FormData();
      formData.append('audio_file', audioBlob, `recording.${audioBlob.type.includes('wav') ? 'wav' : 'webm'}`);

      console.log('Sending audio to server...');
      const response = await fetch('http://localhost:8001/voice/process-audio', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      console.log('Server response:', data);
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

        // Play TTS response if available
        const responseText = typeof data.ai_response === 'object' ? data.ai_response.text : data.ai_response;
        if (responseText) {
          await playTTSResponse(responseText);
        }
      }
    } catch (error) {
      console.error('Audio processing error:', error);
      setVoiceResponse({
        success: false,
        error: `Recording processing failed: ${error}`
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const playTTSResponse = async (text: string) => {
    try {
      const response = await fetch('http://localhost:8001/voice/text-to-speech', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });

      const data = await response.json();
      if (data.status === 'success') {
        // The TTS engine will play the audio directly on the server
        // For local PyTTSx3, the audio plays through system speakers
        console.log('TTS response played:', data.message);
      }
    } catch (error) {
      console.error('TTS playback failed:', error);
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
        <div className="flex flex-wrap gap-4 mb-4">
          {/* Microphone Recording Button */}
          <button
            onClick={isRecording ? stopRecording : startRecording}
            disabled={isProcessing}
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
            disabled={isProcessing}
            className="px-6 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:bg-gray-400"
          >
            {isProcessing ? 'Processing...' : '🎵 Test Voice AI'}
          </button>

          <button
            onClick={simpleTest}
            disabled={isProcessing}
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

        {isRecording && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
            <div className="flex items-center">
              <div className="animate-pulse w-3 h-3 bg-red-500 rounded-full mr-3"></div>
              <span className="text-red-700 font-medium">🎙️ Recording... Speak now!</span>
            </div>
            <p className="text-sm text-red-600 mt-2">Click "Stop Recording" when you're done speaking.</p>
          </div>
        )}

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