"""
Discord Voice Channel Module
Handles voice channel connections, audio playback, and queue management.
Integrates with TTSManager for speech synthesis.
"""

import asyncio
import io
import logging
from typing import Optional, Callable
from collections import deque

import discord

from .tts_manager import TTSManager, get_tts_manager

logger = logging.getLogger(__name__)


class VoiceQueue:
    """
    Queue for managing text-to-speech audio playback.
    Handles queueing, prioritization, and sequential playback.
    """

    def __init__(self, max_queue_size: int = 50):
        """
        Initialize the voice queue.
        
        Args:
            max_queue_size: Maximum number of items in queue
        """
        self.queue = deque(maxlen=max_queue_size)
        self.is_playing = False
        self.current_task: Optional[asyncio.Task] = None

    def add(self, text: str, voice: Optional[str] = None, priority: bool = False) -> None:
        """
        Add text to the queue.
        
        Args:
            text: Text to synthesize and play
            voice: Optional voice override
            priority: If True, add to front of queue
            
        Raises:
            RuntimeError: If queue is full
        """
        item = {"text": text, "voice": voice}
        
        if len(self.queue) >= self.queue.maxlen:
            raise RuntimeError("Voice queue is full")
        
        if priority:
            # Create new deque with item at front
            new_queue = deque(self.queue)
            new_queue.appendleft(item)
            self.queue = new_queue
        else:
            self.queue.append(item)
        
        logger.debug(f"Added to queue (priority={priority}): {text[:30]}...")

    def get_next(self) -> Optional[dict]:
        """Get next item from queue."""
        if self.queue:
            return self.queue.popleft()
        return None

    def clear(self) -> None:
        """Clear the entire queue."""
        self.queue.clear()
        logger.info("Voice queue cleared")

    def size(self) -> int:
        """Get current queue size."""
        return len(self.queue)

    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self.queue) == 0


