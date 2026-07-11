"""
Wellsy Voice Module — Speech-to-Text using faster-whisper
Lets Wellsy hear you!
"""
import numpy as np
import threading
import queue
import time

# Will be set after import check
whisper_model = None
SAMPLE_RATE = 16000


def _load_model():
    """Load the Whisper model (lazy loading to save RAM)."""
    global whisper_model
    if whisper_model is None:
        try:
            from faster_whisper import WhisperModel
            print("[Wellsy STT] Loading whisper model (tiny)...")
            whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")
            print("[Wellsy STT] Model loaded!")
        except ImportError:
            print("[Wellsy STT] faster-whisper not installed. Voice input disabled.")
            print("  Install with: pip install faster-whisper")
            return None
    return whisper_model


def transcribe_audio(audio_data: np.ndarray) -> str:
    """Transcribe audio numpy array to text."""
    model = _load_model()
    if model is None:
        return ""
    
    # Ensure correct format
    if audio_data.dtype != np.float32:
        audio_data = audio_data.astype(np.float32)
    
    segments, info = model.transcribe(audio_data, beam_size=3, language="en")
    text = " ".join([seg.text.strip() for seg in segments])
    return text.strip()


def transcribe_file(audio_path: str) -> str:
    """Transcribe an audio file to text."""
    model = _load_model()
    if model is None:
        return ""
    
    segments, info = model.transcribe(audio_path, beam_size=3, language="en")
    text = " ".join([seg.text.strip() for seg in segments])
    return text.strip()


class VoiceListener:
    """
    Continuous voice listener that captures audio from mic,
    detects speech, and returns transcribed text.
    """
    
    def __init__(self, silence_threshold=500, silence_duration=1.5):
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self._thread = None
    
    def start(self, callback):
        """Start listening. Calls callback(text) when speech is detected and transcribed."""
        try:
            import sounddevice as sd
        except ImportError:
            print("[Wellsy STT] sounddevice not installed. Run: pip install sounddevice")
            return
        
        self.is_listening = True
        self._callback = callback
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        print("[Wellsy STT] Listening for voice input...")
    
    def stop(self):
        """Stop listening."""
        self.is_listening = False
        if self._thread:
            self._thread.join(timeout=2)
        print("[Wellsy STT] Stopped listening.")
    
    def _listen_loop(self):
        """Main listening loop — records audio chunks, detects speech, transcribes."""
        import sounddevice as sd
        
        buffer = []
        silent_chunks = 0
        is_speaking = False
        chunk_duration = 0.5  # 500ms chunks
        chunk_samples = int(SAMPLE_RATE * chunk_duration)
        
        while self.is_listening:
            try:
                # Record a chunk
                audio_chunk = sd.rec(chunk_samples, samplerate=SAMPLE_RATE, 
                                     channels=1, dtype='float32')
                sd.wait()
                audio_chunk = audio_chunk.flatten()
                
                # Check volume (RMS)
                rms = np.sqrt(np.mean(audio_chunk ** 2)) * 10000
                
                if rms > self.silence_threshold:
                    # Speech detected
                    is_speaking = True
                    silent_chunks = 0
                    buffer.append(audio_chunk)
                elif is_speaking:
                    # Silence after speech
                    silent_chunks += 1
                    buffer.append(audio_chunk)
                    
                    if silent_chunks >= (self.silence_duration / chunk_duration):
                        # End of speech - transcribe
                        full_audio = np.concatenate(buffer)
                        text = transcribe_audio(full_audio)
                        
                        if text and len(text) > 1:
                            self._callback(text)
                        
                        # Reset
                        buffer = []
                        silent_chunks = 0
                        is_speaking = False
                        
            except Exception as e:
                print(f"[Wellsy STT] Error: {e}")
                time.sleep(0.5)


if __name__ == "__main__":
    # Quick test
    print("Testing transcription from file...")
    # Test with a dummy
    model = _load_model()
    if model:
        print("Model loaded successfully!")
    else:
        print("Could not load model.")
