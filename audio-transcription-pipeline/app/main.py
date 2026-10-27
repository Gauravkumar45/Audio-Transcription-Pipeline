from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from app.schemas import TranscriptionResponse
from app.service import AudioValidationError, TranscriptionService
from app.settings import TRANSCRIPTION_MODE, WHISPER_MODEL
from app.transcriber import Transcriber, TranscriptionError

app = FastAPI(
    title="Audio Transcription Pipeline",
    description="Upload an audio file and receive transcript text with segment-level timestamps.",
    version="1.0.0",
)
service = TranscriptionService(Transcriber(TRANSCRIPTION_MODE, WHISPER_MODEL))


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "mode": TRANSCRIPTION_MODE}


@app.post("/v1/transcriptions", response_model=TranscriptionResponse)
async def create_transcription(
    file: UploadFile = File(...),
    language: str | None = Query(default=None, min_length=2, max_length=10),
) -> dict:
    try:
        return await service.transcribe_upload(file, language=language)
    except AudioValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except TranscriptionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        # Avoid returning internal stack traces to clients.
        raise HTTPException(status_code=500, detail="Unexpected transcription service error.") from exc
