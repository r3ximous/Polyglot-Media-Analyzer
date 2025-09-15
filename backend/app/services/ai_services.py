from transformers import (
    AutoModelForSpeechSeq2Seq, 
    AutoProcessor, 
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    AutoModelForSequenceClassification,
    pipeline
)
import torch
import librosa
import numpy as np
from typing import List, Dict, Any, Optional
import asyncio
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)

class ASRService:
    def __init__(self):
        self.model_name = settings.ASR_MODEL
        self.processor = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._load_model()
    
    def _load_model(self):
        try:
            self.processor = AutoProcessor.from_pretrained(self.model_name)
            self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                use_safetensors=True
            )
            logger.info(f"ASR model loaded: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load ASR model: {e}")
            raise
    
    async def transcribe_audio(self, audio_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Transcribe audio file to text with timestamps"""
        try:
            # Load audio file
            audio, sample_rate = librosa.load(audio_path, sr=16000)
            
            # Process audio
            inputs = self.processor(
                audio, 
                sampling_rate=sample_rate, 
                return_tensors="pt"
            ).to(self.device)
            
            # Generate transcription
            with torch.no_grad():
                generated_ids = self.model.generate(
                    inputs["input_features"],
                    max_new_tokens=444,
                    return_timestamps=True
                )
            
            # Decode results
            transcription = self.processor.batch_decode(
                generated_ids, 
                skip_special_tokens=True
            )[0]
            
            return {
                "text": transcription,
                "language": language or "auto-detected",
                "confidence_score": 0.8,  # Placeholder - Whisper doesn't provide confidence scores directly
                "timestamps": []  # Would need additional processing for precise timestamps
            }
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise

class TranslationService:
    def __init__(self):
        self.model_name = settings.TRANSLATION_MODEL
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._load_model()
    
    def _load_model(self):
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            self.model.to(self.device)
            logger.info(f"Translation model loaded: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load translation model: {e}")
            raise
    
    async def translate_text(self, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        """Translate text from source language to target language"""
        try:
            # Prepare input
            input_text = f">>{target_lang}<< {text}"
            inputs = self.tokenizer(input_text, return_tensors="pt", truncation=True).to(self.device)
            
            # Generate translation
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=512,
                    num_beams=4,
                    early_stopping=True
                )
            
            # Decode translation
            translated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            return {
                "original_text": text,
                "translated_text": translated_text,
                "source_language": source_lang,
                "target_language": target_lang,
                "confidence_score": 0.8  # Placeholder
            }
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise

class SummarizationService:
    def __init__(self):
        self.model_name = settings.SUMMARIZATION_MODEL
        self.summarizer = None
        self._load_model()
    
    def _load_model(self):
        try:
            self.summarizer = pipeline(
                "summarization",
                model=self.model_name,
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info(f"Summarization model loaded: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load summarization model: {e}")
            raise
    
    async def summarize_text(self, text: str, max_length: int = 150, min_length: int = 50) -> Dict[str, Any]:
        """Generate summary of input text"""
        try:
            # Split text into chunks if too long
            max_input_length = 1024
            if len(text) > max_input_length:
                chunks = [text[i:i+max_input_length] for i in range(0, len(text), max_input_length)]
                summaries = []
                
                for chunk in chunks:
                    summary = self.summarizer(
                        chunk,
                        max_length=max_length,
                        min_length=min_length,
                        do_sample=False
                    )
                    summaries.append(summary[0]['summary_text'])
                
                # Combine and re-summarize if needed
                combined_summary = " ".join(summaries)
                if len(combined_summary) > max_input_length:
                    final_summary = self.summarizer(
                        combined_summary,
                        max_length=max_length,
                        min_length=min_length,
                        do_sample=False
                    )
                    summary_text = final_summary[0]['summary_text']
                else:
                    summary_text = combined_summary
            else:
                summary = self.summarizer(
                    text,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False
                )
                summary_text = summary[0]['summary_text']
            
            return {
                "original_text": text,
                "summary_text": summary_text,
                "summary_type": "abstractive"
            }
            
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            raise

class SentimentAnalysisService:
    def __init__(self):
        self.model_name = settings.SENTIMENT_MODEL
        self.sentiment_analyzer = None
        self._load_model()
    
    def _load_model(self):
        try:
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info(f"Sentiment analysis model loaded: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load sentiment analysis model: {e}")
            raise
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of input text"""
        try:
            # Split text into segments if too long
            max_length = 512
            segments = [text[i:i+max_length] for i in range(0, len(text), max_length)]
            
            results = []
            for i, segment in enumerate(segments):
                if segment.strip():  # Skip empty segments
                    sentiment_result = self.sentiment_analyzer(segment)
                    results.append({
                        "segment": segment,
                        "sentiment": sentiment_result[0]['label'].lower(),
                        "confidence_score": sentiment_result[0]['score'],
                        "segment_index": i
                    })
            
            # Calculate overall sentiment
            if results:
                avg_confidence = sum(r['confidence_score'] for r in results) / len(results)
                sentiment_counts = {}
                for result in results:
                    sentiment = result['sentiment']
                    sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
                
                overall_sentiment = max(sentiment_counts, key=sentiment_counts.get)
            else:
                overall_sentiment = "neutral"
                avg_confidence = 0.0
            
            return {
                "text": text,
                "overall_sentiment": overall_sentiment,
                "overall_confidence": avg_confidence,
                "segments": results
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            raise