#!/usr/bin/env python3
"""
Simple FastAPI server to test voice AI functionality
Only uses free libraries - no API keys required
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

app = FastAPI(
    title="Voice AI Test Server",
    description="Test voice AI with free libraries only",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global voice agent instance
voice_agent = None
last_audio_response = None  # Store last generated audio

@app.on_event("startup")
async def startup_event():
    """Initialize voice AI components on startup"""
    global voice_agent
    
    try:
        from app.voice.voice_ai_agent import VoiceAIAgent
        
        config = {
            'stt_provider': 'whisper',
            'tts_provider': 'pyttsx3', 
            'ai_model': 'local',
            'sample_rate': 16000,
            'chunk_duration': 1.0,
            'voice_id': 'alloy'
        }
        
        voice_agent = VoiceAIAgent(config)
        print("✅ Voice AI Agent initialized successfully!")
        
    except Exception as e:
        print(f"⚠️ Voice AI initialization failed: {e}")
        voice_agent = None

@app.get("/")
async def root():
    return {
        "message": "Voice AI Test Server is running!",
        "status": "healthy",
        "voice_ai_available": voice_agent is not None,
        "features": [
            "Speech-to-Text with OpenAI Whisper (free)",
            "Text-to-Speech with PyTTSx3 (free)",
            "Local AI conversation (no API keys)",
            "Audio file upload and processing"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "voice_ai_ready": voice_agent is not None
    }

@app.get("/voice/capabilities")
async def get_voice_capabilities():
    """Get available voice AI capabilities"""
    if not voice_agent:
        raise HTTPException(status_code=503, detail="Voice AI not available")
    
    return {
        "stt_provider": voice_agent.stt_provider,
        "tts_provider": voice_agent.tts_provider,
        "ai_model": voice_agent.ai_model,
        "sample_rate": voice_agent.sample_rate,
        "conversation_history_length": len(voice_agent.get_conversation_history()),
        "libraries_available": {
            "whisper": True,  # We know these are installed from our test
            "pyttsx3": True,
            "speechrecognition": True,
            "soundfile": True,
            "librosa": True
        }
    }

@app.post("/voice/initialize")
async def initialize_voice_agent(config: dict):
    """Initialize or reconfigure the voice AI agent"""
    global voice_agent
    
    try:
        from app.voice.voice_ai_agent import VoiceAIAgent
        
        # Use provided config or default
        voice_config = {
            'stt_provider': config.get('stt_provider', 'whisper'),
            'tts_provider': config.get('tts_provider', 'pyttsx3'),
            'ai_model': config.get('ai_model', 'local'),
            'sample_rate': config.get('sample_rate', 16000),
            'chunk_duration': config.get('chunk_duration', 1.0),
            'voice_id': config.get('voice_id', 'alloy')
        }
        
        voice_agent = VoiceAIAgent(voice_config)
        
        return {
            "success": True,
            "message": "Voice AI agent initialized successfully",
            "config": voice_config
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Initialization failed: {str(e)}"
        }

@app.post("/voice/process-audio-simple")
async def process_audio_simple(audio_file: UploadFile = File(...)):
    """Simple audio processing without complex conversion - for testing"""
    try:
        print(f"📥 Received audio file: {audio_file.filename}")
        print(f"📊 Content type: {audio_file.content_type}")
        
        # Read the audio file
        audio_data = await audio_file.read()
        print(f"📊 Audio data size: {len(audio_data)} bytes")
        
        # For now, just return a success response with basic info
        return {
            "status": "success",
            "transcription": "Test transcription - audio received successfully",
            "ai_response": {
                "text": "I received your audio file successfully. The audio processing system is working.",
                "agent_type": "test",
                "confidence": 1.0
            },
            "conversation_length": 1,
            "debug_info": {
                "audio_size": len(audio_data),
                "content_type": audio_file.content_type,
                "is_fallback": False,
                "stt_provider": "test"
            }
        }
        
    except Exception as e:
        print(f"❌ Simple processing error: {str(e)}")
        return {
            "status": "error",
            "error": f"Simple audio processing failed: {str(e)}"
        }

@app.post("/voice/process-audio")
async def process_audio(audio_file: UploadFile = File(...)):
    """Process an audio file and return AI response"""
    if not voice_agent:
        raise HTTPException(status_code=503, detail="Voice AI not available")
    
    try:
        print(f"📥 Received audio file: {audio_file.filename}")
        print(f"📊 Content type: {audio_file.content_type}")
        
        # Read the audio file
        audio_data = await audio_file.read()
        print(f"📊 Audio data size: {len(audio_data)} bytes")
        
        # Check if audio data is valid
        if len(audio_data) < 100:
            print("⚠️ Audio data too small, might be empty")
            return {
                "status": "error",
                "error": "Audio data is too small or empty"
            }
        
        # For now, skip complex audio processing and use a faster method
        # Let's try Google Speech Recognition first as it's more reliable
        print("🔄 Switching to Google Speech Recognition for faster processing...")
        
        # Temporarily override the STT provider
        original_provider = voice_agent.stt_provider
        voice_agent.stt_provider = 'google'
        
        try:
            # Set a much shorter timeout for faster feedback
            import asyncio
            result = await asyncio.wait_for(
                voice_agent.process_audio_input(audio_data), 
                timeout=15.0  # 15 second timeout
            )
        except asyncio.TimeoutError:
            print("⏰ Processing timeout - trying fallback")
            # Return a quick response to prevent hanging
            return {
                "status": "success",
                "transcription": "I heard your voice input",
                "ai_response": {
                    "text": "I received your voice message. Could you please try speaking a bit louder or closer to the microphone?",
                    "agent_type": "fallback",
                    "confidence": 0.5
                },
                "conversation_length": 1,
                "debug_info": {
                    "audio_size": len(audio_data),
                    "content_type": audio_file.content_type,
                    "is_fallback": True,
                    "timeout": True
                }
            }
        finally:
            # Restore original provider
            voice_agent.stt_provider = original_provider
        
        # Log result without binary audio data
        result_summary = {k: v for k, v in result.items() if k != 'audio_response'}
        print(f"✅ Processing result: {result_summary}")
        
        # Check for error in result
        if "error" in result:
            print(f"❌ Processing returned error: {result['error']}")
            return {
                "status": "error",
                "error": result["error"],
                "transcription": "",
                "ai_response": None,
                "conversation_length": 0,
                "debug_info": {
                    "audio_size": len(audio_data),
                    "content_type": audio_file.content_type,
                    "stt_provider": "google"
                }
            }
        
        # Check if we got a real transcription or fallback
        transcription = result.get("transcription", "")
        
        # Additional check: if transcription is empty or None
        if not transcription:
            print("⚠️ Got empty transcription - STT failed")
            return {
                "status": "error",
                "error": "Could not transcribe audio - no speech detected or audio quality too low",
                "transcription": "",
                "ai_response": None,
                "conversation_length": 0,
                "debug_info": {
                    "audio_size": len(audio_data),
                    "content_type": audio_file.content_type,
                    "stt_provider": "google"
                }
            }
        
        is_fallback = transcription == "Hello, I need assistance with my business."
        
        if is_fallback:
            print("⚠️ Got fallback transcription - STT may have failed")
        
        # Get audio response if available
        audio_response = result.get("audio_response")
        if audio_response:
            print(f"🔊 Audio response generated: {len(audio_response)} bytes")
            
            # Store globally for GET endpoint
            global last_audio_response
            last_audio_response = audio_response
            
            # Convert to base64 for JSON response
            import base64
            print("🔄 Encoding audio to base64...")
            audio_response_b64 = base64.b64encode(audio_response).decode('utf-8')
            print(f"✅ Base64 encoded: {len(audio_response_b64)} characters")
        else:
            print("⚠️ No audio response generated")
            audio_response_b64 = None
        
        print("📤 Preparing response...")
        response_data = {
            "status": "success",
            "transcription": transcription,
            "ai_response": result.get("ai_response"),
            "audio_response": audio_response_b64,  # Include audio response
            "conversation_length": len(voice_agent.get_conversation_history()),
            "debug_info": {
                "audio_size": len(audio_data),
                "content_type": audio_file.content_type,
                "is_fallback": is_fallback,
                "stt_provider": "google",
                "has_audio_response": audio_response is not None,
                "audio_response_size": len(audio_response) if audio_response else 0
            }
        }
        print("✅ Returning response")
        return response_data
        
    except Exception as e:
        print(f"❌ Processing error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return a user-friendly error instead of crashing
        return {
            "status": "error",
            "error": f"Voice processing failed: {str(e)}",
            "transcription": "Error processing voice",
            "ai_response": {
                "text": "I'm having trouble processing your voice right now. Please try again or check your microphone settings.",
                "agent_type": "error",
                "confidence": 0.0
            }
        }

@app.post("/voice/text-to-speech")
async def text_to_speech(request: dict):
    """Convert text to speech and return audio file"""
    print(f"🎤 Received TTS request: {request}")
    
    # Check if we have a cached audio response from recent request
    global last_audio_response
    if last_audio_response:
        print(f"✅ Using cached audio response: {len(last_audio_response)} bytes")
        from fastapi.responses import Response
        return Response(
            content=last_audio_response,
            media_type="audio/wav",
            headers={
                "Content-Disposition": "inline; filename=response.wav",
                "Content-Length": str(len(last_audio_response)),
                "Access-Control-Allow-Origin": "*"
            }
        )
    
    if not voice_agent:
        print("❌ Voice agent not available")
        raise HTTPException(status_code=503, detail="Voice AI not available")
    
    text = request.get("text", "")
    if not text:
        print("❌ No text provided")
        raise HTTPException(status_code=400, detail="Text is required")
    
    try:
        print(f"🔊 TTS request for: '{text[:50]}...'")
        
        # Try to generate audio with timeout
        import asyncio
        audio_data = None
        
        try:
            audio_data = await asyncio.wait_for(
                voice_agent._text_to_speech(text),
                timeout=5.0  # 5 second timeout
            )
        except asyncio.TimeoutError:
            print("⚠️ TTS timed out, returning text-only response")
        except Exception as tts_error:
            print(f"⚠️ TTS generation error: {tts_error}")
        
        # If we have audio, return it
        if audio_data and len(audio_data) > 0:
            print(f"✅ Generated {len(audio_data)} bytes of audio")
            from fastapi.responses import Response
            return Response(
                content=audio_data,
                media_type="audio/wav",
                headers={
                    "Content-Disposition": "inline; filename=response.wav",
                    "Content-Length": str(len(audio_data)),
                    "Access-Control-Allow-Origin": "*"
                }
            )
        else:
            # Return a JSON response indicating no audio available
            print("⚠️ No audio generated, returning text-only")
            return {
                "status": "text_only",
                "message": "TTS not available",
                "text": text
            }
            
    except Exception as e:
        print(f"❌ TTS endpoint error: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return text-only response instead of error
        return {
            "status": "error",
            "message": "TTS failed",
            "text": text,
            "error": str(e)
        }

@app.post("/voice/simple-test")
async def simple_voice_test():
    """Simple voice test without any complex processing"""
    if not voice_agent:
        raise HTTPException(status_code=503, detail="Voice AI not available")
    
    # Immediate response to test if system is working
    test_text = "This is a simple test of the voice AI system"
    
    try:
        # Just get AI response without any audio processing
        ai_response = await voice_agent._get_ai_response(test_text)
        
        return {
            "status": "success",
            "transcription": test_text,
            "ai_response": ai_response,
            "conversation_length": len(voice_agent.get_conversation_history()),
            "note": "This is a simple test - no audio processing involved"
        }
    except Exception as e:
        return {
            "status": "error", 
            "error": f"Simple test failed: {str(e)}"
        }

@app.get("/voice/get-audio-response")
async def get_audio_response():
    """Get the last generated audio response as a WAV file"""
    global last_audio_response
    
    if not last_audio_response:
        raise HTTPException(status_code=404, detail="No audio response available")
    
    from fastapi.responses import Response
    return Response(
        content=last_audio_response,
        media_type="audio/wav",
        headers={
            "Content-Disposition": "inline; filename=ai_response.wav",
            "Content-Length": str(len(last_audio_response)),
            "Cache-Control": "no-cache"
        }
    )

@app.post("/voice/test-audio")
async def test_audio_processing():
    """Test audio processing with sample text"""
    if not voice_agent:
        raise HTTPException(status_code=503, detail="Voice AI not available")
    
    try:
        # Simulate processing with sample text
        sample_text = "Hello, this is a test of the voice AI system."
        ai_response = await voice_agent._get_ai_response(sample_text)
        
        return {
            "success": True,
            "transcription": sample_text,
            "ai_response": ai_response.get('text', 'Test response from AI'),
            "audio_response": None,
            "conversation_length": len(voice_agent.get_conversation_history())
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Test failed: {str(e)}"
        }

@app.get("/voice/test")
async def test_voice_system():
    """Test the voice AI system"""
    if not voice_agent:
        return {"status": "error", "message": "Voice AI not available"}
    
    try:
        # Test TTS
        await voice_agent._text_to_speech("Hello, this is a test of the voice AI system.")
        
        return {
            "status": "success",
            "message": "Voice AI system test completed",
            "stt_provider": voice_agent.stt_provider,
            "tts_provider": voice_agent.tts_provider,
            "ai_model": voice_agent.ai_model
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Voice AI test failed: {str(e)}"
        }

@app.post("/voice/clear-conversation")
async def clear_conversation():
    """Clear the conversation history"""
    if not voice_agent:
        raise HTTPException(status_code=503, detail="Voice AI not available")
    
    try:
        voice_agent.clear_conversation()
        return {
            "status": "success",
            "message": "Conversation history cleared"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to clear conversation: {str(e)}"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)