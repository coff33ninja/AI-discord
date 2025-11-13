"""
KittenTTS Manager Module
Handles text-to-speech synthesis using the KittenTTS model.
Provides text generation, audio processing, and voice selection utilities.
"""

import io
import numpy as np
from typing import Optional
from pathlib import Path
import logging

try:
    from kittentts import KittenTTS
    HAS_KITTENTTS = True
except ImportError:
    HAS_KITTENTTS = False

try:
    import soundfile as sf
    HAS_SOUNDFILE = True
except ImportError:
    HAS_SOUNDFILE = False

logger = logging.getLogger(__name__)

# Available voice options in KittenTTS
AVAILABLE_VOICES = [
    'expr-voice-2-m',
    'expr-voice-2-f',
    'expr-voice-3-m',
    'expr-voice-3-f',
    'expr-voice-4-m',
    'expr-voice-4-f',
    'expr-voice-5-m',
    'expr-voice-5-f',
]

DEFAULT_VOICE = 'expr-voice-2-f'
DEFAULT_MODEL = "KittenML/kitten-tts-nano-0.2"
SAMPLE_RATE = 24000


class TTSManager:
    """
    Manages text-to-speech operations using KittenTTS.
    
    Attributes:
        model: The KittenTTS model instance
        current_voice: Currently selected voice
        model_name: Name of the TTS model being used
    """

    def __init__(self, model_name: str = DEFAULT_MODEL, voice: str = DEFAULT_VOICE):
        """
        Initialize the TTS Manager.
        
        Args:
            model_name: HuggingFace model identifier for KittenTTS
            voice: Default voice to use for synthesis
            
        Raises:
            ImportError: If KittenTTS or soundfile are not installed
            ValueError: If selected voice is not available
        """
        if not HAS_KITTENTTS:
            raise ImportError(
                "KittenTTS is not installed. "
                "Install it using: pip install https://github.com/KittenML/KittenTTS/releases/download/0.1/kittentts-0.1.0-py3-none-any.whl"
            )
        
        if not HAS_SOUNDFILE:
            raise ImportError(
                "soundfile is not installed. "
                "Install it using: pip install soundfile"
            )
        
        if voice not in AVAILABLE_VOICES:
            raise ValueError(
                f"Voice '{voice}' not available. "
                f"Choose from: {', '.join(AVAILABLE_VOICES)}"
            )
        
        logger.info(f"Initializing KittenTTS with model: {model_name}")
        self.model = KittenTTS(model_name)
        self.current_voice = voice
        self.model_name = model_name
        logger.info(f"KittenTTS initialized successfully with voice: {voice}")

    def set_voice(self, voice: str) -> None:
        """
        Change the current voice.
        
        Args:
            voice: Voice identifier to use
            
        Raises:
            ValueError: If voice is not available
        """
        if voice not in AVAILABLE_VOICES:
            raise ValueError(
                f"Voice '{voice}' not available. "
                f"Choose from: {', '.join(AVAILABLE_VOICES)}"
            )
        self.current_voice = voice
        logger.info(f"Voice changed to: {voice}")

    def generate_audio(
        self,
        text: str,
        voice: Optional[str] = None,
        return_bytes: bool = False,
    ) -> tuple[np.ndarray, int] | bytes:
        """
        Generate audio from text.
        
        Args:
            text: Text to synthesize
            voice: Optional voice override (uses current_voice if None)
            return_bytes: If True, returns WAV bytes; if False, returns (audio_array, sample_rate)
            
        Returns:
            If return_bytes=False: Tuple of (audio_array, sample_rate)
            If return_bytes=True: WAV file as bytes
            
        Raises:
            ValueError: If text is empty or voice is invalid
        """
        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string")
        
        # Truncate text if too long (API limitation)
        if len(text) > 1000:
            logger.warning(f"Text truncated from {len(text)} to 1000 characters")
            text = text[:1000]
        
        selected_voice = voice or self.current_voice
        
        if selected_voice not in AVAILABLE_VOICES:
            raise ValueError(
                f"Voice '{selected_voice}' not available. "
                f"Choose from: {', '.join(AVAILABLE_VOICES)}"
            )
        
        logger.info(f"Generating audio for text: {text[:50]}... with voice: {selected_voice}")
        
        try:
            audio_array = self.model.generate(text, voice=selected_voice)
            
            if return_bytes:
                # Convert to WAV bytes
                wav_buffer = io.BytesIO()
                sf.write(wav_buffer, audio_array, SAMPLE_RATE, format='WAV')
                wav_buffer.seek(0)
                return wav_buffer.getvalue()
            else:
                return audio_array, SAMPLE_RATE
                
        except Exception as e:
            logger.error(f"Error generating audio: {str(e)}")
            raise

    def save_audio(
        self,
        text: str,
        output_path: str,
        voice: Optional[str] = None,
        format: str = 'WAV',
    ) -> Path:
        """
        Generate and save audio to a file.
        
        Args:
            text: Text to synthesize
            output_path: Path to save the audio file
            voice: Optional voice override
            format: Audio format (WAV, FLAC, OGG, etc.)
            
        Returns:
            Path object of saved file
            
        Raises:
            ValueError: If text is empty or voice is invalid
        """
        audio_array, sample_rate = self.generate_audio(text, voice=voice, return_bytes=False)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Saving audio to: {output_path}")
        sf.write(str(output_path), audio_array, sample_rate, format=format)
        return output_path

    @staticmethod
    def get_available_voices() -> list[str]:
        """Get list of available voices."""
        return AVAILABLE_VOICES.copy()

    @staticmethod
    def is_voice_available(voice: str) -> bool:
        """Check if a voice is available."""
        return voice in AVAILABLE_VOICES


# Module-level singleton instance (lazy loaded)
_tts_instance: Optional[TTSManager] = None


def get_tts_manager(
    model_name: str = DEFAULT_MODEL,
    voice: str = DEFAULT_VOICE,
    reinitialize: bool = False,
) -> TTSManager:
    """
    Get or create the global TTSManager instance.
    
    Args:
        model_name: Model to use if creating new instance
        voice: Default voice if creating new instance
        reinitialize: Force creation of new instance
        
    Returns:
        TTSManager instance
    """
    global _tts_instance
    
    if _tts_instance is None or reinitialize:
        _tts_instance = TTSManager(model_name=model_name, voice=voice)
    
    return _tts_instance
