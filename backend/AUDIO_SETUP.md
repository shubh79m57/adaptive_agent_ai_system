# Audio Processing Setup Guide

## FFmpeg Installation (Required for Audio Conversion)

FFmpeg is required to convert audio formats (WebM, MP3, etc.) to WAV for speech recognition.

### Windows Installation Options:

#### Option 1: Using Chocolatey (Recommended)
```powershell
choco install ffmpeg
```

#### Option 2: Manual Installation
1. Download FFmpeg from: https://ffmpeg.org/download.html
   - For Windows, use builds from: https://www.gyan.dev/ffmpeg/builds/
   - Download the "ffmpeg-release-essentials.zip"

2. Extract the zip file to a location (e.g., `C:\ffmpeg`)

3. Add FFmpeg to your PATH:
   - Open System Properties → Environment Variables
   - Edit the "Path" variable under System Variables
   - Add the path to FFmpeg's `bin` folder (e.g., `C:\ffmpeg\bin`)
   - Click OK to save

4. Verify installation:
```powershell
ffmpeg -version
```

### After Installation
Restart your terminal/IDE and the voice server for changes to take effect.

## Python Audio Libraries

The following Python packages are also required:

```bash
pip install pydub soundfile librosa SpeechRecognition pyttsx3
```

## Testing

After installation, test the audio processing:

```bash
python test_voice.py
```

## Troubleshooting

### "Couldn't find ffmpeg or avconv" warning
- FFmpeg is not in your system PATH
- Follow the installation steps above

### "The system cannot find the file specified"
- FFmpeg executable is not accessible
- Verify FFmpeg is installed: `ffmpeg -version`
- Check your PATH environment variable includes FFmpeg's bin directory

### Audio conversion still failing
- Try using librosa fallback (already implemented)
- Ensure audio file format is supported (WAV, WebM, MP3)
- Check audio file is not corrupted
