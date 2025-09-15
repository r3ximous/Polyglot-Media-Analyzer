"""
Real-time streaming service for live video/audio processing
"""
import asyncio
import websockets
import json
from typing import Dict, Any, List
import cv2
import numpy as np
from .ai_services import ASRService, SentimentAnalysisService
from .video_processing import ObjectDetectionService
import logging

logger = logging.getLogger(__name__)

class StreamingService:
    def __init__(self):
        self.asr_service = ASRService()
        self.sentiment_service = SentimentAnalysisService()
        self.object_detection_service = ObjectDetectionService()
        self.active_streams = {}
        
    async def start_streaming_session(self, session_id: str, stream_config: Dict[str, Any]):
        """Start a new streaming session"""
        self.active_streams[session_id] = {
            "config": stream_config,
            "buffer": [],
            "results": []
        }
        logger.info(f"Started streaming session: {session_id}")
        
    async def process_audio_chunk(self, session_id: str, audio_chunk: bytes) -> Dict[str, Any]:
        """Process incoming audio chunk"""
        if session_id not in self.active_streams:
            raise ValueError(f"Session {session_id} not found")
            
        # Add to buffer
        self.active_streams[session_id]["buffer"].append(audio_chunk)
        
        # Process when buffer is full enough
        if len(self.active_streams[session_id]["buffer"]) >= 5:  # ~5 seconds
            combined_audio = b''.join(self.active_streams[session_id]["buffer"])
            
            # Save temporarily and transcribe
            temp_path = f"/tmp/stream_{session_id}.wav"
            with open(temp_path, "wb") as f:
                f.write(combined_audio)
                
            # Transcribe
            transcription = await self.asr_service.transcribe_audio(temp_path)
            
            # Analyze sentiment
            sentiment = await self.sentiment_service.analyze_sentiment(transcription["text"])
            
            result = {
                "timestamp": len(self.active_streams[session_id]["results"]) * 5,
                "transcription": transcription,
                "sentiment": sentiment,
                "session_id": session_id
            }
            
            self.active_streams[session_id]["results"].append(result)
            self.active_streams[session_id]["buffer"] = []  # Clear buffer
            
            return result
            
        return {"status": "buffering"}
        
    async def process_video_frame(self, session_id: str, frame_data: bytes) -> Dict[str, Any]:
        """Process incoming video frame"""
        if session_id not in self.active_streams:
            raise ValueError(f"Session {session_id} not found")
            
        # Convert frame data to image
        nparr = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect objects (sample every 10th frame for performance)
        frame_count = len(self.active_streams[session_id]["results"])
        if frame_count % 10 == 0:
            from PIL import Image
            pil_image = Image.fromarray(frame_rgb)
            objects = await self.object_detection_service._detect_objects_in_frame(pil_image)
            
            return {
                "frame_number": frame_count,
                "objects": objects,
                "timestamp": frame_count / 30.0,  # Assuming 30 FPS
                "session_id": session_id
            }
            
        return {"status": "skipped_frame"}
        
    async def get_live_insights(self, session_id: str) -> Dict[str, Any]:
        """Get real-time insights from streaming session"""
        if session_id not in self.active_streams:
            raise ValueError(f"Session {session_id} not found")
            
        results = self.active_streams[session_id]["results"]
        
        if not results:
            return {"status": "no_data"}
            
        # Aggregate insights
        all_text = " ".join([r["transcription"]["text"] for r in results])
        sentiments = [r["sentiment"]["overall_sentiment"] for r in results]
        
        # Calculate trending sentiment
        sentiment_trend = "stable"
        if len(sentiments) >= 3:
            recent = sentiments[-3:]
            if all(s == "positive" for s in recent):
                sentiment_trend = "improving"
            elif all(s == "negative" for s in recent):
                sentiment_trend = "declining"
                
        return {
            "session_duration": len(results) * 5,
            "total_words": len(all_text.split()),
            "sentiment_trend": sentiment_trend,
            "current_sentiment": sentiments[-1] if sentiments else "neutral",
            "recent_transcription": results[-1]["transcription"]["text"] if results else "",
            "session_id": session_id
        }
        
    async def end_streaming_session(self, session_id: str) -> Dict[str, Any]:
        """End streaming session and return final summary"""
        if session_id not in self.active_streams:
            raise ValueError(f"Session {session_id} not found")
            
        session_data = self.active_streams[session_id]
        final_summary = await self.get_live_insights(session_id)
        
        # Clean up
        del self.active_streams[session_id]
        
        logger.info(f"Ended streaming session: {session_id}")
        return final_summary


class WebSocketHandler:
    def __init__(self):
        self.streaming_service = StreamingService()
        
    async def handle_websocket(self, websocket, path):
        """Handle WebSocket connections for real-time streaming"""
        session_id = None
        try:
            async for message in websocket:
                data = json.loads(message)
                
                if data["type"] == "start_session":
                    session_id = data["session_id"]
                    await self.streaming_service.start_streaming_session(
                        session_id, 
                        data.get("config", {})
                    )
                    await websocket.send(json.dumps({
                        "type": "session_started",
                        "session_id": session_id
                    }))
                    
                elif data["type"] == "audio_chunk":
                    result = await self.streaming_service.process_audio_chunk(
                        data["session_id"], 
                        data["audio_data"].encode()
                    )
                    await websocket.send(json.dumps({
                        "type": "transcription_result",
                        "data": result
                    }))
                    
                elif data["type"] == "video_frame":
                    result = await self.streaming_service.process_video_frame(
                        data["session_id"],
                        data["frame_data"].encode()
                    )
                    await websocket.send(json.dumps({
                        "type": "object_detection_result", 
                        "data": result
                    }))
                    
                elif data["type"] == "get_insights":
                    insights = await self.streaming_service.get_live_insights(
                        data["session_id"]
                    )
                    await websocket.send(json.dumps({
                        "type": "live_insights",
                        "data": insights
                    }))
                    
        except websockets.exceptions.ConnectionClosed:
            if session_id:
                await self.streaming_service.end_streaming_session(session_id)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            await websocket.send(json.dumps({
                "type": "error",
                "message": str(e)
            }))