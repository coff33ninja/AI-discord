"""
Voice Interaction Module
Full voice conversation pipeline: STT → AI → TTS
Users can speak in voice channels and get AI responses with voice synthesis.
"""

import logging
from typing import Optional

from discord.ext import commands

from modules.stt_manager import get_stt_manager, STTManager
from modules.ai_voice_integration import get_ai_voice_integration, AIVoiceIntegration
from modules.api_manager import GeminiAPIManager

logger = logging.getLogger(__name__)


class VoiceConversation:
    """
    Manages a complete voice conversation in a Discord channel.
    Handles: recording → transcription → AI response → synthesis → playback
    """

    def __init__(
        self,
        guild_id: int,
        stt_manager: Optional[STTManager] = None,
        ai_voice_integration: Optional[AIVoiceIntegration] = None,
        api_manager: Optional[GeminiAPIManager] = None,
    ):
        """
        Initialize voice conversation.
        
        Args:
            guild_id: Guild/server ID
            stt_manager: STTManager instance
            ai_voice_integration: AIVoiceIntegration instance
            api_manager: GeminiAPIManager instance for AI responses
        """
        self.guild_id = guild_id
        self.stt_manager = stt_manager or get_stt_manager()
        self.ai_voice = ai_voice_integration or get_ai_voice_integration()
        self.api_manager = api_manager
        self.is_listening = False
        self.conversation_history = []
        logger.info(f"VoiceConversation initialized for guild {guild_id}")

    async def process_audio_and_respond(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
    ) -> dict:
        """
        Process audio: transcribe → generate AI response → synthesize voice.
        
        Args:
            audio_data: Raw audio bytes
            language: Optional language code
            
        Returns:
            Dict with 'transcription', 'response', 'status', and 'error' keys
        """
        result = {
            'transcription': None,
            'response': None,
            'status': 'processing',
            'error': None,
        }
        
        try:
            # Step 1: Transcribe audio
            logger.info("Step 1: Transcribing user audio...")
            transcription = await self.stt_manager.transcribe_audio(audio_data, language)
            
            if not transcription or transcription.strip() == '':
                result['status'] = 'no_speech'
                result['error'] = 'No speech detected in audio'
                logger.warning("No speech detected in audio")
                return result
            
            result['transcription'] = transcription
            logger.info(f"User said: {transcription}")
            
            # Add to history
            self.conversation_history.append({
                'role': 'user',
                'content': transcription
            })
            
            # Step 2: Generate AI response
            logger.info("Step 2: Generating AI response...")
            if not self.api_manager:
                result['status'] = 'error'
                result['error'] = 'API manager not configured'
                logger.error("API manager not configured for AI response")
                return result
            
            ai_response = await self.api_manager.generate_content(transcription)
            
            if not ai_response:
                result['status'] = 'error'
                result['error'] = 'Failed to generate AI response'
                logger.error("AI response generation failed")
                return result
            
            result['response'] = ai_response
            logger.info(f"AI response: {ai_response[:100]}...")
            
            # Add to history
            self.conversation_history.append({
                'role': 'assistant',
                'content': ai_response
            })
            
            # Step 3: Synthesize and play voice response
            logger.info("Step 3: Synthesizing and playing voice response...")
            if self.ai_voice.is_connected_to_voice(self.guild_id):
                success = await self.ai_voice.speak_ai_response(
                    self.guild_id,
                    ai_response
                )
                if success:
                    result['status'] = 'success'
                    logger.info("Voice response played successfully")
                else:
                    result['status'] = 'partial_success'
                    result['error'] = 'Response generated but voice playback failed'
                    logger.warning("Voice playback failed")
            else:
                result['status'] = 'partial_success'
                result['error'] = 'Not connected to voice channel'
                logger.warning("Not connected to voice channel for playback")
            
            return result
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            logger.error(f"Error in voice conversation: {e}")
            return result

    def get_conversation_history(self) -> list:
        """Get conversation history."""
        return self.conversation_history.copy()

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history.clear()
        logger.info(f"Conversation history cleared for guild {self.guild_id}")

    def get_history_length(self) -> int:
        """Get number of messages in history."""
        return len(self.conversation_history)