class VoiceChannelManager:
    """
    Manages voice channel connections and audio playback.
    Handles TTS synthesis and Discord audio output.
    """

    def __init__(self, tts_manager: Optional[TTSManager] = None):
        """
        Initialize the Voice Channel Manager.
        
        Args:
            tts_manager: TTSManager instance (creates one if None)
        """
        self.tts_manager = tts_manager or get_tts_manager()
        self.voice_clients: dict[int, discord.VoiceClient] = {}
        self.queues: dict[int, VoiceQueue] = {}
        self.max_queue_size = 50
        logger.info("VoiceChannelManager initialized")

    def _get_queue(self, guild_id: int) -> VoiceQueue:
        """Get or create queue for guild."""
        if guild_id not in self.queues:
            self.queues[guild_id] = VoiceQueue(max_queue_size=self.max_queue_size)
        return self.queues[guild_id]

    async def connect_to_voice(
        self,
        channel: discord.VoiceChannel,
    ) -> discord.VoiceClient:
        """
        Connect to a voice channel.
        
        Args:
            channel: Voice channel to connect to
            
        Returns:
            VoiceClient for the connected channel
            
        Raises:
            discord.DiscordException: If connection fails
        """
        guild_id = channel.guild.id
        
        # Disconnect existing connection if present
        if guild_id in self.voice_clients:
            await self.disconnect_from_voice(channel.guild)
        
        try:
            logger.info(f"Connecting to voice channel: {channel.name} ({guild_id})")
            vc = await channel.connect()
            self.voice_clients[guild_id] = vc
            logger.info(f"Successfully connected to {channel.name}")
            return vc
        except discord.DiscordException as e:
            logger.error(f"Failed to connect to voice channel: {str(e)}")
            raise

    async def disconnect_from_voice(self, guild: discord.Guild) -> None:
        """
        Disconnect from voice channel.
        
        Args:
            guild: Guild to disconnect from
        """
        guild_id = guild.id
        
        if guild_id in self.voice_clients:
            vc = self.voice_clients[guild_id]
            try:
                logger.info(f"Disconnecting from voice channel in {guild.name}")
                await vc.disconnect()
                del self.voice_clients[guild_id]
                # Clear queue for this guild
                if guild_id in self.queues:
                    self.queues[guild_id].clear()
                logger.info(f"Disconnected from {guild.name}")
            except Exception as e:
                logger.error(f"Error disconnecting: {str(e)}")

    def queue_text(
        self,
        guild_id: int,
        text: str,
        voice: Optional[str] = None,
        priority: bool = False,
    ) -> None:
        """
        Queue text for TTS playback.
        
        Args:
            guild_id: Guild ID for the queue
            text: Text to synthesize
            voice: Optional voice override
            priority: If True, prioritize in queue
            
        Raises:
            RuntimeError: If queue is full
        """
        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string")
        
        queue = self._get_queue(guild_id)
        queue.add(text, voice=voice, priority=priority)

    async def play_audio(
        self,
        guild_id: int,
        audio_data: bytes,
        after: Optional[Callable] = None,
    ) -> bool:
        """
        Play audio in a voice channel.
        
        Args:
            guild_id: Guild ID with active voice connection
            audio_data: Audio data as bytes (WAV format)
            after: Optional callback after playback
            
        Returns:
            True if playback started, False if no voice connection
        """
        if guild_id not in self.voice_clients:
            logger.warning(f"No voice connection for guild {guild_id}")
            return False
        
        vc = self.voice_clients[guild_id]
        
        if vc.is_playing():
            vc.stop()
        
        try:
            # Create AudioSource from bytes
            audio_source = discord.FFmpegPCMAudio(
                io.BytesIO(audio_data),
                pipe=True
            )
            vc.play(audio_source, after=after)
            logger.debug(f"Started playback in guild {guild_id}")
            return True
        except Exception as e:
            logger.error(f"Error playing audio: {str(e)}")
            return False

    async def play_text(
        self,
        guild_id: int,
        text: str,
        voice: Optional[str] = None,
    ) -> bool:
        """
        Generate TTS audio and play it immediately.
        
        Args:
            guild_id: Guild ID with active voice connection
            text: Text to synthesize and play
            voice: Optional voice override
            
        Returns:
            True if playback started, False otherwise
        """
        try:
            audio_bytes = self.tts_manager.generate_audio(text, voice=voice, return_bytes=True)
            return await self.play_audio(guild_id, audio_bytes)
        except Exception as e:
            logger.error(f"Error in play_text: {str(e)}")
            return False

    async def process_queue(self, guild_id: int) -> None:
        """
        Process and play all items in the voice queue.
        Runs continuously until queue is empty.
        
        Args:
            guild_id: Guild ID with queue to process
        """
        queue = self._get_queue(guild_id)
        
        if queue.is_playing:
            logger.debug(f"Queue already processing for guild {guild_id}")
            return
        
        queue.is_playing = True
        
        try:
            while not queue.is_empty():
                item = queue.get_next()
                if item:
                    logger.debug(f"Processing queue item: {item['text'][:30]}...")
                    await self.play_text(guild_id, item["text"], voice=item["voice"])
                    
                    # Wait for audio to finish playing
                    vc = self.voice_clients.get(guild_id)
                    if vc:
                        while vc.is_playing():
                            await asyncio.sleep(0.1)
                        # Small delay between items
                        await asyncio.sleep(0.5)
        except Exception as e:
            logger.error(f"Error processing queue: {str(e)}")
        finally:
            queue.is_playing = False
            logger.debug(f"Queue processing finished for guild {guild_id}")

    def stop_playback(self, guild_id: int) -> None:
        """
        Stop current audio playback.
        
        Args:
            guild_id: Guild ID to stop playback for
        """
        if guild_id in self.voice_clients:
            vc = self.voice_clients[guild_id]
            if vc.is_playing():
                vc.stop()
                logger.info(f"Stopped playback in guild {guild_id}")

    def get_voice_client(self, guild_id: int) -> Optional[discord.VoiceClient]:
        """Get voice client for guild."""
        return self.voice_clients.get(guild_id)

    def is_connected(self, guild_id: int) -> bool:
        """Check if connected to voice in guild."""
        vc = self.voice_clients.get(guild_id)
        return vc is not None and vc.is_connected()

    def get_queue_size(self, guild_id: int) -> int:
        """Get current queue size for guild."""
        return self._get_queue(guild_id).size()

    def clear_queue(self, guild_id: int) -> None:
        """Clear queue for guild."""
        self._get_queue(guild_id).clear()


# Module-level singleton instance
_voice_manager_instance: Optional[VoiceChannelManager] = None


def get_voice_manager(
    tts_manager: Optional[TTSManager] = None,
    reinitialize: bool = False,
) -> VoiceChannelManager:
    """
    Get or create the global VoiceChannelManager instance.
    
    Args:
        tts_manager: TTSManager to use (creates default if None)
        reinitialize: Force creation of new instance
        
    Returns:
        VoiceChannelManager instance
    """
    global _voice_manager_instance
    
    if _voice_manager_instance is None or reinitialize:
        _voice_manager_instance = VoiceChannelManager(tts_manager=tts_manager)
    
    return _voice_manager_instance
