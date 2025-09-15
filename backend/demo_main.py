"""
Demo version of main.py that runs without external dependencies
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import os
import uuid
import json
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Polyglot Media Analyzer - Demo",
    version="1.0.0",
    description="AI-powered multilingual media analysis platform",
    openapi_url="/api/v1/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo
demo_files = {}
demo_analytics = {
    "overview": {
        "total_files": 42,
        "total_duration": 15840,  # seconds
        "languages_detected": 8,
        "models_utilized": 5,
        "highlight_reels": 17,
        "avg_highlight_duration": 45,
        "files_growth": 23
    },
    "processing_trends": [
        {"date": "2025-09-08", "video_files": 12, "audio_files": 8},
        {"date": "2025-09-09", "video_files": 15, "audio_files": 10},
        {"date": "2025-09-10", "video_files": 18, "audio_files": 12},
        {"date": "2025-09-11", "video_files": 14, "audio_files": 9},
        {"date": "2025-09-12", "video_files": 20, "audio_files": 15},
        {"date": "2025-09-13", "video_files": 22, "audio_files": 18},
        {"date": "2025-09-14", "video_files": 25, "audio_files": 20}
    ],
    "language_distribution": [
        {"name": "English", "count": 156},
        {"name": "Spanish", "count": 89},
        {"name": "French", "count": 67},
        {"name": "German", "count": 45},
        {"name": "Japanese", "count": 34},
        {"name": "Portuguese", "count": 28}
    ],
    "sentiment_trends": [
        {"date": "2025-09-08", "positive": 45, "neutral": 35, "negative": 20},
        {"date": "2025-09-09", "positive": 50, "neutral": 30, "negative": 20},
        {"date": "2025-09-10", "positive": 48, "neutral": 32, "negative": 20},
        {"date": "2025-09-11", "positive": 52, "neutral": 28, "negative": 20},
        {"date": "2025-09-12", "positive": 55, "neutral": 25, "negative": 20},
        {"date": "2025-09-13", "positive": 53, "neutral": 27, "negative": 20},
        {"date": "2025-09-14", "positive": 58, "neutral": 22, "negative": 20}
    ],
    "top_objects": [
        {"object": "person", "count": 245},
        {"object": "car", "count": 123},
        {"object": "building", "count": 98},
        {"object": "tree", "count": 87},
        {"object": "computer", "count": 65},
        {"object": "phone", "count": 54}
    ],
    "model_performance": [
        {"model": "Whisper ASR", "accuracy": 92, "avg_processing_time": 15},
        {"model": "BART Summarization", "accuracy": 88, "avg_processing_time": 8},
        {"model": "RoBERTa Sentiment", "accuracy": 94, "avg_processing_time": 3},
        {"model": "DETR Object Detection", "accuracy": 86, "avg_processing_time": 12},
        {"model": "Helsinki Translation", "accuracy": 89, "avg_processing_time": 5}
    ],
    "top_searches": [
        {"query": "meeting highlights", "count": 45},
        {"query": "positive sentiment", "count": 38},
        {"query": "product demo", "count": 32},
        {"query": "keynote presentation", "count": 28},
        {"query": "customer feedback", "count": 24}
    ],
    "file_type_distribution": [
        {"name": "MP4 Video", "count": 123},
        {"name": "MP3 Audio", "count": 89},
        {"name": "WAV Audio", "count": 67},
        {"name": "AVI Video", "count": 34}
    ],
    "realtime": {
        "active_streams": 3,
        "queue_length": 12,
        "avg_processing_time": 8.5,
        "gpu_utilization": 72
    }
}

# Pydantic models
class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    message: str
    status: str

class ProcessingStatus(BaseModel):
    file_id: str
    status: str
    progress: int
    current_task: str
    estimated_time_remaining: Optional[int] = None

class SearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = {}
    limit: Optional[int] = 20

# Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🌍 Welcome to Polyglot Media Analyzer Demo!",
        "version": "1.0.0",
        "docs_url": "/docs",
        "api_url": "/api/v1",
        "demo_mode": True,
        "features": [
            "🎵 Audio & Video Processing",
            "🗣️ Real-time Transcription", 
            "🌍 Multilingual Translation",
            "📄 AI Summarization",
            "😊 Sentiment Analysis",
            "👁️ Object Detection",
            "🎬 Highlight Reels",
            "🔍 Smart Search",
            "📊 Analytics Dashboard"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0", "demo_mode": True}

@app.post("/api/v1/media/upload", response_model=FileUploadResponse)
async def upload_media(file: UploadFile = File(...)):
    """Upload media file for processing"""
    try:
        # Generate file ID
        file_id = str(uuid.uuid4())
        
        # Store demo file info
        demo_files[file_id] = {
            "filename": file.filename,
            "content_type": file.content_type,
            "upload_time": datetime.now().isoformat(),
            "status": "processing",
            "progress": 0
        }
        
        logger.info(f"Demo upload: {file.filename} -> {file_id}")
        
        return FileUploadResponse(
            file_id=file_id,
            filename=file.filename,
            message="File uploaded successfully (Demo Mode)",
            status="processing"
        )
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/media/status/{file_id}", response_model=ProcessingStatus)
async def get_processing_status(file_id: str):
    """Get processing status for a file"""
    if file_id not in demo_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Simulate processing progress
    file_info = demo_files[file_id]
    
    if file_info["status"] == "processing":
        # Simulate progress
        current_progress = min(file_info["progress"] + 10, 100)
        demo_files[file_id]["progress"] = current_progress
        
        if current_progress >= 100:
            demo_files[file_id]["status"] = "completed"
            current_task = "Processing complete"
            estimated_time = 0
        else:
            tasks = ["Extracting audio", "Transcribing speech", "Analyzing sentiment", "Detecting objects", "Generating summary"]
            current_task = tasks[current_progress // 20] if current_progress // 20 < len(tasks) else "Finalizing"
            estimated_time = (100 - current_progress) * 2  # 2 seconds per percent
    else:
        current_task = "Completed"
        estimated_time = 0
        current_progress = 100
    
    return ProcessingStatus(
        file_id=file_id,
        status=file_info["status"],
        progress=current_progress,
        current_task=current_task,
        estimated_time_remaining=estimated_time
    )

@app.get("/api/v1/media/transcription/{file_id}")
async def get_transcription(file_id: str):
    """Get transcription results"""
    if file_id not in demo_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {
        "file_id": file_id,
        "transcription": {
            "text": "Welcome to our product demonstration. Today we'll be showcasing the new AI-powered features that make our platform stand out in the market. The advanced machine learning algorithms provide real-time analysis with incredible accuracy.",
            "language": "en",
            "confidence_score": 0.94,
            "segments": [
                {"start_time": 0.0, "end_time": 3.2, "text": "Welcome to our product demonstration.", "confidence": 0.96},
                {"start_time": 3.5, "end_time": 8.1, "text": "Today we'll be showcasing the new AI-powered features", "confidence": 0.93},
                {"start_time": 8.3, "end_time": 12.7, "text": "that make our platform stand out in the market.", "confidence": 0.92}
            ]
        }
    }

@app.get("/api/v1/media/summary/{file_id}")
async def get_summary(file_id: str):
    """Get AI-generated summary"""
    if file_id not in demo_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {
        "file_id": file_id,
        "summary": {
            "text": "This video presents a product demonstration highlighting AI-powered features and advanced machine learning capabilities that differentiate the platform in the competitive market landscape.",
            "key_points": [
                "Product demonstration of new features",
                "AI-powered platform capabilities", 
                "Advanced machine learning algorithms",
                "Real-time analysis functionality",
                "High accuracy performance metrics"
            ],
            "summary_type": "abstractive"
        }
    }

@app.get("/api/v1/media/sentiment/{file_id}")
async def get_sentiment(file_id: str):
    """Get sentiment analysis results"""
    if file_id not in demo_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {
        "file_id": file_id,
        "sentiment": {
            "overall_sentiment": "positive",
            "overall_confidence": 0.87,
            "segments": [
                {"segment": "Welcome to our product demonstration", "sentiment": "positive", "confidence_score": 0.89},
                {"segment": "AI-powered features", "sentiment": "positive", "confidence_score": 0.91},
                {"segment": "stand out in the market", "sentiment": "positive", "confidence_score": 0.85}
            ]
        }
    }

@app.post("/api/v1/search/search")
async def search_content(request: SearchRequest):
    """Search media content"""
    # Demo search results
    results = [
        {
            "file_id": "demo-1",
            "score": 0.95,
            "source": {
                "filename": "product_demo.mp4",
                "file_type": "video",
                "language": "en",
                "sentiment": "positive",
                "duration": 180.5,
                "transcription_text": "Welcome to our revolutionary AI platform that transforms how businesses handle multilingual content...",
                "summary_text": "Product demonstration showcasing AI-powered multilingual content processing capabilities.",
                "objects_detected": ["person", "computer", "presentation", "logo"],
                "created_at": "2025-09-14T10:30:00Z"
            },
            "highlights": {
                "transcription_text": [f"Welcome to our revolutionary <mark>{request.query}</mark> platform..."],
                "summary_text": [f"Product demonstration showcasing <mark>{request.query}</mark> capabilities..."]
            }
        },
        {
            "file_id": "demo-2", 
            "score": 0.82,
            "source": {
                "filename": "customer_interview.mp3",
                "file_type": "audio",
                "language": "en",
                "sentiment": "positive",
                "duration": 245.2,
                "transcription_text": "The new AI features have completely transformed our workflow and productivity...",
                "summary_text": "Customer testimonial highlighting positive impact of AI features on business operations.",
                "objects_detected": [],
                "created_at": "2025-09-13T14:20:00Z"
            },
            "highlights": {
                "transcription_text": [f"The new <mark>{request.query}</mark> features have completely transformed..."],
                "summary_text": []
            }
        }
    ]
    
    return {
        "total": len(results),
        "results": results,
        "query": request.query,
        "filters": request.filters
    }

@app.get("/api/v1/search/analytics/overview")
async def get_analytics(timeframe: str = "30d"):
    """Get analytics overview"""
    return demo_analytics

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "demo_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )