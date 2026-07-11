"""
Play Wellsy voice demos + generate remaining ones
"""
import asyncio
import os
import subprocess
import edge_tts

DEMO_DIR = r"D:\Wellsy\voice_demos"
os.makedirs(DEMO_DIR, exist_ok=True)

DEMO_TEXT = "Hey there! I'm Wellsy, your personal assistant. What's the plan for today? Want me to play some music, or should we get some work done?"

VOICES = [
    ("Jenny", "en-US-JennyNeural"),
    ("Aria", "en-US-AriaNeural"),
    ("Sonia", "en-GB-SoniaNeural"),
    ("Neerja", "en-IN-NeerjaNeural"),
]

async def generate_missing():
    for name, voice_id in VOICES:
        out_file = os.path.join(DEMO_DIR, f"wellsy_voice_{name.lower()}.mp3")
        if os.path.exists(out_file) and os.path.getsize(out_file) > 1000:
            print(f"  {name} already generated, skipping")
            continue
        print(f"  Generating {name}...")
        try:
            tts = edge_tts.Communicate(DEMO_TEXT, voice_id)
            await tts.save(out_file)
            print(f"  Saved: {name}")
        except Exception as e:
            print(f"  [!] {name} failed: {e}")

def play_mp3(filepath, label):
    print(f"\n  >>> Now playing: {label} <<<")
    proc = subprocess.run(
        ["powershell", "-Command",
         f"Add-Type -AssemblyName presentationCore; "
         f"$p = New-Object System.Windows.Media.MediaPlayer; "
         f"$p.Open([Uri]'{filepath}'); "
         f"Start-Sleep -Milliseconds 800; "
         f"$p.Play(); "
         f"Start-Sleep -Seconds 9; "
         f"$p.Stop(); $p.Close()"],
        capture_output=True, timeout=15
    )
    print(f"  Done: {label}")

async def main():
    print("=" * 50)
    print("  Wellsy Voice Demos")
    print("=" * 50)
    
    # Generate any missing
    await generate_missing()
    
    print("\n  Playing all voices through your headphones...")
    print("  Listen carefully!\n")
    
    for name, _ in VOICES:
        mp3 = os.path.join(DEMO_DIR, f"wellsy_voice_{name.lower()}.mp3")
        if os.path.exists(mp3):
            play_mp3(mp3, name)
        else:
            print(f"  Skipping {name} - file not found")
    
    print("\n" + "=" * 50)
    print("  All done! Tell me which voice you liked!")
    print("=" * 50)

asyncio.run(main())
