from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import aiofiles
import os
import uuid
import logging
from typing import List, Optional
import asyncio

from ..core.database import get_db, AsyncSessionLocal
from ..core.config import settings
from ..models.media import MediaFile, ProcessingResult, Transcription, Translation, Summary, SentimentAnalysis, ObjectDetection
from ..services import (
    ASRService, TranslationService, SummarizationService, 
    SentimentAnalysisService, ObjectDetectionService, 
    VideoProcessingService, ElasticSearchService
)
from ..api.schemas import (
    FileUploadResponse, ProcessingStatus, TranscriptionResponse,
    TranslationRequest, TranslationResponse, SummaryResponse,
    SentimentResponse, ObjectDetectionResponse, HighlightRequest,
    HighlightResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services
asr_service = ASRService()
translation_service = TranslationService()
summarization_service = SummarizationService()
sentiment_service = SentimentAnalysisService()
object_detection_service = ObjectDetectionService()
video_service = VideoProcessingService()
es_service = ElasticSearchService()

@router.post("/upload", response_model=FileUploadResponse)
async def upload_media_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload media file for processing"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file selected")
        
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not supported. Allowed: {settings.ALLOWED_EXTENSIONS}"
            )
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Save file
        file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}_{file.filename}")
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Determine file type
        file_type = "video" if file_extension in [".mp4", ".avi", ".mov"] else "audio"
        
        # Create database record
        media_file = MediaFile(
            file_id=file_id,
            filename=file.filename,
            file_path=file_path,
            file_type=file_type,
            file_size=len(content),
            status="uploaded"
        )
        
        db.add(media_file)
        await db.commit()
        await db.refresh(media_file)
        
        # Start background processing
        background_tasks.add_task(process_media_file, file_id, file_path, file_type)
        
        return FileUploadResponse(
            file_id=file_id,
            filename=file.filename,
            file_type=file_type,
            file_size=len(content),
            status="uploaded",
            message="File uploaded successfully. Processing started."
        )
        
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{file_id}", response_model=ProcessingStatus)
async def get_processing_status(file_id: str, db: AsyncSession = Depends(get_db)):
    """Get processing status for a file"""
    try:
        # Get media file
        result = await db.execute(
            select(MediaFile).where(MediaFile.file_id == file_id)
        )
        media_file = result.scalar_one_or_none()
        
        if not media_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get processing results
        results_query = await db.execute(
            select(ProcessingResult).where(ProcessingResult.file_id == file_id)
        )
        processing_results = results_query.scalars().all()
        
        # Compile results
        results = {}
        for result in processing_results:
            results[result.task_type] = result.result_data
        
        return ProcessingStatus(
            file_id=file_id,
            status=media_file.status,
            results=results if results else None
        )
        
    except Exception as e:
        logger.error(f"Status retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transcription/{file_id}", response_model=TranscriptionResponse)
async def get_transcription(file_id: str, db: AsyncSession = Depends(get_db)):
    """Get transcription for a file"""
    try:
        result = await db.execute(
            select(Transcription).where(Transcription.file_id == file_id)
        )
        transcription = result.scalar_one_or_none()
        
        if not transcription:
            raise HTTPException(status_code=404, detail="Transcription not found")
        
        return TranscriptionResponse(
            file_id=transcription.file_id,
            language=transcription.language,
            text=transcription.text,
            timestamps=transcription.timestamps,
            confidence_score=transcription.confidence_score,
            created_at=transcription.created_at
        )
        
    except Exception as e:
        logger.error(f"Transcription retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/translate/{file_id}", response_model=TranslationResponse)
