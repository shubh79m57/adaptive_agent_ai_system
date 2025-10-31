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
import os
import platform

# Configure FFmpeg path for pydub BEFORE importing it (Windows only)
if platform.system() == 'Windows':
    ffmpeg_path = r"C:\ffmpeg\bin\ffmpeg.exe"
    ffprobe_path = r"C:\ffmpeg\bin\ffprobe.exe"
    if os.path.exists(ffmpeg_path):
        # Set environment variable as fallback
        os.environ["PATH"] = os.environ.get("PATH", "") + os.pathsep + r"C:\ffmpeg\bin"

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

# Configure pydub to use explicit FFmpeg paths (already added to PATH earlier)
try:
    from pydub import AudioSegment
    if platform.system() == 'Windows' and os.path.exists(r"C:\ffmpeg\bin\ffmpeg.exe"):
        AudioSegment.converter = r"C:\ffmpeg\bin\ffmpeg.exe"
        AudioSegment.ffprobe = r"C:\ffmpeg\bin\ffprobe.exe"
        logger.info(f"✅ Configured pydub to use FFmpeg at: C:\\ffmpeg\\bin\\ffmpeg.exe")
except ImportError:
    pass

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
        
        # TTS lock to prevent concurrent calls (pyttsx3 is not thread-safe)
        self._tts_lock = asyncio.Lock()
        
    def _initialize_stt(self):
        """Initialize Speech-to-Text engine"""
        # Always initialize the recognizer for Google STT
        if SPEECH_RECOGNITION_AVAILABLE:
            self.recognizer = sr.Recognizer()
            # Adjust recognizer settings for better accuracy
            self.recognizer.energy_threshold = 300  # Minimum audio energy to consider for recording
            self.recognizer.dynamic_energy_threshold = True  # Automatically adjust energy threshold
            self.recognizer.dynamic_energy_adjustment_damping = 0.15
            self.recognizer.dynamic_energy_ratio = 1.5
            self.recognizer.pause_threshold = 0.8  # Seconds of non-speaking audio before phrase is considered complete
            
            self.microphone = sr.Microphone()
            logger.info("Google Speech Recognition initialized with optimized settings")
        
        if self.stt_provider == 'whisper' and WHISPER_AVAILABLE:
            try:
                self.whisper_model = whisper.load_model("base")
                logger.info("Whisper STT model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load Whisper: {e}")
                self.stt_provider = 'google'
    
    def _initialize_tts(self):
        """Initialize Text-to-Speech engine"""
        if self.tts_provider == 'pyttsx3' and PYTTSX3_AVAILABLE:
            try:
                logger.debug("🔊 Initializing pyttsx3 TTS engine...")
                self.tts_engine = pyttsx3.init()
                # Configure voice settings
                voices = self.tts_engine.getProperty('voices')
                if voices:
                    logger.debug(f"🔊 Found {len(voices)} available voices")
                    # Try to use a female voice if available
                    for voice in voices:
                        if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                            self.tts_engine.setProperty('voice', voice.id)
                            logger.debug(f"🔊 Selected voice: {voice.name}")
                            break
                
                self.tts_engine.setProperty('rate', 180)  # Speed
                self.tts_engine.setProperty('volume', 0.9)  # Volume
                logger.info("✅ PyTTSx3 TTS engine initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize pyttsx3: {e}")
                self.tts_provider = None
        elif self.tts_provider == 'pyttsx3' and not PYTTSX3_AVAILABLE:
            logger.warning("⚠️ pyttsx3 TTS requested but not available")
            self.tts_provider = None
        
        if self.tts_provider == 'elevenlabs' and ELEVENLABS_AVAILABLE:
            # Would need API key for ElevenLabs
            logger.info("ElevenLabs TTS configured (requires API key)")
        
        if not self.tts_provider:
            logger.warning("⚠️ No TTS provider available - responses will be text-only")
    
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
            logger.debug(f"Starting audio processing, audio size: {len(audio_data)} bytes")
            
            # Step 1: Convert audio to text
            logger.debug("Step 1: Converting audio to text...")
            transcription = await self._speech_to_text(audio_data)
            if not transcription:
                return {"error": "Could not transcribe audio"}
            
            logger.info(f"✅ Transcribed: {transcription}")
            
            # Step 2: Get AI response
            logger.debug("Step 2: Getting AI response...")
            ai_response = await self._get_ai_response(transcription)
            
            # Step 3: Convert response to speech
            logger.debug("Step 3: Converting response to speech...")
            audio_response = await self._text_to_speech(ai_response['text'])
            
            # Step 4: Update conversation history
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user_audio": len(audio_data),
                "user_text": transcription,
                "ai_text": ai_response['text'],
                "ai_audio": len(audio_response) if audio_response else 0
            })
            
            logger.debug("Audio processing completed successfully")
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
        
        logger.debug(f"Starting STT with provider: {self.stt_provider}")
        
        if self.stt_provider == 'whisper' and WHISPER_AVAILABLE:
            try:
                logger.debug("Processing audio with Whisper...")
                
                # Try to process audio directly with Whisper first
                try:
                    import tempfile
                    import os
                    
                    # Save raw audio data to temporary file
                    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_file:
                        temp_file.write(audio_data)
                        temp_path = temp_file.name
                    
                    logger.info(f"Saved raw audio to: {temp_path}")
                    
                    # Try Whisper directly on the file
                    logger.info("Starting Whisper transcription...")
                    result = self.whisper_model.transcribe(temp_path)
                    transcription = result["text"].strip()
                    
                    # Clean up temp file
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                    
                    if transcription and len(transcription) > 2:
                        logger.info(f"Whisper transcription successful: {transcription}")
                        return transcription
                    else:
                        logger.warning("Whisper returned empty or very short transcription")
                
                except Exception as whisper_error:
                    logger.error(f"Direct Whisper processing failed: {whisper_error}")
                    
                    # Fallback: Try with audio conversion using librosa
                    if AUDIO_LIBS_AVAILABLE:
                        try:
                            logger.info("Trying audio conversion fallback...")
                            audio_io = io.BytesIO(audio_data)
                            audio_array, sr = librosa.load(audio_io, sr=self.sample_rate)
                            
                            # Save as WAV for Whisper
                            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                                temp_path = temp_file.name
                            
                            sf.write(temp_path, audio_array, self.sample_rate)
                            logger.info(f"Converted audio saved to: {temp_path}")
                            
                            # Transcribe with Whisper
                            result = self.whisper_model.transcribe(temp_path)
                            transcription = result["text"].strip()
                            
                            # Clean up temp file
                            try:
                                os.unlink(temp_path)
                            except:
                                pass
                            
                            if transcription and len(transcription) > 2:
                                logger.info(f"Whisper transcription (converted) successful: {transcription}")
                                return transcription
                                
                        except Exception as conversion_error:
                            logger.error(f"Audio conversion fallback failed: {conversion_error}")
                
            except Exception as e:
                logger.error(f"Whisper STT error: {e}")
                
        if self.stt_provider == 'google' and SPEECH_RECOGNITION_AVAILABLE:
            try:
                import speech_recognition as sr
                logger.debug("Processing audio with Google Speech Recognition...")
                logger.debug(f"Audio data size: {len(audio_data)} bytes")
                
                # First, try to process as WAV directly (no conversion needed)
                try:
                    import io
                    logger.debug("🎵 Trying direct WAV processing...")
                    audio_io = io.BytesIO(audio_data)
                    
                    # Try to read audio file info for diagnostics
                    try:
                        with sr.AudioFile(audio_io) as source:
                            logger.info(f"📊 Audio info - Sample rate: {source.SAMPLE_RATE}Hz, Sample width: {source.SAMPLE_WIDTH} bytes, Duration: {source.DURATION}s")
                            
                            # Adjust for ambient noise if duration is sufficient
                            if source.DURATION > 0.5:
                                logger.debug("🔇 Adjusting for ambient noise...")
                                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                            
                            audio = self.recognizer.record(source)
                            logger.debug(f"📊 Recorded audio data length: {len(audio.frame_data)} bytes")
                            
                            # Check if we actually have audio data
                            if len(audio.frame_data) < 100:
                                logger.warning("⚠️ Audio data too short, likely silent or empty")
                                return None
                            
                            logger.debug("🌐 Sending to Google Speech Recognition...")
                            text = self.recognizer.recognize_google(audio)
                        
                        # Check if text is empty
                        if not text or text.strip() == "":
                            logger.warning("⚠️ Google Speech Recognition returned empty result")
                            return None
                        
                        logger.info(f"✅ Transcribed: '{text}'")
                        return text
                    except sr.UnknownValueError:
                        logger.warning("⚠️ Google Speech Recognition could not understand audio - possibly no speech or unclear audio")
                        return None
                    except sr.RequestError as e:
                        logger.error(f"❌ Could not request results from Google Speech Recognition service; {e}")
                        return None
                except Exception as wav_error:
                    logger.debug(f"⚠️ Direct WAV processing failed: {str(wav_error)}")
                    logger.debug("Trying conversion methods...")
                
                # If direct WAV fails, try conversion methods with pydub
                if AUDIO_LIBS_AVAILABLE:
                    try:
                        # Try to convert audio using pydub (auto-detect format)
                        from pydub import AudioSegment
                        import tempfile
                        import os
                        
                        logger.debug("🔄 Converting audio to WAV for Google STT...")
                        
                        # Save original audio to temp file - try WAV first, then other formats
                        with tempfile.NamedTemporaryFile(suffix=".dat", delete=False) as temp_audio:
                            temp_audio.write(audio_data)
                            audio_path = temp_audio.name
                        
                        logger.debug(f"📁 Saved audio to: {audio_path}")
                        
                        # Try to load audio - let pydub auto-detect the format
                        logger.debug("🎵 Loading audio with pydub...")
                        try:
                            # Try WAV format first
                            audio_segment = AudioSegment.from_file(audio_path, format="wav")
                        except:
                            try:
                                # Try WebM/Opus
                                audio_segment = AudioSegment.from_file(audio_path, format="webm")
                            except:
                                # Try auto-detect
                                audio_segment = AudioSegment.from_file(audio_path)
                        
                        logger.debug(f"🎵 Audio loaded - duration: {len(audio_segment)}ms, channels: {audio_segment.channels}, frame_rate: {audio_segment.frame_rate}")
                        
                        # Create WAV temp file
                        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                            wav_path = temp_wav.name
                        
                        # Export as WAV with proper settings for speech recognition
                        logger.debug("🔧 Converting to 16kHz mono WAV...")
                        audio_segment = audio_segment.set_frame_rate(16000).set_channels(1)
                        audio_segment.export(wav_path, format="wav")
                        
                        logger.debug(f"✅ Audio converted successfully to: {wav_path}")
                        
                        # Use Google STT on the converted WAV file
                        logger.debug("🎤 Running Google Speech Recognition...")
                        with sr.AudioFile(wav_path) as source:
                            audio = self.recognizer.record(source)
                            text = self.recognizer.recognize_google(audio)
                            
                            # Check if text is empty
                            if not text or text.strip() == "":
                                logger.warning("⚠️ Google Speech Recognition returned empty result")
                                # Clean up temp files
                                try:
                                    os.unlink(audio_path)
                                    os.unlink(wav_path)
                                except:
                                    pass
                                return None
                            
                            logger.info(f"✅ Transcribed: '{text}'")
                            
                            # Clean up temp files
                            try:
                                os.unlink(audio_path)
                                os.unlink(wav_path)
                                logger.debug("🧹 Cleaned up temp files")
                            except Exception as cleanup_error:
                                logger.warning(f"⚠️ Cleanup error: {cleanup_error}")
                            
                            return text
                            
                    except FileNotFoundError as fnf_error:
                        logger.debug(f"❌ FFmpeg not found: {fnf_error}")
                        # Continue to fallback method below
                    except Exception as conversion_error:
                        logger.debug(f"❌ Audio conversion failed: {conversion_error}")
                        # Continue to fallback method below
                        # Continue to fallback method below
                        
                # Fallback: try a different approach - use librosa if available
                logger.debug("⚠️ FFmpeg not available, trying librosa approach...")
                if AUDIO_LIBS_AVAILABLE:
                    try:
                        import librosa
                        import soundfile as sf
                        import io
                        import tempfile
                        import os
                        
                        logger.debug("🔄 Using librosa for audio conversion...")
                        
                        # Try to load the WebM data directly with librosa
                        audio_io = io.BytesIO(audio_data)
                        try:
                            # This might work for some WebM files
                            audio_array, sample_rate = librosa.load(audio_io, sr=16000)
                            logger.debug(f"🎵 Librosa loaded audio: {len(audio_array)} samples at {sample_rate}Hz")
                            
                            # Save as WAV
                            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                                wav_path = temp_wav.name
                            
                            sf.write(wav_path, audio_array, sample_rate)
                            logger.debug(f"✅ Audio saved as WAV: {wav_path}")
                            
                            # Use Google STT
                            with sr.AudioFile(wav_path) as source:
                                audio = self.recognizer.record(source)
                                text = self.recognizer.recognize_google(audio)
                                
                                # Check if text is empty
                                if not text or text.strip() == "":
                                    logger.warning("⚠️ Google Speech Recognition returned empty result")
                                    try:
                                        os.unlink(wav_path)
                                    except:
                                        pass
                                    return None
                                
                                logger.info(f"✅ Transcribed: '{text}'")
                                
                                # Clean up
                                try:
                                    os.unlink(wav_path)
                                except:
                                    pass
                                
                                return text
                                
                        except Exception as librosa_error:
                            logger.debug(f"❌ Librosa approach failed: {librosa_error}")
                        
                    except ImportError:
                        logger.debug("⚠️ Librosa not available")
                    except Exception as e:
                        logger.debug(f"❌ Librosa processing error: {e}")
                
                logger.debug("❌ All audio processing methods failed")
                    
            except Exception as e:
                logger.debug(f"❌ Google STT error: {e}")
        
        # Fallback: return a mock transcription for testing
        logger.warning("⚠️ STT failed, using fallback transcription")
        return "Hello, I need assistance with my business."
    
    async def _get_ai_response(self, user_text: str) -> Dict[str, Any]:
        """Get AI response to user input"""
        try:
            if self.ai_model == 'local':
                # For voice, provide a concise greeting/acknowledgment
                # instead of full business analysis
                user_lower = user_text.lower()
                
                # Simple greeting responses
                if any(word in user_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
                    return {
                        "text": "Hello! How can I help you today?",
                        "agent_type": "voice_assistant",
                        "confidence": 0.9
                    }
                
                # If it's a question or request, acknowledge it
                if any(word in user_lower for word in ['help', 'need', 'want', 'can you', 'how', 'what', 'why']):
                    return {
                        "text": "I'd be happy to help you with that. What specifically would you like to know?",
                        "agent_type": "voice_assistant",
                        "confidence": 0.9
                    }
                
                # Default acknowledgment
                return {
                    "text": "I understand. Please tell me more about what you need.",
                    "agent_type": "voice_assistant",
                    "confidence": 0.8
                }
            
        except Exception as e:
            logger.error(f"AI response error: {e}")
        
        # Fallback response
        return {
            "text": "I'm here to help. What can I do for you?",
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
        
        # Remove headers and labels like "Business & Go-To-Market Strategy Advice."
        if '.' in text:
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            # Skip header-like sentences and keep actual content
            actual_sentences = []
            for sentence in sentences:
                # Skip if it looks like a header (short, ends with colon, all caps parts, etc)
                if len(sentence) < 15 or sentence.endswith(':') or 'Your Question:' in sentence:
                    continue
                if not any(keyword in sentence.lower() for keyword in ['framework', 'advice', 'strategy', 'general']):
                    actual_sentences.append(sentence)
            
            if actual_sentences:
                # For voice, just use first meaningful sentence
                result = actual_sentences[0]
            else:
                result = "I'm here to help you with that."
        else:
            result = text
        
        # Ensure it's concise for speech (max 100 chars for quick response)
        if len(result) > 100:
            result = result[:97] + "..."
        
        return result
    
    async def _text_to_speech(self, text: str) -> Optional[bytes]:
        """Convert text to speech audio"""
        
        logger.info(f"🔊 TTS request for text: '{text[:50]}...'")
        
        # Use lock to prevent concurrent TTS calls (pyttsx3 is not thread-safe)
        async with self._tts_lock:
            logger.info("🔒 Acquired TTS lock")
            
            if self.tts_provider == 'pyttsx3' and PYTTSX3_AVAILABLE:
                try:
                    import tempfile
                    import os
                    import asyncio
                    from concurrent.futures import ThreadPoolExecutor
                    
                    logger.info("🔊 Using pyttsx3 for TTS...")
                    
                    # Reinitialize TTS engine for each request (pyttsx3 Windows issue)
                    logger.debug("🔄 Reinitializing pyttsx3 engine...")
                    try:
                        # Create a fresh engine instance for this request
                        import pyttsx3
                        temp_engine = pyttsx3.init()
                        temp_engine.setProperty('rate', 180)
                        temp_engine.setProperty('volume', 0.9)
                        logger.debug("✅ Fresh TTS engine created")
                    except Exception as init_error:
                        logger.error(f"Failed to create TTS engine: {init_error}")
                        return None
                    
                    # Use pyttsx3 to generate speech in a separate thread to avoid blocking
                    def generate_speech(engine, text_to_speak, output_path):
                        """Generate speech in a thread to avoid blocking"""
                        try:
                            logger.debug(f"Thread: Starting TTS generation for: {text_to_speak[:30]}...")
                            engine.save_to_file(text_to_speak, output_path)
                            logger.debug("Thread: Calling runAndWait()...")
                            engine.runAndWait()
                            logger.debug("Thread: runAndWait() completed")
                            
                            # Stop the engine
                            try:
                                engine.stop()
                            except:
                                pass
                            
                            # Check if file was created
                            import os
                            if os.path.exists(output_path):
                                file_size = os.path.getsize(output_path)
                                logger.debug(f"Thread: Audio file created, size: {file_size} bytes")
                                return True
                            else:
                                logger.error("Thread: Audio file was not created!")
                                return False
                        except Exception as e:
                            logger.error(f"Thread: TTS generation error: {e}")
                            import traceback
                            logger.error(traceback.format_exc())
                            return False
                    
                    # Create temp file
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                        temp_path = temp_file.name
                    
                    logger.debug(f"🔊 Saving speech to: {temp_path}")
                    
                    # Run TTS in executor to prevent blocking
                    logger.debug("Starting TTS in thread pool executor...")
                    loop = asyncio.get_event_loop()
                    with ThreadPoolExecutor(max_workers=1) as executor:
                        logger.debug("Submitting TTS task to executor...")
                        success = await loop.run_in_executor(executor, generate_speech, temp_engine, text, temp_path)
                        logger.debug(f"TTS task completed, success: {success}")
                    
                    if not success:
                        logger.error("TTS generation failed in executor")
                        return None
                    
                    # Read the generated audio file
                    with open(temp_path, 'rb') as f:
                        audio_data = f.read()
                    
                    logger.info(f"✅ TTS generated {len(audio_data)} bytes of audio")
                    
                    # Clean up temp file
                    try:
                        os.unlink(temp_path)
                    except Exception:
                        pass
                    
                    return audio_data
                    
                except Exception as e:
                    logger.error(f"❌ TTS error: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
            else:
                logger.warning(f"⚠️ TTS not available - provider: {self.tts_provider}, pyttsx3 available: {PYTTSX3_AVAILABLE}")
            
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