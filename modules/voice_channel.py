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
from discord.sinks import WaveSink

from .tts_manager import TTSManager, get_tts_manager
from .stt_manager import STTManager, get_stt_manager

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

    def add(
        self, text: str, voice: Optional[str] = None, priority: bool = False
    ) -> None:
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

    def __init__(
        self,
        tts_manager: Optional[TTSManager] = None,
        stt_manager: Optional[STTManager] = None,
    ):
        """
        Initialize the Voice Channel Manager.

        Args:
            tts_manager: TTSManager instance (creates one if None)
            stt_manager: STTManager instance (creates one if None)
        """
        self.tts_manager = tts_manager or get_tts_manager()
        self.stt_manager = stt_manager or get_stt_manager()
        self.voice_clients: dict[int, discord.VoiceClient] = {}
        self.queues: dict[int, VoiceQueue] = {}
        self.listening_tasks: dict[
            int, asyncio.Task
        ] = {}  # Track listening tasks per guild
        self.max_queue_size = 50
        logger.info("VoiceChannelManager initialized with TTS and STT")

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
        Connect to a voice channel with retry logic for 4006 errors.

        Args:
            channel: Voice channel to connect to

        Returns:
            VoiceClient for the connected channel

        Raises:
            discord.DiscordException: If connection fails after retries
        """
        guild_id = channel.guild.id

        # Check if already connected to the same channel
        if guild_id in self.voice_clients:
            existing_vc = self.voice_clients[guild_id]
            if existing_vc.is_connected() and existing_vc.channel.id == channel.id:
                logger.info(f"Already connected to {channel.name}, returning existing connection")
                return existing_vc
            else:
                # Disconnect from different channel or invalid connection
                logger.info(f"Disconnecting from existing voice connection before connecting to {channel.name}")
                await self.disconnect_from_voice(channel.guild)

        # Retry logic for 4006 errors
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(
                    f"Connecting to voice channel: {channel.name} ({guild_id}) - Attempt {attempt + 1}"
                )

                # Add a small delay between attempts
                if attempt > 0:
                    await asyncio.sleep(2)

                vc = await channel.connect(timeout=30.0, reconnect=True)
                self.voice_clients[guild_id] = vc
                logger.info(f"Successfully connected to {channel.name}")
                return vc

            except discord.errors.ConnectionClosed as e:
                if e.code == 4006:
                    logger.warning(
                        f"Voice connection failed with 4006 (attempt {attempt + 1}/{max_retries})"
                    )
                    if attempt < max_retries - 1:
                        continue
                    else:
                        logger.error(
                            "All voice connection attempts failed with 4006 error"
                        )
                        raise discord.DiscordException(
                            "Voice connection failed: Session no longer valid (4006)"
                        )
                else:
                    logger.error(
                        f"Voice connection failed with code {e.code}: {str(e)}"
                    )
                    raise
            except discord.DiscordException as e:
                logger.error(f"Failed to connect to voice channel: {str(e)}")
                if attempt < max_retries - 1:
                    continue
                else:
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
                
                # Stop any ongoing listening sessions
                if guild_id in self.listening_tasks:
                    await self.stop_listening(guild_id)
                
                # Stop any current playback
                if vc.is_playing():
                    vc.stop()
                
                # Clear queue for this guild
                if guild_id in self.queues:
                    self.queues[guild_id].clear()
                    # Cancel any ongoing queue processing
                    queue = self.queues[guild_id]
                    if hasattr(queue, 'current_task') and queue.current_task:
                        queue.current_task.cancel()
                
                # Disconnect from voice
                await vc.disconnect()
                
                # Clean up references
                del self.voice_clients[guild_id]
                if guild_id in self.queues:
                    del self.queues[guild_id]
                
                logger.info(f"Disconnected from {guild.name}")
            except Exception as e:
                logger.error(f"Error disconnecting: {str(e)}")
                # Force cleanup even if disconnect failed
                self.voice_clients.pop(guild_id, None)
                self.queues.pop(guild_id, None)
                self.listening_tasks.pop(guild_id, None)

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
            audio_source = discord.FFmpegPCMAudio(io.BytesIO(audio_data), pipe=True)
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
            audio_bytes = self.tts_manager.generate_audio(
                text, voice=voice, return_bytes=True
            )
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

    async def start_listening(
        self, guild_id: int, callback: Callable[[str], None] = None
    ) -> bool:
        """
        Start listening for voice input in a guild.

        Args:
            guild_id: Guild ID to listen in
            callback: Optional callback function for transcribed text

        Returns:
            bool: True if listening started successfully
        """
        if guild_id not in self.voice_clients:
            logger.warning(f"No voice connection for guild {guild_id}")
            return False

        if guild_id in self.listening_tasks:
            logger.info(f"Already listening in guild {guild_id}")
            return True

        try:
            vc = self.voice_clients[guild_id]

            # Create recording sink
            sink = VoiceRecordingSink(self.stt_manager, callback)

            # Start recording
            vc.start_recording(sink, self._recording_finished, guild_id)

            # Store the sink for cleanup
            self.listening_tasks[guild_id] = {"sink": sink, "callback": callback}

            logger.info(f"Started listening session in guild {guild_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to start listening: {e}")
            return False

    async def stop_listening(self, guild_id: int) -> bool:
        """
        Stop listening for voice input in a guild.

        Args:
            guild_id: Guild ID to stop listening in

        Returns:
            bool: True if listening stopped successfully
        """
        if guild_id not in self.listening_tasks:
            logger.info(f"Not listening in guild {guild_id}")
            return False

        try:
            vc = self.voice_clients.get(guild_id)
            if vc:
                vc.stop_recording()

            # Clean up the sink
            session = self.listening_tasks[guild_id]
            sink = session["sink"]
            sink.cleanup()
            del self.listening_tasks[guild_id]

            logger.info(f"Stopped listening in guild {guild_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to stop listening: {e}")
            return False

    def is_listening(self, guild_id: int) -> bool:
        """Check if currently listening in a guild."""
        return guild_id in self.listening_tasks

    def _recording_finished(self, sink, guild_id: int) -> None:
        """
        Callback when recording finishes.

        Args:
            sink: The recording sink
            guild_id: Guild ID
        """
        logger.info(f"Recording finished for guild {guild_id}")

        # Process any remaining audio
        asyncio.create_task(sink.process_remaining_audio())

    async def cleanup_all_connections(self) -> None:
        """
        Clean up all voice connections and resources.
        Should be called during bot shutdown.
        """
        logger.info("Starting cleanup of all voice connections")
        
        # Stop all listening sessions
        for guild_id in list(self.listening_tasks.keys()):
            try:
                await self.stop_listening(guild_id)
            except Exception as e:
                logger.warning(f"Error stopping listening in guild {guild_id}: {e}")
        
        # Disconnect from all voice channels
        for guild_id, vc in list(self.voice_clients.items()):
            try:
                # Stop playback
                if vc.is_playing():
                    vc.stop()
                
                # Disconnect
                await vc.disconnect()
                logger.info(f"Cleaned up voice connection for guild {guild_id}")
            except Exception as e:
                logger.warning(f"Error cleaning up voice connection for guild {guild_id}: {e}")
        
        # Clear all data structures
        self.voice_clients.clear()
        self.queues.clear()
        self.listening_tasks.clear()
        
        logger.info("Voice connection cleanup completed")


class VoiceRecordingSink(WaveSink):
    """
    Voice recording sink that transcribes audio using STT.
    Extends discord.sinks.WaveSink for proper voice recording.
    """

    def __init__(
        self,
        stt_manager: STTManager,
        callback: Optional[Callable[[str, discord.User], None]] = None,
    ):
        """
        Initialize the voice recording sink.

        Args:
            stt_manager: STT manager for transcription
            callback: Optional callback for transcribed text and user
        """
        super().__init__()
        self.stt_manager = stt_manager
        self.callback = callback
        self.processing_tasks = set()  # Track processing tasks
        logger.info("VoiceRecordingSink initialized with discord.sinks")

    def write(self, data, user):
        """
        Process incoming voice data from discord.sinks.

        Args:
            data: Audio data
            user: Discord user who spoke
        """
        # Call parent write method to handle the audio data
        super().write(data, user)

        # Process audio for transcription every few seconds
        if len(self.audio_data.get(user, [])) % 100 == 0:  # Every ~2 seconds
            task = asyncio.create_task(self._process_user_audio(user))
            self.processing_tasks.add(task)
            task.add_done_callback(self.processing_tasks.discard)

    async def _process_user_audio(self, user: discord.User):
        """
        Process accumulated audio data for a user.

        Args:
            user: Discord user
        """
        try:
            # Get audio data for this user
            if user not in self.audio_data or not self.audio_data[user]:
                return

            # Get recent audio chunks (last 2 seconds worth)
            recent_chunks = self.audio_data[user][-100:]  # Approximate 2 seconds

            if len(recent_chunks) < 10:  # Skip very short clips
                return

            # Convert audio chunks to bytes
            audio_bytes = b"".join(chunk for chunk in recent_chunks if chunk)

            if len(audio_bytes) < 1000:  # Skip very short audio
                return

            # Transcribe the audio
            text = await self.stt_manager.transcribe_audio(audio_bytes)

            if text and text.strip():
                logger.info(f"Transcribed from {user.display_name}: {text}")

                # Call the callback if provided
                if self.callback:
                    if asyncio.iscoroutinefunction(self.callback):
                        await self.callback(text, user)
                    else:
                        self.callback(text, user)

        except Exception as e:
            logger.error(f"Error processing audio for user {user.display_name}: {e}")

    async def process_remaining_audio(self):
        """Process any remaining audio data when recording stops."""
        try:
            for user in self.audio_data:
                if self.audio_data[user]:
                    await self._process_user_audio(user)
        except Exception as e:
            logger.error(f"Error processing remaining audio: {e}")

    def cleanup(self):
        """Clean up audio buffers and tasks."""
        # Cancel any pending processing tasks
        for task in self.processing_tasks:
            if not task.done():
                task.cancel()
        self.processing_tasks.clear()

        # Clear audio data
        if hasattr(self, "audio_data"):
            self.audio_data.clear()

        logger.info("VoiceRecordingSink cleaned up")


# Module-level singleton instance
_voice_manager_instance: Optional[VoiceChannelManager] = None


def get_voice_manager(
    tts_manager: Optional[TTSManager] = None,
    stt_manager: Optional[STTManager] = None,
    reinitialize: bool = False,
) -> VoiceChannelManager:
    """
    Get or create the global VoiceChannelManager instance.

    Args:
        tts_manager: TTSManager to use (creates default if None)
        stt_manager: STTManager to use (creates default if None)
        reinitialize: Force creation of new instance

    Returns:
        VoiceChannelManager instance
    """
    global _voice_manager_instance

    if _voice_manager_instance is None or reinitialize:
        _voice_manager_instance = VoiceChannelManager(
            tts_manager=tts_manager, stt_manager=stt_manager
        )

    return _voice_manager_instance
