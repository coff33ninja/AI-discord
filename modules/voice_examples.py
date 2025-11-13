"""
KittenTTS Voice Integration Examples
Demonstrates how to use the TTS and Voice Channel modules
"""

from discord.ext import commands

from modules.tts_manager import get_tts_manager, AVAILABLE_VOICES
from modules.voice_channel import get_voice_manager


class VoiceCommands(commands.Cog):
    """Example Discord commands for voice and TTS functionality."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_manager = get_voice_manager()

    @commands.command(name="join")
    async def join_voice(self, ctx: commands.Context):
        """Join the voice channel of the command author."""
        if not ctx.author.voice:
            await ctx.send("❌ You must be in a voice channel!")
            return

        try:
            await self.voice_manager.connect_to_voice(ctx.author.voice.channel)
            await ctx.send(f"✅ Joined {ctx.author.voice.channel.name}")
        except Exception as e:
            await ctx.send(f"❌ Failed to join voice: {str(e)}")

    @commands.command(name="leave")
    async def leave_voice(self, ctx: commands.Context):
        """Leave the current voice channel."""
        try:
            await self.voice_manager.disconnect_from_voice(ctx.guild)
            await ctx.send("✅ Left voice channel")
        except Exception as e:
            await ctx.send(f"❌ Failed to leave: {str(e)}")

    @commands.command(name="say")
    async def say(self, ctx: commands.Context, *, text: str):
        """
        Generate and play TTS audio immediately.
        Usage: !say Hello, this is a test
        """
        if not self.voice_manager.is_connected(ctx.guild.id):
            await ctx.send("❌ Not connected to a voice channel! Use !join first")
            return

        if not text or len(text.strip()) == 0:
            await ctx.send("❌ Please provide text to speak")
            return

        async with ctx.typing():
            success = await self.voice_manager.play_text(ctx.guild.id, text)

        if success:
            await ctx.send(f"🔊 Speaking: *{text[:50]}...*")
        else:
            await ctx.send("❌ Failed to generate or play audio")

    @commands.command(name="queue")
    async def queue_text(self, ctx: commands.Context, *, text: str):
        """
        Queue text for TTS playback.
        Usage: !queue This will be spoken after current audio finishes
        """
        if not self.voice_manager.is_connected(ctx.guild.id):
            await ctx.send("❌ Not connected to a voice channel! Use !join first")
            return

        if not text or len(text.strip()) == 0:
            await ctx.send("❌ Please provide text to queue")
            return

        try:
            self.voice_manager.queue_text(ctx.guild.id, text)
            queue_size = self.voice_manager.get_queue_size(ctx.guild.id)
            await ctx.send(f"📝 Queued! Queue size: {queue_size}")

            # Start processing if not already running
            await self.voice_manager.process_queue(ctx.guild.id)
        except RuntimeError as e:
            await ctx.send(f"❌ {str(e)}")

    @commands.command(name="stop")
    async def stop_audio(self, ctx: commands.Context):
        """Stop current audio playback and clear queue."""
        self.voice_manager.stop_playback(ctx.guild.id)
        self.voice_manager.clear_queue(ctx.guild.id)
        await ctx.send("⏹️ Stopped playback and cleared queue")

    @commands.command(name="voice")
    async def change_voice(self, ctx: commands.Context, voice: str = None):
        """
        Change the TTS voice.
        Usage: !voice expr-voice-2-f
        Available voices: expr-voice-2-m, expr-voice-2-f, expr-voice-3-m, expr-voice-3-f, etc.
        """
        tts_manager = get_tts_manager()

        if voice is None:
            available = ", ".join(AVAILABLE_VOICES)
            current = tts_manager.current_voice
            await ctx.send(f"Current voice: `{current}`\n\nAvailable voices:\n`{available}`")
            return

        if not tts_manager.is_voice_available(voice):
            available = ", ".join(AVAILABLE_VOICES)
            await ctx.send(f"❌ Voice not found!\n\nAvailable voices:\n`{available}`")
            return

        tts_manager.set_voice(voice)
        await ctx.send(f"✅ Voice changed to: `{voice}`")

    @commands.command(name="queuesize")
    async def show_queue_size(self, ctx: commands.Context):
        """Show the current queue size."""
        size = self.voice_manager.get_queue_size(ctx.guild.id)
        await ctx.send(f"📊 Current queue size: {size}")


# Example usage in main bot file:
# async def setup(bot):
#     await bot.add_cog(VoiceCommands(bot))


# Example: Direct integration without commands
async def example_direct_usage():
    """
    Example of using the modules directly without Discord commands.
    """
    from modules.tts_manager import TTSManager

    # Initialize TTS manager
    tts_manager = TTSManager(voice='expr-voice-2-f')

    # Method 1: Generate and save audio
    audio_path = tts_manager.save_audio(
        "Hello, this is a test message",
        "output.wav",
        format='WAV'
    )
    print(f"Audio saved to: {audio_path}")

    # Method 2: Generate audio as bytes for direct playback
    audio_bytes = tts_manager.generate_audio(
        "Another test message",
        return_bytes=True
    )
    print(f"Generated {len(audio_bytes)} bytes of audio")

    # Method 3: Generate with different voice
    audio_array, sample_rate = tts_manager.generate_audio(
        "Speaking with a different voice",
        voice='expr-voice-3-m',
        return_bytes=False
    )
    print(f"Generated audio at {sample_rate}Hz")


if __name__ == "__main__":
    print("This module contains examples. Import the VoiceCommands cog in your bot!")
