import asyncio
import subprocess
import edge_tts
import os

os.makedirs(r"D:\Wellsy\voice_demos", exist_ok=True)

text = "Oh my god, heyy! I'm Wellsy! So like, what are we doing today? Want me to play some music? Or should I open something for you? Just say the word babe, I got you!"

OUT = r"D:\Wellsy\voice_demos\wellsy_jenny.mp3"

async def go():
    print("Generating Wellsy voice...")
    tts = edge_tts.Communicate(text, "en-US-JennyNeural", rate="+10%", pitch="+5Hz")
    await tts.save(OUT)
    print("Playing through your headphones now...")

asyncio.run(go())

# Play it
subprocess.run([
    "powershell", "-Command",
    "Add-Type -AssemblyName presentationCore;"
    "$p = New-Object System.Windows.Media.MediaPlayer;"
    f"$p.Open([Uri]'{OUT}');"
    "Start-Sleep -Milliseconds 800;"
    "$p.Play();"
    "Start-Sleep -Seconds 10;"
    "$p.Stop(); $p.Close()"
])
print("Done! Did you hear her?")