async def translate_content(
    file_id: str,
    translation_request: TranslationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Translate content for a file"""
    try:
        # Perform translation
        translation_result = await translation_service.translate_text(
            translation_request.text,
            translation_request.source_language,
            translation_request.target_language
        )
        
        # Save to database
        translation = Translation(
            file_id=file_id,
            source_language=translation_request.source_language,
            target_language=translation_request.target_language,
            original_text=translation_request.text,
            translated_text=translation_result["translated_text"],
            confidence_score=translation_result["confidence_score"]
        )
        
        db.add(translation)
        await db.commit()
        await db.refresh(translation)
        
        return TranslationResponse(
            file_id=translation.file_id,
            source_language=translation.source_language,
            target_language=translation.target_language,
            original_text=translation.original_text,
            translated_text=translation.translated_text,
            confidence_score=translation.confidence_score,
            created_at=translation.created_at
        )
        
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary/{file_id}", response_model=SummaryResponse)
async def get_summary(file_id: str, db: AsyncSession = Depends(get_db)):
    """Get summary for a file"""
    try:
        result = await db.execute(
            select(Summary).where(Summary.file_id == file_id)
        )
        summary = result.scalar_one_or_none()
        
        if not summary:
            raise HTTPException(status_code=404, detail="Summary not found")
        
        return SummaryResponse(
            file_id=summary.file_id,
            language=summary.language,
            original_text=summary.original_text,
            summary_text=summary.summary_text,
            summary_type=summary.summary_type,
            created_at=summary.created_at
        )
        
    except Exception as e:
        logger.error(f"Summary retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sentiment/{file_id}", response_model=SentimentResponse)
async def get_sentiment_analysis(file_id: str, db: AsyncSession = Depends(get_db)):
    """Get sentiment analysis for a file"""
    try:
        result = await db.execute(
            select(SentimentAnalysis).where(SentimentAnalysis.file_id == file_id)
        )
        sentiment_results = result.scalars().all()
        
        if not sentiment_results:
            raise HTTPException(status_code=404, detail="Sentiment analysis not found")
        
        # Aggregate results
        segments = []
        sentiment_counts = {}
        total_confidence = 0
        
        for sentiment in sentiment_results:
            segments.append({
                "text": sentiment.text_segment,
                "sentiment": sentiment.sentiment,
                "confidence": sentiment.confidence_score,
                "timestamp_start": sentiment.timestamp_start,
                "timestamp_end": sentiment.timestamp_end
            })
            
            sentiment_counts[sentiment.sentiment] = sentiment_counts.get(sentiment.sentiment, 0) + 1
            total_confidence += sentiment.confidence_score
        
        overall_sentiment = max(sentiment_counts, key=sentiment_counts.get)
        avg_confidence = total_confidence / len(sentiment_results)
        
        return SentimentResponse(
            file_id=file_id,
            overall_sentiment=overall_sentiment,
            overall_confidence=avg_confidence,
            segments=segments,
            created_at=sentiment_results[0].created_at
        )
        
    except Exception as e:
        logger.error(f"Sentiment analysis retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/objects/{file_id}", response_model=ObjectDetectionResponse)
async def get_object_detection(file_id: str, db: AsyncSession = Depends(get_db)):
    """Get object detection results for a file"""
    try:
        result = await db.execute(
            select(ObjectDetection).where(ObjectDetection.file_id == file_id)
        )
        detections = result.scalars().all()
        
        if not detections:
            raise HTTPException(status_code=404, detail="Object detection results not found")
        
        detection_data = []
        for detection in detections:
            detection_data.append({
                "timestamp": detection.timestamp,
                "objects": detection.objects,
                "frame_path": detection.frame_path
            })
        
        return ObjectDetectionResponse(
            file_id=file_id,
            detections=detection_data,
            total_frames=len(detections),
            created_at=detections[0].created_at
        )
        
    except Exception as e:
        logger.error(f"Object detection retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/highlight/{file_id}", response_model=HighlightResponse)
async def create_highlight_reel(
    file_id: str,
    highlight_request: HighlightRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create highlight reel from specified segments"""
    try:
        # Get media file
        result = await db.execute(
            select(MediaFile).where(MediaFile.file_id == file_id)
        )
        media_file = result.scalar_one_or_none()
        
        if not media_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        if media_file.file_type != "video":
            raise HTTPException(status_code=400, detail="Highlight reels can only be created for videos")
        
        # Extract segments
        segments = [(seg["start"], seg["end"]) for seg in highlight_request.segments]
        
        # Create highlight reel
        output_path = os.path.join(
            settings.UPLOAD_DIR, 
            f"{file_id}_highlights.mp4"
        )
        
        highlight_path = await video_service.create_highlight_reel(
            media_file.file_path,
            segments,
            output_path
        )
        
        total_duration = sum(seg["end"] - seg["start"] for seg in highlight_request.segments)
        
        return HighlightResponse(
            file_id=file_id,
            highlight_video_path=highlight_path,
            segments_count=len(segments),
            total_duration=total_duration,
            created_at=media_file.created_at
        )
        
    except Exception as e:
        logger.error(f"Highlight reel creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_media_file(file_id: str, file_path: str, file_type: str):
    """Background task to process uploaded media file"""
    try:
        # Create new database session for background task
        async with AsyncSessionLocal() as db:
            # Update status
            result = await db.execute(
                select(MediaFile).where(MediaFile.file_id == file_id)
            )
            media_file = result.scalar_one_or_none()
            if media_file:
                media_file.status = "processing"
                await db.commit()
            
            # Extract audio if video
            audio_path = file_path
            if file_type == "video":
                audio_path = file_path.replace(os.path.splitext(file_path)[1], ".wav")
                await video_service.extract_audio_from_video(file_path, audio_path)
            
            # Transcription
            transcription_result = await asr_service.transcribe_audio(audio_path)
            transcription = Transcription(
                file_id=file_id,
                language=transcription_result["language"],
                text=transcription_result["text"],
                timestamps=transcription_result["timestamps"],
                confidence_score=transcription_result["confidence_score"]
            )
            db.add(transcription)
            
            # Summarization
            summary_result = await summarization_service.summarize_text(transcription_result["text"])
            summary = Summary(
                file_id=file_id,
                language=transcription_result["language"],
                original_text=transcription_result["text"],
                summary_text=summary_result["summary_text"],
                summary_type=summary_result["summary_type"]
            )
            db.add(summary)
            
            # Sentiment Analysis
            sentiment_result = await sentiment_service.analyze_sentiment(transcription_result["text"])
            for segment in sentiment_result["segments"]:
                sentiment = SentimentAnalysis(
                    file_id=file_id,
                    text_segment=segment["segment"],
                    sentiment=segment["sentiment"],
                    confidence_score=segment["confidence_score"]
                )
                db.add(sentiment)
            
            # Object Detection for videos
            object_results = []
            if file_type == "video":
                object_results = await object_detection_service.detect_objects_in_video(file_path)
                for detection in object_results:
                    obj_detection = ObjectDetection(
                        file_id=file_id,
                        timestamp=detection["timestamp"],
                        objects=detection["objects"]
                    )
                    db.add(obj_detection)
            
            # Update status
            if media_file:
                media_file.status = "completed"
                await db.commit()
            
            # Index in ElasticSearch
            await index_media_content(file_id, {
                "file_id": file_id,
                "filename": media_file.filename if media_file else "",
                "file_type": file_type,
                "transcription_text": transcription_result["text"],
                "summary_text": summary_result["summary_text"],
                "language": transcription_result["language"],
                "sentiment": sentiment_result["overall_sentiment"],
                "objects_detected": [obj["label"] for detection in object_results for obj in detection["objects"]] if file_type == "video" else [],
                "created_at": media_file.created_at.isoformat() if media_file else "",
                "duration": media_file.duration if media_file else 0
            })
        
    except Exception as e:
        logger.error(f"Media processing failed for {file_id}: {e}")
        # Update status to error
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(MediaFile).where(MediaFile.file_id == file_id)
            )
            media_file = result.scalar_one_or_none()
            if media_file:
                media_file.status = "error"
                await db.commit()

async def index_media_content(file_id: str, content: dict):
    """Index media content in ElasticSearch"""
    try:
        await es_service.index_media_content(file_id, content)
    except Exception as e:
        logger.error(f"ElasticSearch indexing failed: {e}")