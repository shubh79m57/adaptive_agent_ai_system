"""
Voice AI API endpoints for real-time voice processing
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import base64

# Import voice components
try:
    from ..voice.voice_ai_agent import create_voice_agent, VoiceAIAgent
    from ..voice.livekit_agent import LiveKitVoiceAssistant, LiveKitVoiceAgent
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    print("Voice components not available")

router = APIRouter()

class VoiceConfigRequest(BaseModel):
    stt_provider: Optional[str] = "whisper"  # whisper, google, azure
    tts_provider: Optional[str] = "pyttsx3"  # pyttsx3, elevenlabs, azure
    ai_model: Optional[str] = "local"  # local, openai, anthropic
    sample_rate: Optional[int] = 16000
    voice_id: Optional[str] = "alloy"

class AudioProcessRequest(BaseModel):
    audio_data: str  # Base64 encoded audio
    format: Optional[str] = "wav"
    config: Optional[VoiceConfigRequest] = None

class LiveKitRoomRequest(BaseModel):
    room_name: str
    participant_name: str
    config: Optional[VoiceConfigRequest] = None

# Legacy models for backward compatibility
class RoomCreateRequest(BaseModel):
    room_name: str

class TokenRequest(BaseModel):
    room_name: str
    participant_identity: str

# Global voice agent instances
voice_agent: Optional[VoiceAIAgent] = None
livekit_assistant: Optional[LiveKitVoiceAssistant] = None
legacy_voice_agent = LiveKitVoiceAgent() if VOICE_AVAILABLE else None


class CreateRoomRequest(BaseModel):
    room_name: str


class GenerateTokenRequest(BaseModel):
    room_name: str
    participant_identity: str


class ProcessConversationRequest(BaseModel):
    room_name: str
    transcript: str


@router.post("/room/create")
async def create_room(request: CreateRoomRequest):
    """Create a new LiveKit room for voice conversation"""
    try:
        room_name = await voice_agent.create_room(request.room_name)
        return {
            "success": True,
            "room_name": room_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/token/generate")
async def generate_token(request: GenerateTokenRequest):
    """Generate access token for participant"""
    try:
        token = await voice_agent.generate_token(
            request.room_name,
            request.participant_identity
        )
        return {
            "success": True,
            "token": token,
            "room_name": request.room_name,
            "participant_identity": request.participant_identity
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversation/process")
async def process_conversation(request: ProcessConversationRequest):
    """Process and analyze conversation"""
    try:
        result = await voice_agent.process_conversation(
            request.room_name,
            request.transcript
        )
        return {
            "success": True,
            "analysis": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recording/start/{room_name}")
async def start_recording(room_name: str):
    """Start recording a room"""
    try:
        await recorder.start_recording(room_name)
        return {
            "success": True,
            "room_name": room_name,
            "status": "recording"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recording/stop/{room_name}")
async def stop_recording(room_name: str):
    """Stop recording and get transcript"""
    try:
        recording = await recorder.stop_recording(room_name)
        return {
            "success": True,
            "recording": recording
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recording/transcript/{room_name}")
async def get_transcript(room_name: str):
    """Get full transcript of a room"""
    try:
        transcript = recorder.get_full_transcript(room_name)
        return {
            "success": True,
            "room_name": room_name,
            "transcript": transcript
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
