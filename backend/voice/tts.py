"""
Wellsy Voice Module — Text-to-Speech using Edge TTS (Jenny)
Natural, human-like, friendly voice!
"""
import asyncio
import os
import subprocess
import edge_tts

# Wellsy's voice settings — tuned for natural, friendly speech
VOICE_ID = "en-US-JennyNeural"
VOICE_RATE = "+15%"     # Slightly faster = more natural energy
VOICE_PITCH = "+8Hz"    # Slightly higher = more youthful
VOICE_VOLUME = "+0%"

VOICE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "voice_cache")
os.makedirs(VOICE_DIR, exist_ok=True)


def _build_ssml(text: str) -> str:
    """Build SSML for more expressive, human-like speech."""
    import re
    # 1. Clean markdown links: replace [Text](url) with just Text
    clean = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # 2. Clean standalone web URLs, WS links and file links (e.g. http://..., file:///..., wss://...)
    clean = re.sub(r'https?://\S+', 'link', clean)
    clean = re.sub(r'wss?://\S+', 'link', clean)
    clean = re.sub(r'file:///\S+', 'file', clean)
    
    # 3. Clean up generic path patterns (like D:\Wellsy\backend... or D:/Wellsy/backend...)
    clean = re.sub(r'[A-Za-z]:\\[^\s]+', 'path', clean)
    clean = re.sub(r'[A-Za-z]:/[^\s]+', 'path', clean)
    
    # 4. Clean up other markdown symbols, parentheses, brackets, and special chars
    clean = clean.replace("*", "").replace("#", "").replace("`", "")
    clean = clean.replace("  ", " ").strip()
    
    # Truncate very long responses for voice (keep it conversational)
    if len(clean) > 300:
        # Find a good break point
        sentences = clean.split(". ")
        short = ""
        for s in sentences:
            if len(short) + len(s) < 280:
                short += s + ". "
            else:
                break
        clean = short.strip() if short.strip() else clean[:280] + "..."
    
    ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
       xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
  <voice name="{VOICE_ID}">
    <mstts:express-as style="friendly" styledegree="2">
      <prosody rate="{VOICE_RATE}" pitch="{VOICE_PITCH}">
        {clean}
      </prosody>
    </mstts:express-as>
  </voice>
</speak>"""
    return ssml


async def _generate_speech(text: str, output_path: str) -> str:
    """Generate natural speech from text."""
    ssml = _build_ssml(text)
    tts = edge_tts.Communicate(ssml, VOICE_ID)
    await tts.save(output_path)
    return output_path


async def _generate_speech_simple(text: str, output_path: str) -> str:
    """Fallback: generate speech without SSML."""
    import re
    # Clean markdown links, URLs, and paths
    clean = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    clean = re.sub(r'https?://\S+', 'link', clean)
    clean = re.sub(r'wss?://\S+', 'link', clean)
    clean = re.sub(r'file:///\S+', 'file', clean)
    clean = re.sub(r'[A-Za-z]:\\[^\s]+', 'path', clean)
    clean = re.sub(r'[A-Za-z]:/[^\s]+', 'path', clean)
    clean = clean.replace("*", "").replace("#", "").replace("`", "")
    clean = clean.replace("  ", " ").strip()
    if len(clean) > 300:
        sentences = clean.split(". ")
        short = ""
        for s in sentences:
            if len(short) + len(s) < 280:
                short += s + ". "
            else:
                break
        clean = short.strip() if short.strip() else clean[:280] + "..."
    
    tts = edge_tts.Communicate(clean, VOICE_ID, rate=VOICE_RATE, pitch=VOICE_PITCH)
    await tts.save(output_path)
    return output_path


def speak(text: str) -> str:
    """Make Wellsy speak! Natural, friendly voice."""
    audio_file = os.path.join(VOICE_DIR, f"wellsy_{hash(text) & 0xFFFFFFFF}.mp3")
    
    try:
        asyncio.run(_generate_speech(text, audio_file))
    except Exception:
        # Fallback to simple mode if SSML fails
        asyncio.run(_generate_speech_simple(text, audio_file))
    
    # Play through headphones/speakers
    _play_audio(audio_file, text)
    return audio_file


async def speak_async(text: str) -> str:
    """Async version for the FastAPI server."""
    audio_file = os.path.join(VOICE_DIR, f"wellsy_{hash(text) & 0xFFFFFFFF}.mp3")
    
    try:
        await _generate_speech(text, audio_file)
    except Exception:
        await _generate_speech_simple(text, audio_file)
    
    # Play in background
    _play_audio_bg(audio_file, text)
    return audio_file


def _play_audio(filepath: str, text: str):
    """Play audio and wait for it to finish."""
    wait_secs = max(3, len(text) // 12)
    subprocess.run([
        "powershell", "-Command",
        "Add-Type -AssemblyName presentationCore;"
        "$p = New-Object System.Windows.Media.MediaPlayer;"
        f"$p.Open([Uri]'{filepath}');"
        "Start-Sleep -Milliseconds 600;"
        "$p.Play();"
        f"Start-Sleep -Seconds {wait_secs};"
        "$p.Stop(); $p.Close()"
    ], capture_output=True)


def _play_audio_bg(filepath: str, text: str):
    """Play audio in background (non-blocking)."""
    wait_secs = max(3, len(text) // 12)
    subprocess.Popen([
        "powershell", "-Command",
        "Add-Type -AssemblyName presentationCore;"
        "$p = New-Object System.Windows.Media.MediaPlayer;"
        f"$p.Open([Uri]'{filepath}');"
        "Start-Sleep -Milliseconds 600;"
        "$p.Play();"
        f"Start-Sleep -Seconds {wait_secs};"
        "$p.Stop(); $p.Close()"
    ])


if __name__ == "__main__":
    speak("Hey Moksh! How's it going? I've been waiting to talk to you!")
    print("Voice test complete!")
