"""
Check if FFmpeg is installed and accessible
"""
import subprocess
import sys

def check_ffmpeg():
    """Check if FFmpeg is installed and accessible"""
    print("Checking FFmpeg installation...")
    print("-" * 50)
    
    try:
        # Try to run ffmpeg -version
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print("✅ FFmpeg is installed and accessible!")
            print("\nVersion info:")
            # Print first few lines of version output
            lines = result.stdout.split('\n')[:3]
            for line in lines:
                print(f"   {line}")
            return True
        else:
            print("❌ FFmpeg command failed")
            print(f"Error: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ FFmpeg is NOT installed or not in PATH")
        print("\nPlease install FFmpeg:")
        print("   Option 1: choco install ffmpeg")
        print("   Option 2: Download from https://ffmpeg.org/download.html")
        print("\nSee AUDIO_SETUP.md for detailed instructions")
        return False
        
    except Exception as e:
        print(f"❌ Error checking FFmpeg: {e}")
        return False

def check_audio_libraries():
    """Check if required Python audio libraries are installed"""
    print("\n" + "=" * 50)
    print("Checking Python audio libraries...")
    print("-" * 50)
    
    libraries = {
        'pydub': 'Audio conversion',
        'soundfile': 'Audio I/O',
        'librosa': 'Audio processing',
        'speech_recognition': 'Speech-to-text',
        'pyttsx3': 'Text-to-speech'
    }
    
    all_installed = True
    for lib, description in libraries.items():
        try:
            __import__(lib)
            print(f"✅ {lib:20s} - {description}")
        except ImportError:
            print(f"❌ {lib:20s} - {description} (NOT INSTALLED)")
            all_installed = False
    
    if not all_installed:
        print("\nInstall missing libraries:")
        print("   pip install pydub soundfile librosa SpeechRecognition pyttsx3")
    
    return all_installed

if __name__ == "__main__":
    print("\n🔍 Audio Processing Setup Check\n")
    
    ffmpeg_ok = check_ffmpeg()
    libs_ok = check_audio_libraries()
    
    print("\n" + "=" * 50)
    print("Summary:")
    print("-" * 50)
    
    if ffmpeg_ok and libs_ok:
        print("✅ All audio processing dependencies are installed!")
        print("   You can now use voice features.")
        sys.exit(0)
    else:
        print("⚠️  Some dependencies are missing.")
        print("   Please install them to use voice features.")
        print("\n   See AUDIO_SETUP.md for detailed installation instructions.")
        sys.exit(1)
