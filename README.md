# Audio Transcription Pipeline

A small Python project that accepts audio files, converts speech to text, and returns timestamped transcript segments. It includes a command-line interface (CLI), a FastAPI service, mock mode for testing without downloading an ML model, and tests.

## Features

- Supports common audio formats handled by FFmpeg / Faster-Whisper, including WAV, MP3, M4A, FLAC, OGG, and WebM.
- Transcribes speech to text using [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper).
- Returns segment-level timestamps (`start`, `end`, `text`).
- Optional language hint and model selection.
- Mock mode for local development and automated tests.
- FastAPI endpoints for health checks and synchronous transcription.
- Validates file size and extension; temporary uploads are cleaned up.
- Includes Dockerfile and pytest tests.

> **Note:** Segment timestamps are approximate speech-segment boundaries, not word-level timestamps. Real transcription requires FFmpeg and the selected Faster-Whisper model. The API defaults to mock mode to make the project easy to run without downloading a model.

## Repository structure

```text
audio-transcription-pipeline/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI endpoints
│   ├── schemas.py           # Request/response models
│   ├── settings.py          # Environment configuration
│   ├── service.py           # Validation and orchestration
│   └── transcriber.py       # Mock and Faster-Whisper backends
├── tests/
│   ├── test_service.py
│   └── test_api.py
├── .env.example
├── .gitignore
├── Dockerfile
├── requirements.txt
├── transcribe.py            # CLI entry point
└── README.md
```

## Requirements

- Python 3.10+
- FFmpeg installed and available on `PATH` for real audio decoding
- Internet access on the first real-model run to download model weights (unless already cached)

## Quick start

### 1. Clone or unzip the repository

```bash
git clone <YOUR_GIT_REPOSITORY_URL>
cd audio-transcription-pipeline
```

If you downloaded the ZIP, extract it and open a terminal in the extracted folder.

### 2. Create a virtual environment

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the API in mock mode

Mock mode does not need model weights or FFmpeg. It returns a clearly marked demo transcript, useful for checking the API contract.

```bash
uvicorn app.main:app --reload
```

Open the interactive API docs at `http://127.0.0.1:8000/docs`.

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Transcribe a file:

```bash
curl -X POST "http://127.0.0.1:8000/v1/transcriptions" \
  -F "file=@sample.wav"
```

The default API response is JSON with a `text` field and timestamped `segments`.

## Enable real transcription

Install FFmpeg first. For example, on Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install -y ffmpeg
```

Set the environment variables before starting the API:

Linux/macOS:
```bash
export TRANSCRIPTION_MODE=real
export WHISPER_MODEL=base
uvicorn app.main:app --reload
```

Windows PowerShell:
```powershell
$env:TRANSCRIPTION_MODE = "real"
$env:WHISPER_MODEL = "base"
uvicorn app.main:app --reload
```

Available model names include `tiny`, `base`, `small`, `medium`, and `large-v3`. Larger models generally improve accuracy but need more RAM/compute and take longer. CPU users can start with `base` or `small`.

Example:

```bash
curl -X POST "http://127.0.0.1:8000/v1/transcriptions?language=en" \
  -F "file=@meeting.mp3"
```

Use `language` only when you know the spoken language; omit it to let the model detect language automatically.

## Use the CLI

Mock mode:

```bash
python transcribe.py sample.wav
```

Real transcription:

```bash
TRANSCRIPTION_MODE=real python transcribe.py meeting.mp3 --model base --language en --output transcript.json
```

Windows PowerShell:

```powershell
$env:TRANSCRIPTION_MODE = "real"
python transcribe.py meeting.mp3 --model base --language en --output transcript.json
```

The CLI prints JSON to the terminal and optionally writes it to a file.

## Example response

```json
{
  "filename": "meeting.mp3",
  "language": "en",
  "duration_seconds": 12.48,
  "text": "Hello everyone. Let's begin the meeting.",
  "segments": [
    {
      "start": 0.0,
      "end": 2.1,
      "text": "Hello everyone."
    },
    {
      "start": 2.1,
      "end": 4.8,
      "text": "Let's begin the meeting."
    }
  ],
  "mode": "real"
}
```

The numbers above are illustrative; actual output depends on the audio.

## API reference

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Health status and configured mode |
| `POST` | `/v1/transcriptions` | Upload and transcribe an audio file |
| `GET` | `/docs` | Interactive Swagger UI |

The upload endpoint is synchronous and is best suited to small/medium files and a demo assignment. For production workloads, use an asynchronous job architecture (object storage + durable queue + workers) instead of holding an HTTP request open during long transcription.

## Configuration

| Environment variable | Default | Description |
|---|---|---|
| `TRANSCRIPTION_MODE` | `mock` | `mock` or `real` |
| `WHISPER_MODEL` | `base` | Faster-Whisper model size |
| `MAX_UPLOAD_MB` | `50` | Maximum accepted upload size |
| `UPLOAD_DIR` | system temp directory | Temporary upload directory |

Copy `.env.example` as `.env` if you use a dotenv loader or use the variables directly in your shell. This project intentionally avoids adding a dotenv dependency.

## Tests

```bash
pytest -q
```

The tests use mock mode and do not download model weights. They verify validation, response structure, and the health endpoint.

## Engineering decisions

1. **Transcription backend is isolated.** `transcriber.py` provides a simple seam between mock and real inference, so the API and service logic do not depend on one specific model library.
2. **Timestamped segments are part of the contract.** Downstream clients can display subtitles, build summaries, or align text with playback.
3. **Uploads are bounded and temporary files are cleaned up.** This prevents unbounded disk use for the simple service.
4. **Mock mode makes tests deterministic.** CI can test API behaviour without downloading large model weights.
5. **Long-running jobs should be asynchronous in production.** A durable queue, object storage, job table, retry policy, and worker pool are the recommended next step.

## Production improvements

- Upload original audio to S3-compatible object storage and keep metadata in PostgreSQL.
- Return `202 Accepted` and a `job_id`; process through SQS, RabbitMQ, or Kafka workers.
- Add authentication, authorization, rate limits, idempotency keys, and audit logs.
- Persist per-chunk results and use retry/backoff plus a dead-letter queue.
- Add structured logs, metrics, tracing, and retention policies.
- Add silence-aware chunking/overlap for very long recordings and offset chunk timestamps to global time.
- Validate file content as well as extension, and scan uploads where required.
