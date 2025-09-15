from transformers import DetrImageProcessor, DetrForObjectDetection
import torch
import cv2
import numpy as np
from PIL import Image
import moviepy.editor as mp
import os
import logging
from typing import List, Dict, Any, Tuple
from ..core.config import settings

logger = logging.getLogger(__name__)

class ObjectDetectionService:
    def __init__(self):
        self.model_name = settings.OBJECT_DETECTION_MODEL
        self.processor = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._load_model()
    
    def _load_model(self):
        try:
            self.processor = DetrImageProcessor.from_pretrained(self.model_name)
            self.model = DetrForObjectDetection.from_pretrained(self.model_name)
            self.model.to(self.device)
            logger.info(f"Object detection model loaded: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load object detection model: {e}")
            raise
    
    async def detect_objects_in_video(self, video_path: str, sample_rate: int = 5) -> List[Dict[str, Any]]:
        """Detect objects in video frames at specified sample rate (seconds)"""
        try:
            # Load video
            video = mp.VideoFileClip(video_path)
            duration = video.duration
            
            detections = []
            
            # Sample frames at specified intervals
            for timestamp in range(0, int(duration), sample_rate):
                frame = video.get_frame(timestamp)
                frame_pil = Image.fromarray(frame)
                
                # Detect objects in frame
                objects = await self._detect_objects_in_frame(frame_pil)
                
                if objects:
                    detections.append({
                        "timestamp": timestamp,
                        "objects": objects,
                        "frame_number": timestamp * video.fps
                    })
            
            video.close()
            return detections
            
        except Exception as e:
            logger.error(f"Object detection in video failed: {e}")
            raise
    
    async def _detect_objects_in_frame(self, image: Image.Image, confidence_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Detect objects in a single frame"""
        try:
            # Preprocess image
            inputs = self.processor(images=image, return_tensors="pt").to(self.device)
            
            # Run inference
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            # Post-process results
            target_sizes = torch.tensor([image.size[::-1]]).to(self.device)
            results = self.processor.post_process_object_detection(
                outputs, 
                target_sizes=target_sizes, 
                threshold=confidence_threshold
            )[0]
            
            objects = []
            for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
                objects.append({
                    "label": self.model.config.id2label[label.item()],
                    "confidence": score.item(),
                    "bbox": {
                        "x": box[0].item(),
                        "y": box[1].item(),
                        "width": box[2].item() - box[0].item(),
                        "height": box[3].item() - box[1].item()
                    }
                })
            
            return objects
            
        except Exception as e:
            logger.error(f"Object detection in frame failed: {e}")
            return []

class VideoProcessingService:
    def __init__(self):
        pass
    
    async def extract_audio_from_video(self, video_path: str, output_path: str) -> str:
        """Extract audio from video file"""
        try:
            video = mp.VideoFileClip(video_path)
            audio = video.audio
            
            if audio is None:
                raise ValueError("No audio track found in video")
            
            audio.write_audiofile(output_path, verbose=False, logger=None)
            audio.close()
            video.close()
            
            return output_path
            
        except Exception as e:
            logger.error(f"Audio extraction failed: {e}")
            raise
    
    async def extract_keyframes(self, video_path: str, output_dir: str, num_frames: int = 10) -> List[str]:
        """Extract key frames from video"""
        try:
            video = mp.VideoFileClip(video_path)
            duration = video.duration
            
            # Calculate frame timestamps
            timestamps = np.linspace(0, duration - 1, num_frames)
            
            frame_paths = []
            os.makedirs(output_dir, exist_ok=True)
            
            for i, timestamp in enumerate(timestamps):
                frame = video.get_frame(timestamp)
                frame_path = os.path.join(output_dir, f"frame_{i:03d}.jpg")
                
                # Convert numpy array to PIL Image and save
                frame_pil = Image.fromarray(frame)
                frame_pil.save(frame_path, "JPEG")
                frame_paths.append(frame_path)
            
            video.close()
            return frame_paths
            
        except Exception as e:
            logger.error(f"Keyframe extraction failed: {e}")
            raise
    
    async def create_highlight_reel(self, video_path: str, highlights: List[Tuple[float, float]], output_path: str) -> str:
        """Create highlight reel from video segments"""
        try:
            video = mp.VideoFileClip(video_path)
            
            # Extract highlight clips
            clips = []
            for start_time, end_time in highlights:
                clip = video.subclip(start_time, end_time)
                clips.append(clip)
            
            if not clips:
                raise ValueError("No highlight clips to process")
            
            # Concatenate clips
            final_video = mp.concatenate_videoclips(clips)
            
            # Write final video
            final_video.write_videofile(
                output_path,
                verbose=False,
                logger=None,
                temp_audiofile_path=None
            )
            
            # Cleanup
            final_video.close()
            for clip in clips:
                clip.close()
            video.close()
            
            return output_path
            
        except Exception as e:
            logger.error(f"Highlight reel creation failed: {e}")
            raise
    
    async def get_video_metadata(self, video_path: str) -> Dict[str, Any]:
        """Extract metadata from video file"""
        try:
            video = mp.VideoFileClip(video_path)
            
            metadata = {
                "duration": video.duration,
                "fps": video.fps,
                "size": video.size,
                "has_audio": video.audio is not None
            }
            
            video.close()
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            raise