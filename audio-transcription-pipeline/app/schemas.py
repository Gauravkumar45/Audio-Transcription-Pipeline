from pydantic import BaseModel, Field


class TranscriptSegment(BaseModel):
    start: float = Field(ge=0, description="Segment start time in seconds")
    end: float = Field(ge=0, description="Segment end time in seconds")
    text: str


class TranscriptionResponse(BaseModel):
    filename: str
    language: str | None = None
    duration_seconds: float | None = None
    text: str
    segments: list[TranscriptSegment]
    mode: str
