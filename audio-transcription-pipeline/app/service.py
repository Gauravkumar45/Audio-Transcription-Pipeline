from pathlib import Path
from fastapi import UploadFile
from app.settings import ALLOWED_EXTENSIONS, MAX_UPLOAD_MB, UPLOAD_DIR
from app.transcriber import Transcriber, TranscriptionError


class AudioValidationError(ValueError):
    pass


class TranscriptionService:
    def __init__(self, transcriber: Transcriber) -> None:
        self.transcriber = transcriber

    async def transcribe_upload(self, upload: UploadFile, language: str | None = None) -> dict:
        filename = Path(upload.filename or "audio").name
        extension = Path(filename).suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise AudioValidationError(
                f"Unsupported file extension '{extension or '(none)'}'. "
                f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )

        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        temp_path = UPLOAD_DIR / f"upload-{__import__('uuid').uuid4().hex}{extension}"
        total_bytes = 0
        max_bytes = MAX_UPLOAD_MB * 1024 * 1024

        try:
            with temp_path.open("wb") as destination:
                while True:
                    chunk = await upload.read(1024 * 1024)
                    if not chunk:
                        break
                    total_bytes += len(chunk)
                    if total_bytes > max_bytes:
                        raise AudioValidationError(f"File exceeds the {MAX_UPLOAD_MB} MB upload limit.")
                    destination.write(chunk)

            if total_bytes == 0:
                raise AudioValidationError("Uploaded file is empty.")

            result = self.transcriber.transcribe(temp_path, language=language)
            return {"filename": filename, **result}
        finally:
            await upload.close()
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass
