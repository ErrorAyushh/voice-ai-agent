from faster_whisper import WhisperModel

# Load once at module level (avoids reloading every call)
_model = None

def get_model():
    global _model
    if _model is None:
        # "base" = good balance of speed and accuracy on CPU
        _model = WhisperModel("small", device="cpu", compute_type="int8")
    return _model

def transcribe_audio(audio_path: str) -> str:
    """Convert audio file to text using local Whisper model."""
    try:
        model = get_model()
        segments, _ = model.transcribe(audio_path, beam_size=5)
        transcript = " ".join([seg.text.strip() for seg in segments])
        return transcript.strip()
    except Exception as e:
        return f"[Transcription Error]: {str(e)}"