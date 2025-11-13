# KittenTTS Voice Integration Guide

This document describes the KittenTTS voice synthesis modules for your Discord bot.

## Overview

Two new modules have been added to enable text-to-speech (TTS) and voice channel integration:

1. **`tts_manager.py`** - Core TTS functionality using KittenTTS
2. **`voice_channel.py`** - Discord voice channel management and audio playback

## Installation

### Step 1: Install KittenTTS Wheel

KittenTTS uses a wheel distribution instead of PyPI. Install it with:

```bash
pip install https://github.com/KittenML/KittenTTS/releases/download/0.1/kittentts-0.1.0-py3-none-any.whl
```

### Step 2: Install Audio Dependencies

```bash
pip install -r requirements.txt
```

This installs `soundfile` and `numpy` needed for audio processing.

### Step 3: FFmpeg Requirement

Discord.py requires FFmpeg for audio playback. Install it:

**Windows (using winget):**
```bash
winget install FFmpeg
```

**Windows (using chocolatey):**
```bash
choco install ffmpeg
```

**macOS (using brew):**
```bash
brew install ffmpeg
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get install ffmpeg
```

## Module Documentation

### TTSManager (`tts_manager.py`)

Handles text-to-speech synthesis using KittenTTS.

#### Initialization

```python
from modules.tts_manager import TTSManager, get_tts_manager

# Option 1: Direct instantiation
tts = TTSManager(model_name="KittenML/kitten-tts-nano-0.2", voice='expr-voice-2-f')

# Option 2: Using singleton (recommended)
tts = get_tts_manager()
```

#### Available Voices

- `expr-voice-2-m` - Female voice variant 2
- `expr-voice-2-f` - Male voice variant 2
- `expr-voice-3-m` - Female voice variant 3
- `expr-voice-3-f` - Male voice variant 3
- `expr-voice-4-m` - Female voice variant 4
- `expr-voice-4-f` - Male voice variant 4
- `expr-voice-5-m` - Female voice variant 5
- `expr-voice-5-f` - Male voice variant 5

#### Methods

**`generate_audio(text, voice=None, return_bytes=False)`**
- Generates audio from text
- Returns: `(audio_array, sample_rate)` or `bytes` (WAV format)
- Max text length: 1000 characters

```python
# Get numpy array
audio, sr = tts.generate_audio("Hello world")

# Get WAV bytes
audio_bytes = tts.generate_audio("Hello world", return_bytes=True)

# Use different voice
audio = tts.generate_audio("Hello", voice='expr-voice-3-m')
```

**`save_audio(text, output_path, voice=None, format='WAV')`**
- Generates and saves audio to file
- Returns: `Path` object of saved file

```python
path = tts.save_audio("Hello world", "output.wav")
```

**`set_voice(voice)`**
- Change current voice

```python
tts.set_voice('expr-voice-3-f')
```

**`get_available_voices()`** (static)
- Returns list of available voices

```python
voices = TTSManager.get_available_voices()
```

**`is_voice_available(voice)`** (static)
- Check if voice exists

```python
if TTSManager.is_voice_available('expr-voice-2-f'):
    tts.set_voice('expr-voice-2-f')
```

---

### VoiceChannelManager (`voice_channel.py`)

Manages Discord voice channel connections and queued audio playback.

#### Initialization

```python
from modules.voice_channel import VoiceChannelManager, get_voice_manager

# Option 1: Direct instantiation
voice_mgr = VoiceChannelManager()

# Option 2: Using singleton (recommended)
voice_mgr = get_voice_manager()
```

#### Methods

**`connect_to_voice(channel)`** (async)
- Connect to a voice channel
- Returns: `discord.VoiceClient`

```python
vc = await voice_manager.connect_to_voice(ctx.author.voice.channel)
```

**`disconnect_from_voice(guild)`** (async)
- Disconnect from voice channel in guild

```python
await voice_manager.disconnect_from_voice(ctx.guild)
```

**`play_text(guild_id, text, voice=None)`** (async)
- Generate TTS audio and play immediately
- Returns: `bool` (success)

```python
success = await voice_manager.play_text(guild_id, "Hello!")
```

**`queue_text(guild_id, text, voice=None, priority=False)`**
- Queue text for playback
- Raises: `RuntimeError` if queue is full

```python
voice_manager.queue_text(guild_id, "This will be spoken next")

# Prioritize at front of queue
voice_manager.queue_text(guild_id, "Urgent message", priority=True)
```

**`process_queue(guild_id)`** (async)
- Process all queued items sequentially
- Runs continuously until queue empty

```python
await voice_manager.process_queue(guild_id)
```

**`stop_playback(guild_id)`**
- Stop current playback

```python
voice_manager.stop_playback(guild_id)
```

**`clear_queue(guild_id)`**
- Clear all queued items

```python
voice_manager.clear_queue(guild_id)
```

