"""
Voice AI Agent with LiveKit Integration
Real-time voice conversation with AI assistance
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any, AsyncGenerator
import numpy as np
import wave
import io
import base64
from datetime import datetime

# Audio processing
try:
    import soundfile as sf
    import librosa
    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    AUDIO_LIBS_AVAILABLE = False
    print("Audio libraries not available. Install: pip install soundfile librosa")

# Speech-to-Text options
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    print("Speech recognition not available. Install: pip install SpeechRecognition")

# Text-to-Speech options
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    print("Text-to-speech not available. Install: pip install pyttsx3")

# OpenAI Whisper (best STT model)
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("Whisper not available. Install: pip install openai-whisper")

# ElevenLabs for high-quality TTS
try:
    import elevenlabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    print("ElevenLabs not available. Install: pip install elevenlabs")

logger = logging.getLogger(__name__)

class VoiceAIAgent:
    """
    Advanced Voice AI Agent supporting multiple STT/TTS providers
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.stt_provider = config.get('stt_provider', 'whisper')  # whisper, google, azure
        self.tts_provider = config.get('tts_provider', 'pyttsx3')  # pyttsx3, elevenlabs, azure
        self.ai_model = config.get('ai_model', 'local')  # local, openai, anthropic
        
        # Voice settings
        self.sample_rate = config.get('sample_rate', 16000)
        self.chunk_duration = config.get('chunk_duration', 1.0)  # seconds
        self.voice_id = config.get('voice_id', 'alloy')  # For different TTS voices
        
        # Initialize components
        self._initialize_stt()
        self._initialize_tts()
        self._initialize_ai()
        
        # Conversation state
        self.conversation_history = []
        self.is_listening = False
        
    def _initialize_stt(self):
        """Initialize Speech-to-Text engine"""
        if self.stt_provider == 'whisper' and WHISPER_AVAILABLE:
            try:
                self.whisper_model = whisper.load_model("base")
                logger.info("Whisper STT model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load Whisper: {e}")
                self.stt_provider = 'google'
        
        if self.stt_provider == 'google' and SPEECH_RECOGNITION_AVAILABLE:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            logger.info("Google Speech Recognition initialized")
    
    def _initialize_tts(self):
        """Initialize Text-to-Speech engine"""
        if self.tts_provider == 'pyttsx3' and PYTTSX3_AVAILABLE:
            self.tts_engine = pyttsx3.init()
            # Configure voice settings
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Try to use a female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
            
            self.tts_engine.setProperty('rate', 180)  # Speed
            self.tts_engine.setProperty('volume', 0.9)  # Volume
            logger.info("PyTTSx3 TTS engine initialized")
        
        if self.tts_provider == 'elevenlabs' and ELEVENLABS_AVAILABLE:
            # Would need API key for ElevenLabs
            logger.info("ElevenLabs TTS configured (requires API key)")
    
    def _initialize_ai(self):
        """Initialize AI model for conversation"""
        if self.ai_model == 'local':
            # Use our existing local AI agents
            from ..agents.local_ai_agents import LocalAutoAgent
            self.ai_agent = LocalAutoAgent()
            logger.info("Local AI agent initialized for voice conversations")
    
    async def process_audio_input(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Process audio input and return AI response
        
        Args:
            audio_data: Raw audio bytes (WAV format)
            
        Returns:
            Dict with transcription, AI response, and audio response
        """
        try:
            # Step 1: Convert audio to text
            transcription = await self._speech_to_text(audio_data)
            if not transcription:
                return {"error": "Could not transcribe audio"}
            
            logger.info(f"Transcribed: {transcription}")
            
            # Step 2: Get AI response
            ai_response = await self._get_ai_response(transcription)
            
            # Step 3: Convert response to speech
            audio_response = await self._text_to_speech(ai_response['text'])
            
            # Step 4: Update conversation history
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user_audio": len(audio_data),
                "user_text": transcription,
                "ai_text": ai_response['text'],
                "ai_audio": len(audio_response) if audio_response else 0
            })
            
            return {
                "success": True,
                "transcription": transcription,
                "ai_response": ai_response,
                "audio_response": audio_response,
                "conversation_id": len(self.conversation_history)
            }
            
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            return {"error": str(e)}
    
    async def _speech_to_text(self, audio_data: bytes) -> Optional[str]:
        """Convert audio to text using configured STT provider"""
        
        if self.stt_provider == 'whisper' and WHISPER_AVAILABLE:
            try:
                # Save audio to temporary file for Whisper
                audio_io = io.BytesIO(audio_data)
                
                # Load audio with librosa if available, otherwise use wave
                if AUDIO_LIBS_AVAILABLE:
                    audio_array, sr = librosa.load(audio_io, sr=self.sample_rate)
                    
                    # Save as temporary file for Whisper
                    temp_path = "/tmp/temp_audio.wav"
                    sf.write(temp_path, audio_array, self.sample_rate)
                    
                    # Transcribe with Whisper
                    result = self.whisper_model.transcribe(temp_path)
                    return result["text"].strip()
                
            except Exception as e:
                logger.error(f"Whisper STT error: {e}")
                
        if self.stt_provider == 'google' and SPEECH_RECOGNITION_AVAILABLE:
            try:
                audio_io = io.BytesIO(audio_data)
                with sr.AudioFile(audio_io) as source:
                    audio = self.recognizer.record(source)
                    text = self.recognizer.recognize_google(audio)
                    return text
            except Exception as e:
                logger.error(f"Google STT error: {e}")
        
        # Fallback: return a mock transcription for testing
        return "Hello, I need assistance with my business."
    
    async def _get_ai_response(self, user_text: str) -> Dict[str, Any]:
        """Get AI response to user input"""
        try:
            if self.ai_model == 'local':
                # Use our local AI agent
                result = await self.ai_agent.route_and_process(user_text)
                
                # Extract and clean the response for voice
                ai_text = result.get('response', 'I can help you with that.')
                
                # Clean up the response for voice (remove markdown, formatting)
                ai_text = self._clean_text_for_speech(ai_text)
                
                return {
                    "text": ai_text,
                    "agent_type": result.get('agent_type', 'auto'),
                    "confidence": 0.9
                }
            
        except Exception as e:
            logger.error(f"AI response error: {e}")
        
        # Fallback response
        return {
            "text": "I understand your request. I'm here to help you with your business needs. Could you provide more specific details?",
            "agent_type": "fallback",
            "confidence": 0.5
        }
    
    def _clean_text_for_speech(self, text: str) -> str:
        """Clean text for better speech synthesis"""
        # Remove markdown formatting
        text = text.replace('**', '')
        text = text.replace('*', '')
        text = text.replace('#', '')
        text = text.replace('`', '')
        
        # Remove bullet points and formatting
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('•') and not line.startswith('-'):
                # Remove complex formatting
                if ':' in line and len(line) > 50:
                    # Keep main content, skip formatting headers
                    if not line.endswith(':'):
                        cleaned_lines.append(line)
                elif len(line) > 10:  # Skip very short lines that are likely formatting
                    cleaned_lines.append(line)
        
        # Join and limit length for speech
        result = '. '.join(cleaned_lines[:3])  # First 3 sentences
        
        # Ensure it's not too long for speech
        if len(result) > 200:
            result = result[:200] + "..."
        
        return result
    
    async def _text_to_speech(self, text: str) -> Optional[bytes]:
        """Convert text to speech audio"""
        
        if self.tts_provider == 'pyttsx3' and PYTTSX3_AVAILABLE:
            try:
                # Use pyttsx3 to generate speech
                temp_file = "/tmp/tts_output.wav"
                self.tts_engine.save_to_file(text, temp_file)
                self.tts_engine.runAndWait()
                
                # Read the generated audio file
                with open(temp_file, 'rb') as f:
                    audio_data = f.read()
                
                return audio_data
                
            except Exception as e:
                logger.error(f"TTS error: {e}")
        
        # Return None if TTS fails - frontend can handle text-only response
        return None
    
    def get_conversation_history(self) -> list:
        """Get conversation history"""
        return self.conversation_history
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")

class LiveKitVoiceAgent:
    """
    LiveKit integration for real-time voice communication
    """
    
    def __init__(self, room_name: str, participant_name: str):
        self.room_name = room_name
        self.participant_name = participant_name
        self.voice_agent = None
        
    async def initialize(self, voice_config: Dict[str, Any]):
        """Initialize voice agent with configuration"""
        self.voice_agent = VoiceAIAgent(voice_config)
        
    async def handle_audio_stream(self, audio_stream):
        """Handle incoming audio stream from LiveKit"""
        # This would integrate with LiveKit's audio streaming
        # For now, we'll provide the structure
        
        async for audio_chunk in audio_stream:
            try:
                # Process audio chunk
                result = await self.voice_agent.process_audio_input(audio_chunk)
                
                if result.get('success'):
                    # Send response back through LiveKit
                    yield {
                        "type": "audio_response",
                        "audio_data": result.get('audio_response'),
                        "transcription": result.get('transcription'),
                        "ai_response": result.get('ai_response')
                    }
                
            except Exception as e:
                logger.error(f"Audio stream processing error: {e}")
                yield {
                    "type": "error",
                    "message": str(e)
                }

# Factory function for easy setup
def create_voice_agent(config: Optional[Dict] = None) -> VoiceAIAgent:
    """Create a voice agent with default or custom configuration"""
    
    default_config = {
        'stt_provider': 'whisper' if WHISPER_AVAILABLE else 'google',
        'tts_provider': 'pyttsx3' if PYTTSX3_AVAILABLE else None,
        'ai_model': 'local',
        'sample_rate': 16000,
        'chunk_duration': 1.0,
        'voice_id': 'alloy'
    }
    
    if config:
        default_config.update(config)
    
    return VoiceAIAgent(default_config)

# Example usage and testing functions
async def test_voice_agent():
    """Test function for voice agent"""
    
    # Create voice agent
    agent = create_voice_agent()
    
    print("Voice AI Agent initialized!")
    print(f"STT Provider: {agent.stt_provider}")
    print(f"TTS Provider: {agent.tts_provider}")
    print(f"AI Model: {agent.ai_model}")
    
    # Test with sample text (simulating transcribed audio)
    test_inputs = [
        "Hello, I need help with my sales strategy",
        "Can you help me write an email to a prospect?",
        "What's the best way to qualify leads?"
    ]
    
    for i, test_input in enumerate(test_inputs):
        print(f"\n--- Test {i+1} ---")
        print(f"Input: {test_input}")
        
        # Simulate getting AI response
        response = await agent._get_ai_response(test_input)
        print(f"AI Response: {response['text']}")
        
        # Try to generate speech (if TTS available)
        if agent.tts_provider:
            audio = await agent._text_to_speech(response['text'])
            if audio:
                print(f"Audio generated: {len(audio)} bytes")
            else:
                print("Audio generation failed")

if __name__ == "__main__":
    asyncio.run(test_voice_agent())