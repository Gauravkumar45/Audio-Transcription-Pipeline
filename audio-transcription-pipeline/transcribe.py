#!/usr/bin/env python3
"""CLI for transcribing an audio file into JSON with segment timestamps."""

import argparse
import asyncio
import json
from pathlib import Path
from fastapi import UploadFile
from app.service import TranscriptionService
from app.settings import TRANSCRIPTION_MODE, WHISPER_MODEL
from app.transcriber import Transcriber


async def run(args: argparse.Namespace) -> dict:
    path = Path(args.audio).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Audio file does not exist: {path}")
    service = TranscriptionService(Transcriber(args.mode, args.model))
    # UploadFile provides the same interface used by the API service.
    with path.open("rb") as handle:
        upload = UploadFile(filename=path.name, file=handle)
        return await service.transcribe_upload(upload, language=args.language)


def main() -> None:
    parser = argparse.ArgumentParser(description="Transcribe audio and return timestamped segments.")
    parser.add_argument("audio", help="Path to an audio file (WAV, MP3, M4A, FLAC, OGG, WebM)")
    parser.add_argument("--language", help="Optional language code, e.g. en")
    parser.add_argument("--model", default=WHISPER_MODEL, help="Faster-Whisper model (default: configured model)")
    parser.add_argument("--mode", choices=["mock", "real"], default=TRANSCRIPTION_MODE)
    parser.add_argument("--output", help="Optional path to write JSON output")
    args = parser.parse_args()
    result = asyncio.run(run(args))
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    print(rendered)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
