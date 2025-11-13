# persona_manager Module

Personality system management for loading, validating, and managing bot personality/character configuration.

## Overview

The `persona_manager` module manages:
- Persona/personality file loading
- Personality configuration validation
- Bot name management
- Personality trait access
- Persona reloading and hot-swap
- Configuration health checks

## Key Classes

### PersonaManager

Main class for personality system.

```python
from modules.persona_manager import PersonaManager, get_persona_manager

# Get singleton instance
persona = get_persona_manager()

# Get bot name
name = persona.get_name()

# Access personality
traits = persona.persona.get("traits")

# Reload configuration
await persona.reload_persona()
```

## Main Functions

### `get_name()`
Get bot's current name.

**Returns:** str - Bot name

**Example:**
```python
name = persona.get_name()
print(f"I am {name}")  # "I am Akeno"
```

### `get_personality()`
Get full personality configuration.

**Returns:** dict - Complete persona object

**Example:**
```python
persona_config = persona.get_personality()
print(persona_config.keys())  # personality traits, responses, etc.
```

### `reload_persona()`
Reload personality from file.

**Returns:** bool - Success

**Example:**
```python
success = await persona.reload_persona()
if success:
    print("Personality reloaded!")
```

### `validate_persona()`
Validate persona configuration.

**Returns:** dict with:
- `valid` (bool) - Configuration is valid
- `errors` (list) - Validation errors
- `warnings` (list) - Warnings

**Example:**
```python
result = persona.validate_persona()
if result['valid']:
    print("Persona is valid!")
else:
    for error in result['errors']:
        print(f"❌ {error}")
```

### `get_response(response_key, context=None)`
Get personality-based response.

**Parameters:**
- `response_key` (str) - Response type key
- `context` (dict) - Context variables

**Returns:** str - Response text

**Example:**
```python
response = persona.get_response(
    "greeting",
    context={"user_name": "John"}
)
```

### `health_check()`
Check persona configuration health.

**Returns:** dict with status and issues

**Example:**
```python
health = persona.health_check()
print(f"Health: {health['status']}")
for issue in health['issues']:
    print(f"Issue: {issue}")
```

## Persona Structure

Persona file (`persona_card.json`) contains:

```json
{
  "bot_name": "Akeno",
  "traits": {
    "personality_type": "tsundere",
    "mood": 50,
    "friendliness": 30
  },
  "responses": {
    "greeting": "What do you want?",
    "compliment": "N-not bad, I guess...",
    "goodbye": "F-farewell then..."
  },
  "behavior": {
    "use_swearing": true,
    "show_emotion": true
  }
}
```

## Usage Examples

### Get Bot Name

```python
persona = get_persona_manager()

name = persona.get_name()
print(f"Hello! I'm {name}!")
```

### Access Personality Traits

```python
persona_data = persona.get_personality()

personality_type = persona_data.get("traits", {}).get("personality_type")
mood = persona_data.get("traits", {}).get("mood")

print(f"I'm a {personality_type} with mood {mood}")
```

### Get Contextual Responses

```python
# In on_message event
response = persona.get_response(
    "greeting",
    context={"user_name": member.name}
)

await ctx.send(response)
```

### Reload Persona (Admin Command)

```python
@bot.command()
@commands.is_owner()
async def reload_persona(ctx):
    persona = get_persona_manager()
    
    success = await persona.reload_persona()
    if success:
        await ctx.send("✅ Personality reloaded!")
    else:
        await ctx.send("❌ Failed to reload personality")
```

### Validate Configuration

```python
@bot.command()
@commands.is_owner()
async def persona_health(ctx):
    persona = get_persona_manager()
    
    result = persona.validate_persona()
    
    if result['valid']:
        await ctx.send("✅ Persona is healthy")
    else:
        errors = "\n".join(result['errors'])
        await ctx.send(f"❌ Errors:\n{errors}")
```

## Persona Configuration File

Default location: `persona_card.json`

### Required Fields

```json
{
  "bot_name": "Bot Name",
  "traits": {
    "personality_type": "Type (tsundere, etc.)"
  },
  "responses": {
    "greeting": "Response text"
  }
}
```

### Optional Fields

- `behavior` - Behavior settings
- `moods` - Mood descriptions
- `activity_responses` - Activity-based responses
- `help_command` - Help command configuration
- `preferences` - Bot preferences

## Reloading Personality

Hot-swap personality without restarting bot:

```python
# User modifies persona_card.json

# Admin runs command
!reload_persona

# Personality updates immediately
```

## Validation

Automatic validation checks:
1. Bot name exists
2. Required traits present
3. Response keys defined
4. No missing required fields
5. Type checking

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Bot name not found | Add "bot_name" field to persona_card.json |
| Missing responses | Add required response keys |
| Invalid JSON | Use JSON validator |
| Config not updating | Use !reload_persona command |

## Performance

- **Get name**: < 1ms
- **Get personality**: < 5ms
- **Validate**: < 50ms
- **Reload**: ~100ms

## Dependencies

- Built-in `json` - JSON parsing
- Built-in `asyncio` - Async operations

## Related Documentation

- [personality.py](./personality.py.md) - Traits and mood system
- [config_manager.py](./config_manager.md) - General configuration
- [Modules Overview](../MODULES.md) - Other modules

---

*Last Updated: 2025-11-14*
