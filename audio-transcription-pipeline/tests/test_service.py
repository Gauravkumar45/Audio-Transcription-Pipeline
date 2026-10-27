from pathlib import Path
from fastapi import UploadFile
import pytest
from app.service import AudioValidationError, TranscriptionService
from app.transcriber import Transcriber


@pytest.mark.asyncio
async def test_mock_transcription_returns_segments(tmp_path, monkeypatch):
    monkeypatch.setattr("app.service.UPLOAD_DIR", tmp_path)
    service = TranscriptionService(Transcriber("mock", "base"))
    upload = UploadFile(filename="sample.wav", file=__import__("io").BytesIO(b"fake audio bytes"))
    result = await service.transcribe_upload(upload)
    assert result["filename"] == "sample.wav"
    assert result["mode"] == "mock"
    assert isinstance(result["segments"], list)
    assert "text" in result


@pytest.mark.asyncio
async def test_rejects_unsupported_extension(tmp_path, monkeypatch):
    monkeypatch.setattr("app.service.UPLOAD_DIR", tmp_path)
    service = TranscriptionService(Transcriber("mock", "base"))
    upload = UploadFile(filename="payload.exe", file=__import__("io").BytesIO(b"x"))
    with pytest.raises(AudioValidationError):
        await service.transcribe_upload(upload)
