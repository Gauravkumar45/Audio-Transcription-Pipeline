import os
import tempfile
from pathlib import Path

ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".webm", ".mpeg", ".mpga"}
TRANSCRIPTION_MODE = os.getenv("TRANSCRIPTION_MODE", "mock").strip().lower()
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base").strip()
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "50"))
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", tempfile.gettempdir())) / "audio-transcription-uploads"

if TRANSCRIPTION_MODE not in {"mock", "real"}:
    raise ValueError("TRANSCRIPTION_MODE must be either 'mock' or 'real'")
if MAX_UPLOAD_MB < 1:
    raise ValueError("MAX_UPLOAD_MB must be >= 1")