class VoiceInteractionCog(commands.Cog):
    """
    Discord commands for voice interaction with AI.
    Provides voice conversation functionality.
    """

    def __init__(self, bot: commands.Bot, api_manager: GeminiAPIManager):
        """
        Initialize the voice interaction cog.
        
        Args:
            bot: Discord bot instance
            api_manager: Gemini API manager
        """
        self.bot = bot
        self.api_manager = api_manager
        self.conversations = {}  # Store VoiceConversation per guild
        self.stt_manager = None
        self.ai_voice = None
        logger.info("VoiceInteractionCog initialized")

    async def cog_load(self):
        """Initialize managers when cog loads."""
        try:
            self.stt_manager = get_stt_manager()
            self.ai_voice = get_ai_voice_integration()
            logger.info("STT and AI Voice managers loaded")
        except Exception as e:
            logger.error(f"Failed to load STT manager: {e}")

    def _get_conversation(self, guild_id: int) -> VoiceConversation:
        """Get or create conversation for guild."""
        if guild_id not in self.conversations:
            self.conversations[guild_id] = VoiceConversation(
                guild_id,
                stt_manager=self.stt_manager,
                ai_voice_integration=self.ai_voice,
                api_manager=self.api_manager,
            )
        return self.conversations[guild_id]

    @commands.command(name='listen')
    async def start_listening(self, ctx: commands.Context):
        """
        Start listening to voice channel for speech.
        
        Note: This requires the bot to be in a voice channel first.
        Requires: !join_voice first
        """
        if not self.ai_voice or not self.stt_manager:
            await ctx.send("❌ Voice system not initialized")
            return

        guild_id = ctx.guild.id

        if not self.ai_voice.is_connected_to_voice(guild_id):
            await ctx.send("❌ Bot must be in a voice channel first! Use !join_voice")
            return

        conversation = self._get_conversation(guild_id)
        
        if conversation.is_listening:
            await ctx.send("✅ Already listening...")
            return

        conversation.is_listening = True
        await ctx.send(
            "🎤 **Listening to voice channel...**\n"
            "Speak clearly for best results!\n"
            "Use `!stop_listening` to stop."
        )
        logger.info(f"Started listening in guild {guild_id}")

    @commands.command(name='stop_listening')
    async def stop_listening(self, ctx: commands.Context):
        """Stop listening to voice channel."""
        guild_id = ctx.guild.id
        
        if guild_id in self.conversations:
            self.conversations[guild_id].is_listening = False
            await ctx.send("🔇 Stopped listening")
            logger.info(f"Stopped listening in guild {guild_id}")
        else:
            await ctx.send("❌ Not currently listening")

    @commands.command(name='voice_history')
    async def show_voice_history(self, ctx: commands.Context):
        """Show recent voice conversation history."""
        guild_id = ctx.guild.id
        conversation = self._get_conversation(guild_id)
        history = conversation.get_conversation_history()

        if not history:
            await ctx.send("📝 No conversation history yet")
            return

        # Format history for display
        message = "📝 **Voice Conversation History:**\n\n"
        for i, msg in enumerate(history[-6:], 1):  # Show last 6 messages
            role = "👤 You" if msg['role'] == 'user' else "🤖 AI"
            content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
            message += f"{i}. {role}: {content}\n"

        if len(history) > 6:
            message += f"\n_(Total: {len(history)} messages)_"

        await ctx.send(message)

    @commands.command(name='clear_voice_history')
    async def clear_voice_history(self, ctx: commands.Context):
        """Clear voice conversation history."""
        guild_id = ctx.guild.id
        conversation = self._get_conversation(guild_id)
        conversation.clear_history()
        await ctx.send("🗑️ Conversation history cleared")
        logger.info(f"Cleared conversation history for guild {guild_id}")


async def setup(bot: commands.Bot, api_manager: GeminiAPIManager):
    """
    Setup the voice interaction cog.
    
    Usage in bot.py:
        from modules.voice_interaction import setup as setup_voice_interaction
        await setup_voice_interaction(bot, api_manager)
    """
    cog = VoiceInteractionCog(bot, api_manager)
    await bot.add_cog(cog)
    logger.info("VoiceInteractionCog added to bot")
