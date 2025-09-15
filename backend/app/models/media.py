from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float, Boolean
from sqlalchemy.sql import func
from ..core.database import Base
import uuid

class MediaFile(Base):
    __tablename__ = "media_files"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # video, audio
    file_size = Column(Integer, nullable=False)
    duration = Column(Float, nullable=True)
    status = Column(String, default="uploaded")  # uploaded, processing, completed, error
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ProcessingResult(Base):
    __tablename__ = "processing_results"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, nullable=False, index=True)
    task_type = Column(String, nullable=False)  # transcription, translation, summarization, etc.
    language = Column(String, nullable=True)
    result_data = Column(JSON, nullable=False)
    confidence_score = Column(Float, nullable=True)
    processing_time = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Transcription(Base):
    __tablename__ = "transcriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, nullable=False, index=True)
    language = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    timestamps = Column(JSON, nullable=True)  # Array of {start, end, text}
    confidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Translation(Base):
    __tablename__ = "translations"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, nullable=False, index=True)
    source_language = Column(String, nullable=False)
    target_language = Column(String, nullable=False)
    original_text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Summary(Base):
    __tablename__ = "summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, nullable=False, index=True)
    language = Column(String, nullable=False)
    original_text = Column(Text, nullable=False)
    summary_text = Column(Text, nullable=False)
    summary_type = Column(String, default="extractive")  # extractive, abstractive
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SentimentAnalysis(Base):
    __tablename__ = "sentiment_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, nullable=False, index=True)
    text_segment = Column(Text, nullable=False)
    sentiment = Column(String, nullable=False)  # positive, negative, neutral
    confidence_score = Column(Float, nullable=False)
    timestamp_start = Column(Float, nullable=True)
    timestamp_end = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ObjectDetection(Base):
    __tablename__ = "object_detections"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, nullable=False, index=True)
    timestamp = Column(Float, nullable=False)
    objects = Column(JSON, nullable=False)  # Array of detected objects with bounding boxes
    frame_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())