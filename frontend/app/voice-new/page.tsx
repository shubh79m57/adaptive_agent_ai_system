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
  ai_response?: string;
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
      const response = await fetch('/api/voice/capabilities');
      const data = await response.json();
      setCapabilities(data);
    } catch (error) {
      console.error('Error loading capabilities:', error);
    }
  };

  const initializeVoiceAgent = async () => {
    try {
      setIsProcessing(true);
      const response = await fetch('/api/voice/initialize', {
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

  const testWithSampleAudio = async () => {
    setIsProcessing(true);
    try {
      // Simulate audio processing for demo
      const response = await fetch('/api/voice/process-audio', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          audio_data: 'mock_audio_data',
          format: 'wav',
          config: voiceConfig
        })
      });

      const data = await response.json();
      setVoiceResponse(data);
      
      if (data.success) {
        const newEntry = {
          timestamp: new Date().toLocaleTimeString(),
          user_input: data.transcription || '🎵 Test audio input',
          ai_response: data.ai_response || '',
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

  const clearConversation = async () => {
    try {
      await fetch('/api/voice/clear-conversation', { method: 'POST' });
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
          <button
            onClick={testWithSampleAudio}
            disabled={isProcessing}
            className="px-6 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:bg-gray-400"
          >
            {isProcessing ? 'Processing...' : '🎵 Test Voice AI'}
          </button>
          
          <button
            onClick={clearConversation}
            className="px-6 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
          >
            🗑️ Clear History
          </button>
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
                  <p className="bg-green-50 p-3 rounded-lg">{voiceResponse.ai_response}</p>
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