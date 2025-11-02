"""Test audio generation and playback"""
import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_tts_generation():
    """Test TTS audio generation"""
    from backend.app.voice.voice_ai_agent import VoiceAIAgent
    
    config = {
        'stt_provider': 'google',
        'tts_provider': 'pyttsx3',
        'ai_model': 'local',
        'sample_rate': 16000
    }
    
    print("Creating voice agent...")
    agent = VoiceAIAgent(config)
    
    test_text = "Hello! This is a test of the text to speech system. Can you hear me?"
    
    print(f"\nGenerating speech for: '{test_text}'")
    audio_data = await agent._text_to_speech(test_text)
    
    if audio_data:
        print(f"✅ Audio generated: {len(audio_data)} bytes")
        
        # Save to file
        output_file = "test_output.wav"
        with open(output_file, 'wb') as f:
            f.write(audio_data)
        print(f"✅ Audio saved to: {output_file}")
        
        # Try to play it
        try:
            import subprocess
            import platform
            
            system = platform.system()
            print(f"\n🔊 Attempting to play audio on {system}...")
            
            if system == "Windows":
                # Use Windows Media Player
                subprocess.run(["powershell", "-c", f"(New-Object Media.SoundPlayer '{output_file}').PlaySync()"], check=True)
            
            print("✅ Audio playback completed!")
            
        except Exception as e:
            print(f"⚠️ Could not auto-play: {e}")
            print(f"   Please manually play: {output_file}")
    else:
        print("❌ No audio was generated!")

if __name__ == "__main__":
    asyncio.run(test_tts_generation())
