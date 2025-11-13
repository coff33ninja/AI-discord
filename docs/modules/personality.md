# personality Module

Personality trait system managing bot personality traits, moods, and emotional states for nuanced bot behavior.

## Overview

The `personality` module provides:
- Personality trait definitions
- Mood state management
- Emotional state tracking
- Trait-based behavior modification
- Personality evolution and learning
- Mood effects on responses

## Key Classes

### PersonalityTraits

Enum-like structure for personality types.

```python
from modules.personality import Personality, MoodState, PersonalityType

# Create personality instance
personality = Personality(
    personality_type="tsundere",
    initial_mood=50
)

# Access traits
print(personality.get_trait("friendliness"))  # 0-100

# Change mood
personality.update_mood(10)  # +10 mood
```

### Personality

Main personality management class.

```python
from modules.personality import Personality

# Initialize
personality = Personality(
    personality_type="tsundere",
    initial_mood=50,
    traits={
        "friendliness": 30,
        "arrogance": 70,
        "empathy": 40
    }
)

# Get trait
trait_value = personality.get_trait("friendliness")  # 0-100

# Modify mood
personality.update_mood(+10, reason="compliment")
```

### MoodState

Mood levels and effects.

```python
class MoodState:
    HAPPY = 100      # Very positive
    CONTENT = 75     # Positive
    NEUTRAL = 50     # Balanced
    ANNOYED = 25     # Negative
    ANGRY = 0        # Very negative
```

## Personality Types

### Available Types

| Type | Behavior | Mood Range |
|------|----------|-----------|
| **tsundere** | Rough exterior, soft interior | 20-80 |
| **kuudere** | Cold and aloof | 10-60 |
| **yandere** | Obsessive, dangerous | 30-100 |
| **dandere** | Shy, quiet | 10-50 |
| **deredere** | Sweet, cheerful | 60-100 |

### Trait Ranges

Each trait is 0-100:
- **0-25**: Low (negative aspect)
- **26-50**: Medium-low (slight negative)
- **51-75**: Medium-high (slight positive)
- **76-100**: High (very positive)

## Main Functions

### `Personality.__init__(personality_type, initial_mood, traits=None)`

Initialize personality.

**Parameters:**
- `personality_type` (str) - Type of personality
- `initial_mood` (int) - 0-100 mood level
- `traits` (dict) - Optional trait overrides

**Example:**
```python
personality = Personality(
    personality_type="tsundere",
    initial_mood=45,
    traits={
        "friendliness": 25,
        "arrogance": 75
    }
)
```

### `get_trait(trait_name)`

Get trait value.

**Parameters:**
- `trait_name` (str) - Trait name

**Returns:** int - 0-100

**Example:**
```python
friendliness = personality.get_trait("friendliness")
if friendliness < 30:
    behavior = "cold"
else:
    behavior = "warm"
```

### `set_trait(trait_name, value)`

Set trait value.

**Parameters:**
- `trait_name` (str) - Trait name
- `value` (int) - 0-100

**Example:**
```python
personality.set_trait("friendliness", 50)
```

### `update_mood(delta, reason=None)`

Adjust mood.

**Parameters:**
- `delta` (int) - Change amount (-100 to +100)
- `reason` (str) - Reason for mood change

**Returns:** int - New mood value

**Example:**
```python
new_mood = personality.update_mood(+10, reason="positive_interaction")
print(f"Mood increased to {new_mood}")
```

### `get_mood_state()`

Get current mood state.

**Returns:** str - One of HAPPY, CONTENT, NEUTRAL, ANNOYED, ANGRY

**Example:**
```python
mood_state = personality.get_mood_state()
if mood_state in ["ANNOYED", "ANGRY"]:
    response = "Stop bothering me!"
```

### `get_personality_type()`

Get personality type.

**Returns:** str - Personality type

**Example:**
```python
ptype = personality.get_personality_type()
print(f"I'm a {ptype}!")
```

### `get_description()`

Get personality description.

**Returns:** str - Human-readable description

**Example:**
```python
desc = personality.get_description()
print(desc)  # "A tsundere with average mood and high arrogance"
```

## Usage Examples

### Initialize and Check Traits

