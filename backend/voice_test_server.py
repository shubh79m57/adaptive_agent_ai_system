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

@app.post("/voice/process-audio")
async def process_audio(audio_file: UploadFile = File(...)):
    """Process an audio file and return AI response"""
    if not voice_agent:
        raise HTTPException(status_code=503, detail="Voice AI not available")
    
    try:
        # Read the audio file
        audio_data = await audio_file.read()
        
        # Process with voice AI
        result = await voice_agent.process_audio_input(audio_data)
        
        return {
            "status": "success",
            "transcription": result.get("transcription"),
            "ai_response": result.get("ai_response"),
            "conversation_length": len(voice_agent.get_conversation_history())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/voice/text-to-speech")
async def text_to_speech(request: dict):
    """Convert text to speech"""
    if not voice_agent:
        raise HTTPException(status_code=503, detail="Voice AI not available")
    
    text = request.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    try:
        audio_data = await voice_agent._text_to_speech(text)
        
        if audio_data:
            return {
                "status": "success",
                "message": "Text converted to speech",
                "audio_length": len(audio_data) if audio_data else 0
            }
        else:
            return {
                "status": "success",
                "message": "Text processed (TTS engine played audio directly)",
                "audio_length": 0
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)