from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.voice.livekit_agent import LiveKitVoiceAgent, VoiceCallRecorder

router = APIRouter()

voice_agent = LiveKitVoiceAgent()
recorder = VoiceCallRecorder()


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
