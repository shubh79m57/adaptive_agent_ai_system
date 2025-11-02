import pyttsx3
import os

print("Testing TTS directly...")

engine = pyttsx3.init()
engine.setProperty('rate', 180)
engine.setProperty('volume', 0.9)

output_file = 'test_audio_output.wav'
text = "Hello world, this is a test of text to speech"

print(f"Saving to: {output_file}")
engine.save_to_file(text, output_file)
engine.runAndWait()
engine.stop()

if os.path.exists(output_file):
    file_size = os.path.getsize(output_file)
    print(f"✅ Audio file created: {output_file}")
    print(f"✅ File size: {file_size} bytes")
else:
    print("❌ Audio file was NOT created!")
