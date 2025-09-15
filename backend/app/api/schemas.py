from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Upload schemas
class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    file_type: str
    file_size: int
    status: str
    message: str

# Media processing schemas
class TranscriptionResponse(BaseModel):
    file_id: str
    language: str
    text: str
    timestamps: Optional[List[Dict[str, Any]]] = None
    confidence_score: Optional[float] = None
    created_at: datetime

class TranslationRequest(BaseModel):
    text: str
    source_language: str
    target_language: str

class TranslationResponse(BaseModel):
    file_id: str
    source_language: str
    target_language: str
    original_text: str
    translated_text: str
    confidence_score: Optional[float] = None
    created_at: datetime

class SummaryResponse(BaseModel):
    file_id: str
    language: str
    original_text: str
    summary_text: str
    summary_type: str
    created_at: datetime

class SentimentResponse(BaseModel):
    file_id: str
    overall_sentiment: str
    overall_confidence: float
    segments: List[Dict[str, Any]]
    created_at: datetime

class ObjectDetectionResponse(BaseModel):
    file_id: str
    detections: List[Dict[str, Any]]
    total_frames: int
    created_at: datetime

# Processing status schemas
class ProcessingStatus(BaseModel):
    file_id: str
    status: str  # uploaded, processing, completed, error
    progress: Optional[int] = None  # 0-100
    current_task: Optional[str] = None
    error_message: Optional[str] = None
    results: Optional[Dict[str, Any]] = None

# Search schemas
class SearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    size: Optional[int] = 10

class SearchResponse(BaseModel):
    total: int
    results: List[Dict[str, Any]]
    aggregations: Optional[Dict[str, Any]] = None

# Highlight reel schemas
class HighlightRequest(BaseModel):
    file_id: str
    segments: List[Dict[str, float]]  # [{"start": 10.5, "end": 25.0}, ...]
    
class HighlightResponse(BaseModel):
    file_id: str
    highlight_video_path: str
    segments_count: int
    total_duration: float
    created_at: datetime

# Analytics schemas
class MediaAnalytics(BaseModel):
    file_id: str
    filename: str
    file_type: str
    duration: Optional[float]
    language: Optional[str]
    transcription_length: Optional[int]
    sentiment_distribution: Optional[Dict[str, float]]
    objects_count: Optional[int]
    processing_time: Optional[float]
    created_at: datetime