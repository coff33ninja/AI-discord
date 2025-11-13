# config_manager Module

Bot configuration management for loading, validating, and managing application-wide settings and environment variables.

## Overview

The `config_manager` module handles:
- Environment variable loading (.env files)
- Configuration validation
- Settings access and caching
- Hot reload of configurations
- Secret management
- Default configuration fallbacks
- Configuration health checks

## Key Classes

### ConfigManager

Singleton for managing all bot configuration.

```python
from modules.config_manager import ConfigManager, get_config_manager

# Get singleton instance
config = get_config_manager()

# Get setting
token = config.get("DISCORD_TOKEN")

# Get with default
log_level = config.get("LOG_LEVEL", default="INFO")

# Check if setting exists
if config.has("GEMINI_API_KEY"):
    print("API key configured")
```

## Main Functions

### `get(key, default=None)`

Get configuration value.

**Parameters:**
- `key` (str) - Configuration key
- `default` (any) - Default value if not found

**Returns:** any - Configuration value

**Example:**
```python
token = config.get("DISCORD_TOKEN")
timeout = config.get("API_TIMEOUT", default=30)
```

### `set(key, value)`

Set configuration value (runtime only, not persisted).

**Parameters:**
- `key` (str) - Configuration key
- `value` (any) - Value to set

**Example:**
```python
config.set("CURRENT_USER", "John")
```

### `has(key)`

Check if key exists.

**Parameters:**
- `key` (str) - Configuration key

**Returns:** bool

**Example:**
```python
if config.has("API_KEY"):
    print("API configured")
```

### `load_env(path=".env")`

Load environment file.

**Parameters:**
- `path` (str) - Path to .env file

**Returns:** bool - Success

**Example:**
```python
success = await config.load_env(".env.local")
if success:
    print("Config loaded")
```

### `reload()`

Reload configuration from file.

**Returns:** bool - Success

**Example:**
```python
await config.reload()
print("Configuration reloaded")
```

### `validate()`

Validate all required settings.

**Returns:** dict with:
- `valid` (bool) - All required settings present
- `missing` (list) - Missing required keys
- `invalid` (list) - Invalid format

**Example:**
```python
result = config.validate()
if not result['valid']:
    print(f"Missing: {result['missing']}")
```

### `get_all()`

Get all configuration (safe - without secrets).

**Returns:** dict - Configuration

**Example:**
```python
all_config = config.get_all()
print(all_config)
```

### `as_dict(include_secrets=False)`

Export configuration as dictionary.

**Parameters:**
- `include_secrets` (bool) - Include API keys

**Returns:** dict

**Example:**
```python
safe_config = config.as_dict(include_secrets=False)
```

## Configuration Keys

### Required Keys

| Key | Description | Example |
|-----|-------------|---------|
| **DISCORD_TOKEN** | Discord bot token | `MzI4...` |
| **GEMINI_API_KEY** | Google Gemini API key | `AIzaSy...` |

### Optional Keys

| Key | Description | Default |
|-----|-------------|---------|
| **PREFIX** | Command prefix | `!` |
| **LOG_LEVEL** | Logging level | `INFO` |
| **API_TIMEOUT** | API timeout (seconds) | `30` |
| **DATABASE_PATH** | SQLite database path | `data/ai_database.db` |
| **CACHE_SIZE** | Response cache entries | `1000` |
| **MAX_RETRIES** | API retry attempts | `3` |
| **RATE_LIMIT_WINDOW** | Rate limit window (seconds) | `60` |

## Environment File Example

`.env` file:

```env
# Discord Configuration
DISCORD_TOKEN=your_bot_token_here
PREFIX=!

# API Configuration
GEMINI_API_KEY=your_api_key_here
API_TIMEOUT=30
MAX_RETRIES=3

# Logging
LOG_LEVEL=INFO

# Database
DATABASE_PATH=data/ai_database.db

# Features
ENABLE_VOICE=true
ENABLE_GAMES=true
```

## Usage Examples

### Load Configuration on Startup