```python
from modules.personality import Personality, MoodState

# Create tsundere personality
personality = Personality(
    personality_type="tsundere",
    initial_mood=40
)

# Check friendliness
if personality.get_trait("friendliness") < 30:
    print("Keep your distance...")
else:
    print("Sure, I'll talk to you")
```

### Mood-Based Responses

```python
personality.update_mood(-15, reason="annoying_user")

mood_state = personality.get_mood_state()

if mood_state == "ANGRY":
    response = "Leave me alone!"
elif mood_state == "ANNOYED":
    response = "You're getting on my nerves..."
else:
    response = "What do you want?"

await ctx.send(response)
```

### Trait-Based Behavior

```python
# Get empathy level
empathy = personality.get_trait("empathy")

if empathy > 70:
    # High empathy - show concern
    response = f"Are you okay, {user}? I worry about you..."
elif empathy < 30:
    # Low empathy - be indifferent
    response = "Not my problem."
else:
    # Normal empathy
    response = f"I understand, {user}."
```

### Learning and Growth

```python
# Positive interaction increases friendliness
personality.set_trait("friendliness", 
    min(100, personality.get_trait("friendliness") + 5))

# Positive mood change
personality.update_mood(+8, reason="successful_interaction")

# Personality evolves over time
print(personality.get_description())
```

### Mood Decay

```python
# Periodic mood adjustment (natural decay)
async def mood_decay():
    while True:
        await asyncio.sleep(3600)  # Every hour
        
        # Mood slowly returns to baseline (50)
        current_mood = personality.mood
        if current_mood > 50:
            personality.update_mood(-5, reason="time_passing")
        elif current_mood < 50:
            personality.update_mood(+5, reason="time_passing")
```

### Get Personality Summary

```python
# Display personality in embed
personality = get_personality()

embed = discord.Embed(
    title="Personality Profile",
    color=discord.Color.purple()
)

embed.add_field(
    name="Type",
    value=personality.get_personality_type(),
    inline=True
)

embed.add_field(
    name="Mood",
    value=f"{personality.mood} ({personality.get_mood_state()})",
    inline=True
)

embed.add_field(
    name="Friendliness",
    value=f"⭐ {personality.get_trait('friendliness')}/100",
    inline=False
)

embed.add_field(
    name="Arrogance",
    value=f"👑 {personality.get_trait('arrogance')}/100",
    inline=False
)

await ctx.send(embed=embed)
```

## Trait System

### Core Traits

| Trait | Low (0-33) | Medium (34-66) | High (67-100) |
|-------|-----------|----------------|---------------|
| **friendliness** | Cold, distant | Neutral | Warm, caring |
| **arrogance** | Humble, meek | Confident | Arrogant, proud |
| **empathy** | Indifferent | Understanding | Highly empathic |
| **patience** | Easily annoyed | Normal | Very patient |
| **humor** | Serious, bland | Balanced | Funny, joke-filled |

### Trait Interactions

```python
# High arrogance + High empathy = Condescending but caring
# Low friendliness + High empathy = Reluctant helper
# High arrogance + Low empathy = Toxic
# Low friendliness + Low empathy = Indifferent
```

## Mood System

### Mood Changes

```python
+50 to +100:  Great compliment, major victory
+20 to +49:   Positive interaction, small win
-1 to +19:    Neutral, small positive
-20 to -1:    Minor annoyance, small negative
-49 to -21:   Negative interaction, insult
-50 to -100:  Major insult, betrayal
```

### Mood Recovery

```python
# Mood naturally drifts toward neutral (50)
if mood > 50:
    mood -= 2  # Gradually cool down
if mood < 50:
    mood += 2  # Gradually cheer up
```

## Performance

- **Get trait**: < 1ms
- **Set trait**: < 1ms
- **Update mood**: < 1ms
- **Get description**: < 5ms

## Dependencies

- Built-in `dataclasses` - Trait definitions
- Built-in `enum` - Mood states

## Related Documentation

- [persona_manager.py](./persona_manager.md) - Personality system management
- [config_manager.py](./config_manager.md) - Configuration management
- [response_handler.py](./response_handler.md) - Response formatting
- [Modules Overview](../MODULES.md) - Other modules

---

*Last Updated: 2025-11-14*
