# logger Module

Logging configuration and setup for application-wide logging with structured output, file rotation, and level management.

## Overview

The `logger` module provides:
- Structured logging setup
- Log level management
- File rotation
- Console formatting
- Performance tracking
- Error logging
- Debug logging with context

## Key Classes

### BotLogger

Main logger configuration class.

```python
from modules.logger import setup_logger, get_logger

# Setup logging on startup
setup_logger(level="INFO")

# Get logger for module
logger = get_logger(__name__)

# Log messages
logger.info("Bot started")
logger.warning("This is a warning")
logger.error("An error occurred")
```

## Main Functions

### `setup_logger(level="INFO", log_file=None, max_bytes=10485760, backup_count=5)`

Initialize logging system.

**Parameters:**
- `level` (str) - Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
- `log_file` (str) - Optional log file path
- `max_bytes` (int) - Max file size before rotation
- `backup_count` (int) - Number of backup files

**Example:**
```python
from modules.logger import setup_logger

setup_logger(
    level="INFO",
    log_file="bot.log",
    max_bytes=10485760,  # 10MB
    backup_count=5
)
```

### `get_logger(name)`

Get logger for module.

**Parameters:**
- `name` (str) - Usually `__name__`

**Returns:** logging.Logger

**Example:**
```python
logger = get_logger(__name__)
logger.info("Module loaded")
```

### `log_info(message, **kwargs)`

Log info level message.

**Parameters:**
- `message` (str) - Message
- `kwargs` - Additional fields

**Example:**
```python
logger.log_info("User joined", user_id=123, username="John")
```

### `log_warning(message, **kwargs)`

Log warning level message.

**Parameters:**
- `message` (str) - Message
- `kwargs` - Additional fields

**Example:**
```python
logger.log_warning("High memory usage", usage_percent=85)
```

### `log_error(message, exception=None, **kwargs)`

Log error level message.

**Parameters:**
- `message` (str) - Message
- `exception` (Exception) - Optional exception
- `kwargs` - Additional fields

**Example:**
```python
try:
    risky_operation()
except Exception as e:
    logger.log_error("Operation failed", exception=e, user_id=123)
```

### `log_debug(message, **kwargs)`

Log debug level message.

**Parameters:**
- `message` (str) - Message
- `kwargs` - Additional context

**Example:**
```python
logger.log_debug("Cache hit", key="user_123", ttl=300)
```

## Log Levels

| Level | Severity | When to Use |
|-------|----------|------------|
| **DEBUG** | Detailed diagnostic info | Development, troubleshooting |
| **INFO** | General informational | Normal operations |
| **WARNING** | Warning, potential issue | Unusual but handled situations |
| **ERROR** | Serious error | Something went wrong |
| **CRITICAL** | Critical failure | System failure |

## Setup Examples

### Basic Setup

```python
from modules.logger import setup_logger

# In main()
setup_logger(level="INFO")
```

### With File Logging

```python
setup_logger(
    level="INFO",
    log_file="logs/bot.log",
    max_bytes=10485760,  # 10MB
    backup_count=5
)
```

### Development Setup (Debug)

```python
setup_logger(level="DEBUG")
```

### Production Setup

```python
setup_logger(
    level="INFO",
    log_file="logs/bot.log",
    max_bytes=52428800,  # 50MB
    backup_count=10
)
```

## Usage Examples

### Log Application Startup

```python
from modules.logger import setup_logger, get_logger

logger = get_logger(__name__)

async def main():
    setup_logger(level="INFO", log_file="bot.log")
    
    logger.info("Starting bot...")
    
    try:
        await bot.start(token)
    except Exception as e:
        logger.error("Bot crashed", exc_info=True)
        raise
```

### Log Event Handling

```python
logger = get_logger(__name__)

@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    logger.debug(f"Message from {message.author}: {message.content[:50]}...")

@bot.event
async def on_error(event, *args, **kwargs):
    logger.error(f"Error in {event}", exc_info=True)
```

### Log Command Execution

```python
logger = get_logger(__name__)

@bot.before_invoke
async def before_any_command(ctx):
    logger.info(f"Command: {ctx.command.name} by {ctx.author}")

@bot.after_invoke
async def after_any_command(ctx):
    logger.debug(f"Completed: {ctx.command.name}")
```

### Log API Calls

```python
logger = get_logger(__name__)

async def make_api_request(endpoint, data):
    logger.debug(f"API request: {endpoint}")
    
    try:
        response = await api.post(endpoint, data)
        logger.info(f"API success: {endpoint}")
        return response
    except Exception as e:
        logger.error(f"API failed: {endpoint}", exc_info=True)
        raise
```

### Log User Actions

```python
logger = get_logger(__name__)

@bot.command()
async def warn_user(ctx, user: discord.Member, reason: str):
    logger.warning(
        f"User warned: {user.name}",
        user_id=user.id,
        mod_id=ctx.author.id,
        reason=reason
    )
    
    await ctx.send(f"Warned {user.mention}")
```

### Log Performance

```python
import time
logger = get_logger(__name__)

@bot.command()
async def slow_command(ctx):
    start = time.time()
    
    result = await expensive_operation()
    
    duration = time.time() - start
    logger.info(f"Operation completed in {duration:.2f}s")
    
    await ctx.send(f"Result: {result}")
```

### Conditional Logging

```python
logger = get_logger(__name__)

@bot.command()
async def process(ctx, data):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Processing: {data}")
    
    # Do work
    
    logger.info("Processing complete")
```

## Log Output Format

### Console Format

```
[2024-01-15 14:32:10] INFO - modules.bot - Bot started successfully
[2024-01-15 14:32:15] DEBUG - modules.api - API request: /chat
[2024-01-15 14:33:20] WARNING - modules.database - Slow query detected
```

### File Format

```
2024-01-15 14:32:10,123 - modules.bot - INFO - Bot started successfully
2024-01-15 14:32:15,456 - modules.api - DEBUG - API request: /chat
2024-01-15 14:33:20,789 - modules.database - WARNING - Slow query detected
```

## Log Rotation

Logs rotate automatically when size exceeds limit:

```
bot.log          (current)
bot.log.1        (previous)
bot.log.2        (older)
bot.log.3        (oldest)
bot.log.4        (deleted)
```

## Performance

- **Setup**: ~50ms
- **Log message**: ~2-5ms
- **File rotation**: ~100ms

## Best Practices

1. **Use appropriate levels**
   - DEBUG: Development only
   - INFO: Important events
   - WARNING: Handled errors
   - ERROR: Unhandled errors

2. **Log context**
   ```python
   logger.info("Action", user_id=123, action="ban")
   ```

3. **Don't log secrets**
   ```python
   logger.info(f"API key: {key}")  # BAD!
   logger.info("API key configured")  # GOOD
   ```

4. **Use exception info**
   ```python
   except Exception as e:
       logger.error("Failed", exc_info=True)  # Includes traceback
   ```

5. **Rotate logs**
   - Set max_bytes and backup_count
   - Archive old logs

## Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| Logs not appearing | Check log level, call setup_logger() first |
| File permissions | Check write permissions in log directory |
| Disk full | Reduce backup_count or max_bytes |
| Performance impact | Don't log in tight loops |

## Dependencies

- Built-in `logging` - Logging framework
- Built-in `logging.handlers` - Rotating handler

## Related Documentation

- [config_manager.py](./config_manager.md) - Configuration
- [Modules Overview](../MODULES.md) - Other modules

---

*Last Updated: 2025-11-14*
