#!/usr/bin/env python3
"""
Test script for voice AI functionality with free libraries only
"""

import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """Test if all free voice AI libraries can be imported"""
    print("Testing voice AI library imports...")
    
    try:
        import speech_recognition as sr
        print("✅ SpeechRecognition imported successfully")
    except ImportError as e:
        print(f"❌ SpeechRecognition import failed: {e}")
    
    try:
        import pyttsx3
        print("✅ pyttsx3 imported successfully")
    except ImportError as e:
        print(f"❌ pyttsx3 import failed: {e}")
    
    try:
        import whisper
        print("✅ OpenAI Whisper imported successfully")
    except ImportError as e:
        print(f"❌ OpenAI Whisper import failed: {e}")
    
    try:
        import soundfile as sf
        print("✅ SoundFile imported successfully")
    except ImportError as e:
        print(f"❌ SoundFile import failed: {e}")
    
    try:
        import librosa
        print("✅ Librosa imported successfully")
    except ImportError as e:
        print(f"❌ Librosa import failed: {e}")
    
    try:
        import torch
        print("✅ PyTorch imported successfully")
    except ImportError as e:
        print(f"❌ PyTorch import failed: {e}")
    
    try:
        from pydub import AudioSegment
        print("✅ Pydub imported successfully")
    except ImportError as e:
        print(f"❌ Pydub import failed: {e}")

def test_voice_ai_agent():
    """Test our VoiceAIAgent class"""
    print("\nTesting VoiceAIAgent...")
    
    try:
        sys.path.append('app')
        from app.voice.voice_ai_agent import VoiceAIAgent
        
        # Create a simple config for testing
        config = {
            'stt_provider': 'whisper',
            'tts_provider': 'pyttsx3',
            'ai_model': 'local',
            'sample_rate': 16000,
            'chunk_duration': 1.0,
            'voice_id': 'alloy'
        }
        
        agent = VoiceAIAgent(config)
        print("✅ VoiceAIAgent created successfully")
        
        # Test capabilities
        capabilities = agent.get_capabilities()
        print(f"✅ Voice capabilities: {capabilities}")
        
        return True
    except Exception as e:
        print(f"❌ VoiceAIAgent test failed: {e}")
        return False

def test_basic_tts():
    """Test basic text-to-speech functionality"""
    print("\nTesting Text-to-Speech...")
    
    try:
        import pyttsx3
        engine = pyttsx3.init()
        
        # Test without actually speaking
        engine.setProperty('rate', 150)
        print("✅ TTS engine initialized successfully")
        
        # Get available voices
        voices = engine.getProperty('voices')
        print(f"✅ Available voices: {len(voices) if voices else 0}")
        
        engine.stop()
        return True
    except Exception as e:
        print(f"❌ TTS test failed: {e}")
        return False

def test_whisper_model():
    """Test Whisper model loading"""
    print("\nTesting Whisper model...")
    
    try:
        import whisper
        
        # Load the smallest model for testing
        model = whisper.load_model("base")
        print("✅ Whisper base model loaded successfully")
        
        return True
    except Exception as e:
        print(f"❌ Whisper test failed: {e}")
        return False

if __name__ == "__main__":
    print("🎤 Voice AI System Test - Free Libraries Only\n")
    
    # Run all tests
    test_imports()
    
    voice_agent_ok = test_voice_ai_agent()
    tts_ok = test_basic_tts()
    whisper_ok = test_whisper_model()
    
    print("\n" + "="*50)
    print("📊 Test Summary:")
    print(f"Voice Agent: {'✅ PASS' if voice_agent_ok else '❌ FAIL'}")
    print(f"Text-to-Speech: {'✅ PASS' if tts_ok else '❌ FAIL'}")
    print(f"Whisper STT: {'✅ PASS' if whisper_ok else '❌ FAIL'}")
    
    if voice_agent_ok and tts_ok and whisper_ok:
        print("\n🎉 All voice AI components are working with free libraries!")
        print("Ready to start the FastAPI server and test the voice interface.")
    else:
        print("\n⚠️  Some components failed. Check the logs above.")