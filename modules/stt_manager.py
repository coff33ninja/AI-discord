"""
Speech-to-Text (STT) Module
Converts Discord voice audio to text using OpenAI Whisper.
Allows users to speak to the AI in voice channels.
"""

import io
import asyncio
import logging
from typing import Optional

try:
    import whisper
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False

logger = logging.getLogger(__name__)

# Whisper model options (from smallest to largest)
WHISPER_MODELS = {
    'tiny': 'Fast, lower quality (~40MB)',
    'base': 'Balanced (~140MB)',
    'small': 'Better quality (~465MB)',
    'medium': 'High quality (~1.5GB)',
    'large': 'Highest quality (~2.9GB)',
}

DEFAULT_MODEL = 'base'


class STTManager:
    """
    Manages speech-to-text conversion using OpenAI Whisper.
    
    Features:
    - Convert audio bytes to text
    - Support multiple Whisper model sizes
    - Language detection and specification
    - Async processing
    - Caching of loaded models
    """

    def __init__(self, model_name: str = DEFAULT_MODEL):
        """
        Initialize the STT Manager.
        
        Args:
            model_name: Whisper model to use ('tiny', 'base', 'small', 'medium', 'large')
            
        Raises:
            ImportError: If Whisper is not installed
            ValueError: If model_name is invalid
        """
        if not HAS_WHISPER:
            raise ImportError(
                "Whisper is not installed. "
                "Install it using: pip install openai-whisper"
            )
        
        if model_name not in WHISPER_MODELS:
            raise ValueError(
                f"Model '{model_name}' not available. "
                f"Choose from: {', '.join(WHISPER_MODELS.keys())}"
            )
        
        logger.info(f"Loading Whisper model: {model_name}")
        self.model = whisper.load_model(model_name)
        self.model_name = model_name
        logger.info(f"Whisper model '{model_name}' loaded successfully")

    async def transcribe_audio(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
    ) -> Optional[str]:
        """
        Transcribe audio bytes to text.
        
        Args:
            audio_data: Audio as bytes (WAV format expected)
            language: Optional language code (e.g., 'en', 'es', 'fr')
            
        Returns:
            Transcribed text or None if transcription failed
        """
        if not audio_data:
            logger.warning("transcribe_audio called with empty audio data")
            return None
        
        try:
            # Create a BytesIO object from the audio bytes
            audio_file = io.BytesIO(audio_data)
            
            # Run transcription in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            
            logger.info(f"Transcribing audio ({len(audio_data)} bytes)")
            
            result = await loop.run_in_executor(
                None,
                self._transcribe_sync,
                audio_file,
                language
            )
            
            if result:
                logger.info(f"Transcription successful: {result[:100]}...")
                return result
            else:
                logger.warning("Transcription returned empty result")
                return None
                
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return None

    def _transcribe_sync(self, audio_file, language: Optional[str]) -> Optional[str]:
        """
        Synchronous transcription (runs in executor).
        
        Args:
            audio_file: BytesIO object with audio data
            language: Optional language code
            
        Returns:
            Transcribed text
        """
        try:
            result = self.model.transcribe(
                audio_file,
                language=language,
                fp16=False  # Disable fp16 for CPU compatibility
            )
            return result.get('text', '').strip()
        except Exception as e:
            logger.error(f"Sync transcription error: {e}")
            return None

    @staticmethod
    def get_available_models() -> dict:
        """Get list of available Whisper models."""
        return WHISPER_MODELS.copy()

    @staticmethod
    def is_model_available(model_name: str) -> bool:
        """Check if a model is available."""
        return model_name in WHISPER_MODELS


# Module-level singleton instance
_stt_instance: Optional[STTManager] = None


def get_stt_manager(model_name: str = DEFAULT_MODEL, reinitialize: bool = False) -> STTManager:
    """
    Get or create the global STTManager instance.
    
    Args:
        model_name: Model to use if creating new instance
        reinitialize: Force creation of new instance
        
    Returns:
        STTManager instance
    """
    global _stt_instance
    
    if _stt_instance is None or reinitialize:
        _stt_instance = STTManager(model_name=model_name)
    
    return _stt_instance
