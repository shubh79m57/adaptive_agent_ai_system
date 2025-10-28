from typing import Optional, Dict, Any
import asyncio
from livekit import rtc, api
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import openai, silero
from loguru import logger

from app.core.config import settings
from app.agents.adaptive_agent import SalesAgent


class LiveKitVoiceAgent:
    """Real-time voice agent using LiveKit for live sales calls"""
    
    def __init__(self):
        self.livekit_api = api.LiveKitAPI(
            settings.LIVEKIT_URL,
            settings.LIVEKIT_API_KEY,
            settings.LIVEKIT_API_SECRET
        )
        self.sales_agent = SalesAgent()
    
    async def create_room(self, room_name: str) -> str:
        """Create a new LiveKit room for voice conversation"""
        try:
            room = await self.livekit_api.room.create_room(
                api.CreateRoomRequest(name=room_name)
            )
            logger.info(f"Created room: {room.name}")
            return room.name
        except Exception as e:
            logger.error(f"Error creating room: {e}")
            raise
    
    async def generate_token(self, room_name: str, participant_identity: str) -> str:
        """Generate access token for participant"""
        token = api.AccessToken(
            settings.LIVEKIT_API_KEY,
            settings.LIVEKIT_API_SECRET
        )
        token.with_identity(participant_identity).with_name(participant_identity)
        token.with_grants(
            api.VideoGrants(
                room_join=True,
                room=room_name,
            )
        )
        
        return token.to_jwt()
    
    async def start_voice_assistant(self, ctx: JobContext):
        """Start voice assistant in a room"""
        logger.info("Starting voice assistant")
        
        await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
        
        assistant = VoiceAssistant(
            vad=silero.VAD.load(),
            stt=openai.STT(),
            llm=openai.LLM(model="gpt-4"),
            tts=openai.TTS(),
            chat_ctx=llm.ChatContext().append(
                role="system",
                text=(
                    "You are a sales AI assistant. Your goal is to engage prospects, "
                    "understand their needs, and guide them through the sales process. "
                    "Be conversational, empathetic, and adaptive to their responses."
                ),
            ),
        )
        
        assistant.start(ctx.room)
        
        await asyncio.sleep(1)
        await assistant.say("Hello! I'm your AI sales assistant. How can I help you today?")
    
    async def process_conversation(self, room_name: str, transcript: str) -> Dict[str, Any]:
        """Process conversation and learn from it"""
        result = await self.sales_agent.execute(
            f"Analyze this sales conversation and suggest improvements: {transcript}"
        )
        
        return {
            "room": room_name,
            "analysis": result,
            "transcript": transcript
        }


class VoiceCallRecorder:
    """Record and transcribe voice calls for learning"""
    
    def __init__(self):
        self.recordings = {}
    
    async def start_recording(self, room_name: str):
        """Start recording a room"""
        logger.info(f"Starting recording for room: {room_name}")
        self.recordings[room_name] = {
            "status": "recording",
            "transcript": []
        }
    
    async def add_transcript_segment(self, room_name: str, segment: str, speaker: str):
        """Add transcript segment"""
        if room_name in self.recordings:
            self.recordings[room_name]["transcript"].append({
                "speaker": speaker,
                "text": segment
            })
    
    async def stop_recording(self, room_name: str) -> Dict[str, Any]:
        """Stop recording and return transcript"""
        if room_name in self.recordings:
            recording = self.recordings[room_name]
            recording["status"] = "completed"
            return recording
        return {}
    
    def get_full_transcript(self, room_name: str) -> str:
        """Get full transcript as string"""
        if room_name in self.recordings:
            segments = self.recordings[room_name]["transcript"]
            return "\n".join([f"{s['speaker']}: {s['text']}" for s in segments])
        return ""
