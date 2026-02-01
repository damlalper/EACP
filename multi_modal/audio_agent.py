"""
Audio Agent for EACP
Handles audio/video processing, meeting summaries, and command extraction
"""

from typing import Dict, List, Any, Optional
import logging
import os

logger = logging.getLogger(__name__)

# Optional imports for real ASR
try:
    import whisper
except ImportError:
    whisper = None

try:
    from pydub import AudioSegment
except ImportError:
    AudioSegment = None


class AudioAgent:
    """Agent for audio and video processing using OpenAI Whisper."""
    
    def __init__(self, llm_client=None, whisper_model: str = "base"):
        self.llm_client = llm_client
        self.asr_engine = None
        self.whisper_model = whisper_model
        self._initialize_asr()
    
    def _initialize_asr(self):
        """Initialize Automatic Speech Recognition engine (OpenAI Whisper if available, else mock)."""
        try:
            if whisper:
                self.asr_engine = whisper.load_model(self.whisper_model)
                logger.info(f"Whisper ASR engine initialized with model: {self.whisper_model}")
            else:
                logger.warning("whisper not installed; falling back to mock ASR")
                self.asr_engine = "mock"
        except Exception as e:
            logger.error(f"Failed to initialize Whisper: {str(e)}; falling back to mock")
            self.asr_engine = "mock"
    
    def process_audio(self, audio_path: str, task: str = "transcribe") -> Dict[str, Any]:
        """
        Process audio file
        Tasks: transcribe, summarize, extract_commands, sentiment_analysis
        """
        try:
            if task == "summarize":
                return self._summarize_audio(audio_path)
            elif task == "extract_commands":
                return self._extract_commands(audio_path)
            elif task == "sentiment_analysis":
                return self._analyze_sentiment(audio_path)
            else:
                return self._transcribe_audio(audio_path)
        except Exception as e:
            logger.error(f"Audio processing error: {str(e)}")
            return {"error": str(e)}
    
    def process_video(self, video_path: str, extract_audio: bool = True) -> Dict[str, Any]:
        """Process video file"""
        try:
            # Extract audio if needed
            audio_transcript = None
            if extract_audio:
                audio_transcript = self._transcribe_audio(video_path)
            
            # Generate summary
            summary = None
            if audio_transcript and self.llm_client:
                summary = self._generate_meeting_summary(audio_transcript.get("transcript", ""))
            
            return {
                "video_path": video_path,
                "transcript": audio_transcript,
                "summary": summary,
                "duration": 0  # Would extract from video metadata
            }
        except Exception as e:
            logger.error(f"Video processing error: {str(e)}")
            return {"error": str(e)}
    
    def _transcribe_audio(self, audio_path: str) -> Dict[str, Any]:
        """Transcribe audio to text using Whisper or fallback to mock."""
        if not os.path.exists(audio_path):
            return {"error": f"Audio file not found: {audio_path}"}
        
        if whisper and isinstance(self.asr_engine, whisper.Whisper):
            try:
                result = self.asr_engine.transcribe(audio_path)
                return {
                    "audio_path": audio_path,
                    "transcript": result.get("text", ""),
                    "confidence": result.get("confidence", 0.0),
                    "language": result.get("language", "en"),
                    "segments": len(result.get("segments", []))
                }
            except Exception as e:
                logger.error(f"Whisper transcription failed: {str(e)}")
                return {"error": str(e)}
        
        # Mock fallback
        return {
            "audio_path": audio_path,
            "transcript": "[Mock audio transcription]",
            "confidence": 0.85,
            "language": "en"
        }
    
    def _summarize_audio(self, audio_path: str) -> Dict[str, Any]:
        """Summarize audio content"""
        transcript = self._transcribe_audio(audio_path)
        
        if self.llm_client:
            summary = self._generate_meeting_summary(transcript.get("transcript", ""))
            return {
                "audio_path": audio_path,
                "transcript": transcript,
                "summary": summary
            }
        
        return {
            "audio_path": audio_path,
            "transcript": transcript,
            "summary": "[Mock audio summary]"
        }
    
    def _extract_commands(self, audio_path: str) -> Dict[str, Any]:
        """Extract actionable commands from audio"""
        transcript = self._transcribe_audio(audio_path)
        
        if self.llm_client:
            prompt = f"""
            Extract actionable commands and tasks from the following transcript:
            
            {transcript.get("transcript", "")}
            
            Return a list of commands in JSON format.
            """
            commands = self.llm_client.generate(prompt=prompt)
            return {
                "audio_path": audio_path,
                "commands": commands
            }
        
        return {
            "audio_path": audio_path,
            "commands": []
        }
    
    def _analyze_sentiment(self, audio_path: str) -> Dict[str, Any]:
        """Analyze sentiment of audio content"""
        transcript = self._transcribe_audio(audio_path)
        
        if self.llm_client:
            prompt = f"""
            Analyze the sentiment of the following transcript:
            
            {transcript.get("transcript", "")}
            
            Provide sentiment analysis (positive, negative, neutral) and key emotions.
            """
            sentiment = self.llm_client.generate(prompt=prompt)
            return {
                "audio_path": audio_path,
                "sentiment": sentiment
            }
        
        return {
            "audio_path": audio_path,
            "sentiment": {"overall": "neutral", "confidence": 0.5}
        }
    
    def _generate_meeting_summary(self, transcript: str) -> Dict[str, Any]:
        """Generate meeting summary from transcript"""
        if not self.llm_client:
            return {"summary": "[Mock meeting summary]"}
        
        prompt = f"""
        Generate a comprehensive meeting summary from the following transcript:
        
        {transcript}
        
        Include:
        1. Key discussion points
        2. Decisions made
        3. Action items
        4. Next steps
        """
        
        summary = self.llm_client.generate(prompt=prompt)
        return {
            "summary": summary,
            "transcript_length": len(transcript)
        }
