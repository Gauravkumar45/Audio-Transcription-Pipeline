from pathlib import Path
from typing import Any


class TranscriptionError(RuntimeError):
    """Raised when audio decoding or transcription fails."""


class Transcriber:
    def __init__(self, mode: str = "mock", model_name: str = "base") -> None:
        self.mode = mode
        self.model_name = model_name
        self._model: Any = None

    def _load_model(self) -> Any:
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
            except ImportError as exc:
                raise TranscriptionError(
                    "faster-whisper is not installed. Install requirements.txt or use mock mode."
                ) from exc
            try:
                self._model = WhisperModel(self.model_name, device="auto", compute_type="int8")
            except Exception as exc:
                raise TranscriptionError(f"Could not load Whisper model '{self.model_name}': {exc}") from exc
        return self._model

    def transcribe(self, audio_path: Path, language: str | None = None) -> dict:
        if self.mode == "mock":
            return {
                "language": language or "en",
                "duration_seconds": 0.0,
                "text": "[Mock transcription] Audio received successfully. Enable TRANSCRIPTION_MODE=real for speech recognition.",
                "segments": [
                    {
                        "start": 0.0,
                        "end": 0.0,
                        "text": "[Mock transcription] Audio received successfully. Enable TRANSCRIPTION_MODE=real for speech recognition."
                    }
                ],
                "mode": "mock",
            }

        model = self._load_model()
        try:
            segments_iter, info = model.transcribe(
                str(audio_path),
                language=language,
                vad_filter=True,
                beam_size=5,
            )
            segments = []
            text_parts = []
            for segment in segments_iter:
                segment_text = segment.text.strip()
                if segment_text:
                    segments.append({
                        "start": round(float(segment.start), 3),
                        "end": round(float(segment.end), 3),
                        "text": segment_text,
                    })
                    text_parts.append(segment_text)
            return {
                "language": getattr(info, "language", language),
                "duration_seconds": round(float(getattr(info, "duration", 0.0) or 0.0), 3),
                "text": " ".join(text_parts).strip(),
                "segments": segments,
                "mode": "real",
            }
        except TranscriptionError:
            raise
        except Exception as exc:
            raise TranscriptionError(f"Transcription failed: {exc}") from exc
