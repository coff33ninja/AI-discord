"""
AI Voice Integration Module
Integrates Gemini AI responses with KittenTTS voice synthesis for Discord voice channels
Automatically converts text responses to speech and plays them
"""

import asyncio
import logging
from typing import Optional
from modules.tts_manager import get_tts_manager, TTSManager
from modules.voice_channel import get_voice_manager, VoiceChannelManager

logger = logging.getLogger(__name__)


class AIVoiceIntegration:
    """
    Bridges AI responses (from Gemini) with voice synthesis (KittenTTS).
    Automatically converts AI text responses to speech and plays them in Discord voice channels.
    """

    def __init__(
        self,
        tts_manager: Optional[TTSManager] = None,
        voice_manager: Optional[VoiceChannelManager] = None,
        default_voice: str = 'expr-voice-2-f',
        auto_speak: bool = True,
    ):
        """
        Initialize the AI Voice Integration.

        Args:
            tts_manager: TTSManager instance (creates one if None)
            voice_manager: VoiceChannelManager instance (creates one if None)
            default_voice: Default voice for AI responses
            auto_speak: If True, automatically speak all AI responses in connected voice channels
        """
        self.tts_manager = tts_manager or get_tts_manager(voice=default_voice)
        self.voice_manager = voice_manager or get_voice_manager(tts_manager=self.tts_manager)
        self.default_voice = default_voice
        self.auto_speak = auto_speak
        self.guild_voices = {}  # Track voice preferences per guild

        logger.info(
            f"AIVoiceIntegration initialized with voice: {default_voice}, "
            f"auto_speak: {auto_speak}"
        )

    async def speak_response(
        self,
        guild_id: int,
        text: str,
        voice: Optional[str] = None,
        queue: bool = False,
    ) -> bool:
        """
        Convert AI response to speech and play it in voice channel.

        Args:
            guild_id: Guild ID to play audio in
            text: AI response text to synthesize
            voice: Optional voice override
            queue: If True, queue the message; if False, play immediately

        Returns:
            bool: True if successful, False otherwise
        """
        if not text or not isinstance(text, str):
            logger.warning("speak_response called with invalid text")
            return False

        # Check if bot is connected to voice
        if not self.voice_manager.is_connected(guild_id):
            logger.debug(f"Not connected to voice in guild {guild_id}")
            return False

        try:
            selected_voice = voice or self.guild_voices.get(guild_id, self.default_voice)

            if queue:
                # Add to queue for later playback
                self.voice_manager.queue_text(guild_id, text, voice=selected_voice)
                logger.info(f"Queued AI response in guild {guild_id}")
                return True
            else:
                # Play immediately
                success = await self.voice_manager.play_text(guild_id, text, voice=selected_voice)
                if success:
                    logger.info(f"Playing AI response in guild {guild_id} with voice {selected_voice}")
                return success

        except Exception as e:
            logger.error(f"Error in speak_response: {str(e)}")
            return False

    async def speak_ai_response(
        self,
        guild_id: int,
        ai_response: str,
        voice: Optional[str] = None,
        queue: bool = False,
    ) -> bool:
        """
        Convenience method to speak an AI response.
        Automatically handles text length and formatting.

        Args:
            guild_id: Guild ID to play audio in
            ai_response: Full AI response text
            voice: Optional voice override
            queue: If True, queue for later playback

        Returns:
            bool: True if successful
        """
        if not self.auto_speak:
            logger.debug("Auto-speak disabled, skipping voice synthesis")
            return False

        # Clean up the text
        text = ai_response.strip()

        # Split very long responses (> 500 chars) into sentences
        if len(text) > 500:
            # Simple sentence splitting
            sentences = [s.strip() for s in text.replace("!", ".").replace("?", ".").split(".")]
            sentences = [s for s in sentences if s]  # Remove empty strings

            logger.info(f"Long response ({len(text)} chars) split into {len(sentences)} sentences")

            # Play/queue all sentences
            for i, sentence in enumerate(sentences):
                if not sentence:
                    continue

                # Queue all except maybe the first
                should_queue = queue or i > 0
                success = await self.speak_response(guild_id, sentence, voice=voice, queue=should_queue)

                if not success and i == 0:
                    logger.warning("Failed to speak first sentence")
                    return False

                # Small delay between sentences
                if i < len(sentences) - 1:
                    await asyncio.sleep(0.2)

            return True
        else:
            # Speak single response
            return await self.speak_response(guild_id, text, voice=voice, queue=queue)

    async def process_voice_queue(self, guild_id: int) -> None:
        """
        Process and play all queued AI responses.

        Args:
            guild_id: Guild ID to process queue for
        """
        if not self.voice_manager.is_connected(guild_id):
            logger.warning(f"Not connected to voice in guild {guild_id}, cannot process queue")
            return

        try:
            await self.voice_manager.process_queue(guild_id)
        except Exception as e:
            logger.error(f"Error processing voice queue: {str(e)}")

    def set_guild_voice(self, guild_id: int, voice: str) -> bool:
        """
        Set the voice for a specific guild.

        Args:
            guild_id: Guild ID
            voice: Voice identifier

        Returns:
            bool: True if voice is valid
        """
        if not self.tts_manager.is_voice_available(voice):
            logger.warning(f"Invalid voice: {voice}")
            return False

        self.guild_voices[guild_id] = voice
        self.tts_manager.set_voice(voice)
        logger.info(f"Guild {guild_id} voice set to: {voice}")
        return True

    def get_guild_voice(self, guild_id: int) -> str:
        """Get the voice for a guild."""
        return self.guild_voices.get(guild_id, self.default_voice)

    async def connect_guild_to_voice(
        self,
        guild_id: int,
        channel,
    ) -> bool:
        """
        Connect guild to voice channel.

        Args:
            guild_id: Guild ID
            channel: Discord voice channel to connect to

        Returns:
            bool: True if successful
        """
        try:
            await self.voice_manager.connect_to_voice(channel)
            logger.info(f"Connected guild {guild_id} to voice channel")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to voice: {str(e)}")
            return False

    async def disconnect_guild_from_voice(self, guild_id: int, guild) -> bool:
        """
        Disconnect guild from voice channel.

        Args:
            guild_id: Guild ID
            guild: Discord guild object

        Returns:
            bool: True if successful
        """
        try:
            await self.voice_manager.disconnect_from_voice(guild)
            # Clean up stored voice preference
            self.guild_voices.pop(guild_id, None)
            logger.info(f"Disconnected guild {guild_id} from voice")
            return True
        except Exception as e:
            logger.error(f"Failed to disconnect from voice: {str(e)}")
            return False

    def is_connected_to_voice(self, guild_id: int) -> bool:
        """Check if guild is connected to voice."""
        return self.voice_manager.is_connected(guild_id)

    def get_queue_size(self, guild_id: int) -> int:
        """Get current queue size for guild."""
        return self.voice_manager.get_queue_size(guild_id)

    def enable_auto_speak(self) -> None:
        """Enable automatic speech synthesis."""
        self.auto_speak = True
        logger.info("Auto-speak enabled")

    def disable_auto_speak(self) -> None:
        """Disable automatic speech synthesis."""
        self.auto_speak = False
        logger.info("Auto-speak disabled")

    def toggle_auto_speak(self) -> bool:
        """Toggle auto-speak and return new state."""
        self.auto_speak = not self.auto_speak
        logger.info(f"Auto-speak toggled to: {self.auto_speak}")
        return self.auto_speak


# Module-level singleton instance
_ai_voice_instance: Optional[AIVoiceIntegration] = None


def get_ai_voice_integration(
    tts_manager: Optional[TTSManager] = None,
    voice_manager: Optional[VoiceChannelManager] = None,
    default_voice: str = 'expr-voice-2-f',
    auto_speak: bool = True,
    reinitialize: bool = False,
) -> AIVoiceIntegration:
    """
    Get or create the global AIVoiceIntegration instance.

    Args:
        tts_manager: TTSManager instance
        voice_manager: VoiceChannelManager instance
        default_voice: Default voice for AI
        auto_speak: Enable auto-speak
        reinitialize: Force creation of new instance

    Returns:
        AIVoiceIntegration instance
    """
    global _ai_voice_instance

    if _ai_voice_instance is None or reinitialize:
        _ai_voice_instance = AIVoiceIntegration(
            tts_manager=tts_manager,
            voice_manager=voice_manager,
            default_voice=default_voice,
            auto_speak=auto_speak,
        )

    return _ai_voice_instance
