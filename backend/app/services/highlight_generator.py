"""
Advanced highlight reel generation using AI-powered content analysis
"""
import numpy as np
from typing import List, Dict, Any, Tuple
from transformers import pipeline
import torch
from ..services.ai_services import SentimentAnalysisService
import moviepy.editor as mp
import logging

logger = logging.getLogger(__name__)

class HighlightGenerator:
    def __init__(self):
        self.sentiment_service = SentimentAnalysisService()
        self.emotion_classifier = pipeline(
            "audio-classification",
            model="ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition",
            device=0 if torch.cuda.is_available() else -1
        )
        
    async def detect_highlight_moments(self, 
                                     transcription_segments: List[Dict],
                                     sentiment_data: Dict,
                                     audio_path: str,
                                     video_path: str) -> List[Dict[str, Any]]:
        """
        Detect highlight moments using multiple AI signals:
        - Emotional peaks in audio
        - Sentiment changes
        - Topic transitions
        - Visual activity (object detection changes)
        """
        highlights = []
        
        # 1. Emotional Audio Analysis
        emotion_peaks = await self._detect_emotional_peaks(audio_path)
        
        # 2. Sentiment Change Points
        sentiment_changes = self._detect_sentiment_changes(sentiment_data)
        
        # 3. Topic Transitions (using sentence embeddings)
        topic_transitions = await self._detect_topic_transitions(transcription_segments)
        
        # 4. Visual Activity Spikes
        visual_spikes = await self._detect_visual_activity_spikes(video_path)
        
        # 5. Combine all signals to score segments
        segments = self._create_time_segments(transcription_segments)
        
        for segment in segments:
            score = 0
            reasons = []
            
            # Score emotional content
            emotion_score = self._get_emotion_score_for_segment(emotion_peaks, segment)
            score += emotion_score * 0.3
            if emotion_score > 0.7:
                reasons.append(f"High emotional content ({emotion_score:.2f})")
            
            # Score sentiment changes
            sentiment_score = self._get_sentiment_change_score(sentiment_changes, segment)
            score += sentiment_score * 0.25
            if sentiment_score > 0.6:
                reasons.append(f"Sentiment transition ({sentiment_score:.2f})")
            
            # Score topic transitions
            topic_score = self._get_topic_transition_score(topic_transitions, segment)
            score += topic_score * 0.25
            if topic_score > 0.6:
                reasons.append(f"Topic change ({topic_score:.2f})")
            
            # Score visual activity
            visual_score = self._get_visual_activity_score(visual_spikes, segment)
            score += visual_score * 0.2
            if visual_score > 0.7:
                reasons.append(f"High visual activity ({visual_score:.2f})")
            
            # Add highlights above threshold
            if score > 0.5:
                highlights.append({
                    "start_time": segment["start"],
                    "end_time": segment["end"],
                    "score": score,
                    "reasons": reasons,
                    "text": segment.get("text", ""),
                    "type": self._classify_highlight_type(reasons)
                })
        
        # Sort by score and return top highlights
        highlights.sort(key=lambda x: x["score"], reverse=True)
        return highlights[:10]  # Top 10 highlights
    
    async def _detect_emotional_peaks(self, audio_path: str) -> List[Dict]:
        """Detect emotional peaks in audio using emotion recognition"""
        try:
            # Load and segment audio
            audio = mp.AudioFileClip(audio_path)
            duration = audio.duration
            
            emotions = []
            segment_length = 10  # 10-second segments
            
            for start in range(0, int(duration), segment_length):
                end = min(start + segment_length, duration)
                segment_audio = audio.subclip(start, end)
                
                # Save temporary segment
                temp_path = f"/tmp/emotion_segment_{start}.wav"
                segment_audio.write_audiofile(temp_path, verbose=False, logger=None)
                
                # Classify emotion
                emotion_result = self.emotion_classifier(temp_path)
                
                emotions.append({
                    "start": start,
                    "end": end,
                    "emotion": emotion_result[0]["label"],
                    "confidence": emotion_result[0]["score"]
                })
                
                segment_audio.close()
            
            audio.close()
            
            # Find peaks (high-confidence, high-energy emotions)
            peaks = []
            high_energy_emotions = ["angry", "excited", "happy", "surprised"]
            
            for emotion in emotions:
                if (emotion["emotion"] in high_energy_emotions and 
                    emotion["confidence"] > 0.7):
                    peaks.append(emotion)
            
            return peaks
            
        except Exception as e:
            logger.error(f"Emotion detection failed: {e}")
            return []
    
    def _detect_sentiment_changes(self, sentiment_data: Dict) -> List[Dict]:
        """Detect significant sentiment transitions"""
        if not sentiment_data.get("segments"):
            return []
        
        changes = []
        segments = sentiment_data["segments"]
        
        for i in range(1, len(segments)):
            prev_sentiment = segments[i-1]["sentiment"]
            curr_sentiment = segments[i]["sentiment"]
            
            # Detect sentiment flips
            if prev_sentiment != curr_sentiment:
                # Calculate intensity of change
                intensity = abs(segments[i]["confidence_score"] - segments[i-1]["confidence_score"])
                
                changes.append({
                    "timestamp": segments[i]["segment_index"] * 512,  # Approximate time
                    "from_sentiment": prev_sentiment,
                    "to_sentiment": curr_sentiment,
                    "intensity": intensity
                })
        
        return changes
    
    async def _detect_topic_transitions(self, transcription_segments: List[Dict]) -> List[Dict]:
        """Detect topic transitions using sentence similarity"""
        if len(transcription_segments) < 2:
            return []
        
        # Use sentence transformers for semantic similarity
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            
            texts = [seg.get("text", "") for seg in transcription_segments]
            embeddings = model.encode(texts)
            
            transitions = []
            threshold = 0.3  # Similarity threshold
            
            for i in range(1, len(embeddings)):
                # Calculate cosine similarity
                similarity = np.dot(embeddings[i-1], embeddings[i]) / (
                    np.linalg.norm(embeddings[i-1]) * np.linalg.norm(embeddings[i])
                )
                
                # Low similarity indicates topic change
                if similarity < threshold:
                    transitions.append({
                        "timestamp": transcription_segments[i].get("start_time", i * 30),
                        "similarity": similarity,
                        "intensity": 1 - similarity
                    })
            
            return transitions
            
        except ImportError:
            logger.warning("sentence-transformers not available, skipping topic detection")
            return []
        except Exception as e:
            logger.error(f"Topic transition detection failed: {e}")
            return []
    
    async def _detect_visual_activity_spikes(self, video_path: str) -> List[Dict]:
        """Detect visual activity spikes using frame difference analysis"""
        try:
            video = mp.VideoFileClip(video_path)
            duration = video.duration
            fps = video.fps
            
            spikes = []
            sample_rate = 5  # Sample every 5 seconds
            
            prev_frame = None
            for t in range(0, int(duration), sample_rate):
                frame = video.get_frame(t)
                
                if prev_frame is not None:
                    # Calculate frame difference
                    diff = np.mean(np.abs(frame.astype(float) - prev_frame.astype(float)))
                    
                    # High difference indicates visual activity
                    if diff > 30:  # Threshold for activity
                        spikes.append({
                            "timestamp": t,
                            "activity_level": diff / 255.0  # Normalize
                        })
                
                prev_frame = frame
            
            video.close()
            return spikes
            
        except Exception as e:
            logger.error(f"Visual activity detection failed: {e}")
            return []
    
    def _create_time_segments(self, transcription_segments: List[Dict]) -> List[Dict]:
        """Create time-based segments for scoring"""
        if not transcription_segments:
            return []
        
        segments = []
        segment_duration = 30  # 30-second segments
        
        # Group transcription by time segments
        current_segment = {"start": 0, "end": segment_duration, "text": ""}
        
        for trans_seg in transcription_segments:
            seg_time = trans_seg.get("start_time", 0)
            
            if seg_time > current_segment["end"]:
                # Start new segment
                segments.append(current_segment)
                current_segment = {
                    "start": current_segment["end"],
                    "end": current_segment["end"] + segment_duration,
                    "text": trans_seg.get("text", "")
                }
            else:
                # Add to current segment
                current_segment["text"] += " " + trans_seg.get("text", "")
        
        # Add final segment
        if current_segment["text"]:
            segments.append(current_segment)
        
        return segments
    
    def _get_emotion_score_for_segment(self, emotion_peaks: List[Dict], segment: Dict) -> float:
        """Calculate emotion score for a time segment"""
        score = 0
        for peak in emotion_peaks:
            if (peak["start"] <= segment["end"] and peak["end"] >= segment["start"]):
                score = max(score, peak["confidence"])
        return score
    
    def _get_sentiment_change_score(self, sentiment_changes: List[Dict], segment: Dict) -> float:
        """Calculate sentiment change score for a time segment"""
        score = 0
        for change in sentiment_changes:
            if (segment["start"] <= change["timestamp"] <= segment["end"]):
                score = max(score, change["intensity"])
        return score
    
    def _get_topic_transition_score(self, topic_transitions: List[Dict], segment: Dict) -> float:
        """Calculate topic transition score for a time segment"""
        score = 0
        for transition in topic_transitions:
            if (segment["start"] <= transition["timestamp"] <= segment["end"]):
                score = max(score, transition["intensity"])
        return score
    
    def _get_visual_activity_score(self, visual_spikes: List[Dict], segment: Dict) -> float:
        """Calculate visual activity score for a time segment"""
        score = 0
        for spike in visual_spikes:
            if (segment["start"] <= spike["timestamp"] <= segment["end"]):
                score = max(score, spike["activity_level"])
        return score
    
    def _classify_highlight_type(self, reasons: List[str]) -> str:
        """Classify the type of highlight based on detection reasons"""
        if any("emotional" in reason.lower() for reason in reasons):
            return "emotional_moment"
        elif any("sentiment" in reason.lower() for reason in reasons):
            return "sentiment_shift"
        elif any("topic" in reason.lower() for reason in reasons):
            return "topic_transition"
        elif any("visual" in reason.lower() for reason in reasons):
            return "visual_activity"
        else:
            return "general_interest"
    
    async def create_smart_highlight_reel(self, 
                                        video_path: str,
                                        highlights: List[Dict],
                                        output_path: str,
                                        max_duration: int = 120) -> str:
        """Create an optimized highlight reel with transitions and titles"""
        try:
            video = mp.VideoFileClip(video_path)
            
            # Sort highlights by score and time
            sorted_highlights = sorted(highlights, key=lambda x: (x["score"], x["start_time"]), reverse=True)
            
            clips = []
            total_duration = 0
            
            for highlight in sorted_highlights:
                if total_duration >= max_duration:
                    break
                
                # Extract clip with some padding
                start = max(0, highlight["start_time"] - 2)
                end = min(video.duration, highlight["end_time"] + 2)
                clip_duration = end - start
                
                if total_duration + clip_duration > max_duration:
                    # Trim to fit
                    clip_duration = max_duration - total_duration
                    end = start + clip_duration
                
                clip = video.subclip(start, end)
                
                # Add title overlay
                title_text = f"{highlight['type'].replace('_', ' ').title()}"
                title = mp.TextClip(title_text, 
                                  fontsize=24, 
                                  color='white',
                                  bg_color='black',
                                  size=clip.size).set_duration(2)
                
                # Composite title at the beginning
                clip_with_title = mp.CompositeVideoClip([clip, title.set_position(('center', 'top'))])
                clips.append(clip_with_title)
                
                total_duration += clip_duration
            
            if not clips:
                raise ValueError("No suitable clips found for highlight reel")
            
            # Create final video with transitions
            final_video = mp.concatenate_videoclips(clips, method="compose")
            
            # Add background music (optional)
            # final_video = final_video.set_audio(background_music.set_duration(final_video.duration))
            
            # Write final video
            final_video.write_videofile(
                output_path,
                fps=24,
                verbose=False,
                logger=None
            )
            
            # Cleanup
            final_video.close()
            video.close()
            for clip in clips:
                clip.close()
            
            return output_path
            
        except Exception as e:
            logger.error(f"Smart highlight reel creation failed: {e}")
            raise