**`is_connected(guild_id)`**
- Check connection status
- Returns: `bool`

```python
if voice_manager.is_connected(guild_id):
    # Bot is in voice channel
```

**`get_queue_size(guild_id)`**
- Get current queue size
- Returns: `int`

```python
size = voice_manager.get_queue_size(guild_id)
```

---

## Discord Bot Integration

### Using the VoiceCommands Cog

See `voice_examples.py` for a complete example cog with commands:

```python
# In your main bot.py
from modules.voice_examples import VoiceCommands

async def setup_hook():
    await bot.add_cog(VoiceCommands(bot))
```

### Available Commands

Once integrated, your bot will have:

- `!join` - Join your voice channel
- `!leave` - Leave voice channel
- `!say <text>` - Generate and play TTS audio immediately
- `!queue <text>` - Queue text for playback
- `!stop` - Stop audio and clear queue
- `!voice [voice]` - Change or list voices
- `!queuesize` - Show queue size

### Example: Custom Integration

```python
from discord.ext import commands
from modules.voice_channel import get_voice_manager
from modules.tts_manager import get_tts_manager

class MyBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_mgr = get_voice_manager()
        self.tts_mgr = get_tts_manager()

    @commands.command()
    async def speak(self, ctx, *, message):
        """Make the bot speak"""
        if not ctx.author.voice:
            return await ctx.send("Join a voice channel first!")

        # Connect if not already connected
        if not self.voice_mgr.is_connected(ctx.guild.id):
            await self.voice_mgr.connect_to_voice(ctx.author.voice.channel)

        # Play the message
        await self.voice_mgr.play_text(ctx.guild.id, message)
```

---

## Architecture

### VoiceQueue

Internal queue system for managing audio playback:

```python
queue = VoiceQueue(max_queue_size=50)
queue.add("Text to speak")
item = queue.get_next()  # Returns {"text": ..., "voice": ...}
queue.clear()
```

### Audio Format

- **Sample Rate**: 24,000 Hz
- **Format**: WAV (PCM)
- **Max Text**: 1,000 characters per request

---

## Error Handling

Both modules include comprehensive error handling:

```python
from modules.tts_manager import TTSManager
from modules.voice_channel import VoiceChannelManager

try:
    tts = TTSManager(voice='invalid-voice')
except ValueError as e:
    print(f"Invalid voice: {e}")

try:
    voice_mgr.queue_text(guild_id, text)
except RuntimeError as e:
    print(f"Queue full: {e}")

try:
    await voice_mgr.connect_to_voice(channel)
except discord.DiscordException as e:
    print(f"Failed to connect: {e}")
```

---

## Performance Considerations

### Memory Usage

- KittenTTS model: ~25MB (loaded once on startup)
- Audio buffer: ~5MB per queued item
- Queue limit: 50 items default

### CPU Usage

- Text processing: Minimal
- Audio generation: ~100-500ms per message (CPU dependent)
- Audio playback: ~5% CPU usage during playback

### Recommendations

1. **Limit queue size** for memory efficiency
2. **Process queue asynchronously** to avoid blocking
3. **Use priority queuing** for important messages
4. **Monitor voice connections** for stale connections

---

## Logging

Both modules use Python's logging:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('modules.voice_channel')
```

Logs include:
- Model initialization
- Voice channel connections
- Audio generation progress
- Queue processing status
- Playback errors

---

## Troubleshooting

### KittenTTS Installation Issues

**Problem**: "Cannot import kittentts"

**Solution**: Install the wheel directly:
```bash
pip install https://github.com/KittenML/KittenTTS/releases/download/0.1/kittentts-0.1.0-py3-none-any.whl
```

### FFmpeg Issues

**Problem**: "ffmpeg not found"

**Solution**: Ensure FFmpeg is installed and in PATH
```bash
ffmpeg -version
```

### Voice Channel Connection Issues

**Problem**: "Failed to connect to voice channel"

**Causes**:
- Bot lacks CONNECT permission
- Bot lacks SPEAK permission
- Channel is full
- Voice client already connected

**Solution**: Check bot permissions and guild status

### Audio Playback Issues

**Problem**: "No audio playing in voice channel"

**Causes**:
- Bot lacks SPEAK permission
- FFmpeg not installed
- Audio file corrupted
- Voice client disconnected

**Solution**: Verify permissions and FFmpeg installation

---

## Future Enhancements

Potential improvements:

1. **Voice effects**: Add reverb, echo, pitch adjustment
2. **Caching**: Cache frequently used audio
3. **Multiple voices**: Random voice selection per message
4. **Multilingual**: Add language support
5. **Streaming**: Stream long messages instead of buffering
6. **Batch processing**: Generate multiple messages in parallel

---

## License

These modules are part of the AI-Discord bot project.

KittenTTS is under Apache-2.0 license: https://github.com/KittenML/KittenTTS

For support, contact the KittenML team at info@stellonlabs.com