```python
import asyncio
from modules.config_manager import get_config_manager

async def main():
    config = get_config_manager()
    
    # Load .env file
    success = await config.load_env(".env")
    if not success:
        print("Failed to load configuration!")
        return
    
    # Validate required settings
    result = config.validate()
    if not result['valid']:
        print(f"Missing settings: {result['missing']}")
        return
    
    # Start bot
    token = config.get("DISCORD_TOKEN")
    await bot.start(token)

asyncio.run(main())
```

### Access Configuration

```python
config = get_config_manager()

# Get simple value
prefix = config.get("PREFIX", default="!")

# Get with validation
timeout = int(config.get("API_TIMEOUT", default=30))

# Check existence
if config.has("CUSTOM_SETTING"):
    custom = config.get("CUSTOM_SETTING")
```

### Validate Configuration

```python
@bot.command()
@commands.is_owner()
async def check_config(ctx):
    config = get_config_manager()
    
    result = config.validate()
    
    if result['valid']:
        await ctx.send("✅ Configuration is valid")
    else:
        missing = ", ".join(result['missing'])
        await ctx.send(f"❌ Missing: {missing}")
```

### Log Configuration

```python
def setup_logging():
    config = get_config_manager()
    
    log_level = config.get("LOG_LEVEL", "INFO")
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
```

### Runtime Configuration Changes

```python
# Get current setting
current_prefix = config.get("PREFIX")

# Change at runtime (temporary)
config.set("PREFIX", ">>")

# Check new value
print(config.get("PREFIX"))  # ">>"

# Note: Changes not persisted, reload from file to restore
```

### Export Configuration

```python
@bot.command()
@commands.is_owner()
async def show_config(ctx):
    config = get_config_manager()
    
    # Get safe config (no secrets)
    safe_config = config.as_dict(include_secrets=False)
    
    config_str = "\n".join(
        f"{k}: {v}" for k, v in safe_config.items()
    )
    
    embed = discord.Embed(
        title="Bot Configuration",
        description=f"```\n{config_str}\n```",
        color=discord.Color.blue()
    )
    
    await ctx.send(embed=embed)
```

## Configuration Hierarchy

Configuration is loaded in this order (later overrides earlier):

1. **Defaults** - Built-in defaults
2. **.env file** - Environment file
3. **System environment** - OS environment variables
4. **Runtime changes** - `config.set()` calls

## Secret Management

**Sensitive fields** (automatically hidden):
- `DISCORD_TOKEN`
- `GEMINI_API_KEY`
- `DATABASE_PASSWORD`
- Any key containing "SECRET", "PASSWORD", "KEY", or "TOKEN"

```python
# Safe display (hides secrets)
config.get_all()  # Secrets masked

# Unsafe display (shows secrets - admin only!)
config.as_dict(include_secrets=True)
```

## Validation Rules

Automatic validation:

1. Required keys must exist
2. API keys must be non-empty
3. Numeric settings must be valid numbers
4. Timeout values must be positive
5. Paths must be valid

## Performance

- **Get setting**: < 1ms
- **Set setting**: < 1ms
- **Load .env**: ~10ms
- **Validate**: ~20ms
- **Reload**: ~50ms

## Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| Token not loading | Check .env file location and format |
| Settings undefined | Call load_env() before access |
| Changes not persisting | Edit .env file, then reload() |
| Secrets visible | Don't use include_secrets=True |

## Best Practices

1. **Never hardcode secrets** - Use .env files
2. **Validate on startup** - Call validate() early
3. **Use defaults** - Provide sensible defaults
4. **Reload carefully** - Some changes require restart
5. **Hide secrets** - Don't log or display API keys

## Dependencies

- Built-in `os` - Environment variables
- Built-in `dotenv` - Load .env files
- Built-in `logging` - Logging integration

## Related Documentation

- [logger.py](./logger.md) - Logging configuration
- [ai_database.py](./ai_database.md) - Database configuration
- [api_manager.py](./api_manager.md) - API configuration
- [Modules Overview](../MODULES.md) - Other modules

---

*Last Updated: 2025-11-14*
