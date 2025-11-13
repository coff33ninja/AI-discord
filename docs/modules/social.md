# social Module

Relationship tracking system for user-bot interactions with friendship levels, interaction counting, and personalized responses.

## Overview

The `social` module manages user relationships with:
- Progressive friendship levels (Stranger → Close Friend)
- Interaction counting and tracking
- Relationship milestones
- Context-aware responses based on relationship level
- Persistent relationship storage
- Automatic relationship growth

## Key Classes

### SocialManager

Main class for relationship management.

```python
from modules.social import SocialManager, get_social_manager

# Get singleton instance
social = get_social_manager()

# Update relationship on interaction
await social.update_relationship(user_id, guild_id, increment=1)

# Get relationship level
rel = await social.get_relationship(user_id, guild_id)

# Check relationship level name
level = social.get_relationship_level_name(rel['relationship_level'])
```

## Main Functions

### `update_relationship(user_id, guild_id, increment=1)`
Increment relationship score.

**Parameters:**
- `user_id` (str) - Discord user ID
- `guild_id` (str) - Discord guild/server ID
- `increment` (int) - Points to add (default: 1)

**Returns:** dict with:
- `relationship_level` (int) - Current level (0-100)
- `previous_level` (int) - Previous level
- `interaction_count` (int) - Total interactions
- `new_milestone` (str) - Milestone reached if any

**Example:**
```python
result = await social.update_relationship(user_id, guild_id)
if result['new_milestone']:
    print(f"Milestone reached: {result['new_milestone']}")
```

### `get_relationship(user_id, guild_id)`
Get relationship details.

**Parameters:**
- `user_id` (str) - Discord user ID
- `guild_id` (str) - Discord guild/server ID

**Returns:** dict with:
- `user_id` (str) - User ID
- `guild_id` (str) - Guild ID
- `relationship_level` (int) - 0-100
- `interaction_count` (int) - Number of interactions
- `last_interaction` (datetime) - Last message time

**Example:**
```python
rel = await social.get_relationship(user_id, guild_id)
print(f"Relationship: {rel['relationship_level']}/100")
print(f"Interactions: {rel['interaction_count']}")
```

### `get_relationship_level_name(score)`
Get human-readable relationship level.

**Parameters:**
- `score` (int) - Relationship score (0-100)

**Returns:** str - Level name

**Levels:**
- 0-10: Stranger
- 11-25: Acquaintance
- 26-50: Friend
- 51-75: Close Friend
- 76-100: Best Friend / Soulmate

**Example:**
```python
level_name = social.get_relationship_level_name(45)
print(level_name)  # "Friend"
```

### `get_relationship_tier(user_id, guild_id)`
Get full relationship tier with details.

**Returns:** dict with:
- `name` (str) - Tier name
- `level` (int) - Current score
- `progress` (int) - Progress to next level (%)
- `next_milestone` (str) - Next milestone
- `description` (str) - Tier description

**Example:**
```python
tier = await social.get_relationship_tier(user_id, guild_id)
print(f"You are a {tier['name']}")
print(f"Progress to next level: {tier['progress']}%")
```

### `get_milestone_info(score)`
Get information about relationship milestones.

**Parameters:**
- `score` (int) - Relationship score

**Returns:** dict with:
- `current_milestone` (str) - Achievement unlocked
- `next_milestone` (str) - Next achievement
- `interactions_needed` (int) - Interactions until next

**Example:**
```python
milestone = social.get_milestone_info(45)
print(f"Current: {milestone['current_milestone']}")
print(f"Next: {milestone['next_milestone']}")
print(f"Need {milestone['interactions_needed']} more interactions")
```

## Relationship Levels

### 0-10: Stranger
- Bot treats you politely but distant
- Might be suspicious
- Tsundere personality just starting

**Response Style:** Formal, cautious

### 11-25: Acquaintance
- Getting to know each other
- Bot becomes slightly warmer
- Still maintains distance

**Response Style:** Friendly but reserved

### 26-50: Friend
- Regular interactions
- Bot shows caring attitude
- Gets flustered by compliments
- Shares more personality

**Response Style:** Warm, genuinely helpful

### 51-75: Close Friend
- Deep connection established
- Bot clearly cares about you
- Flustered more easily
- Shows vulnerability

**Response Style:** Very warm, affectionate (but denies it)

### 76-100: Best Friend / Soulmate
- Maximum relationship level
- Bot acts like you're special
- Openly (but tsunderely) cares
- Most vulnerable responses

**Response Style:** Love-interest level affection (tsundere)

## Milestones

Users unlock achievements as relationship grows:

| Score | Milestone | Unlock |
|-------|-----------|--------|
| 10 | First Encounter | Friend status reached |
| 25 | Getting Close | Acquaintance upgraded |
| 50 | True Friend | Friend status reached |
| 75 | Very Special | Close Friend reached |
| 100 | Soulmate | Best Friend reached |

## Usage Examples

### Automatic Relationship Tracking

```python
social = get_social_manager()

# In on_message event
async def on_message(message):
    # Update relationship on interaction
    result = await social.update_relationship(
        message.author.id,
        message.guild.id
    )
    
    # Get current relationship
    rel = await social.get_relationship(
        message.author.id,
        message.guild.id
    )
    level_name = social.get_relationship_level_name(rel['relationship_level'])
    
    # Use in AI response
    context = f"User relationship level: {level_name}"
    # ... pass to AI for personalized response
```

### Relationship-Based Responses

```python
rel = await social.get_relationship(user_id, guild_id)
level = rel['relationship_level']

if level < 25:
    greeting = "What do you want?"
elif level < 50:
    greeting = "Hey there!"
elif level < 75:
    greeting = "Oh, it's you! Hi!"
else:
    greeting = "There you are! I was hoping you'd show up!"

await ctx.send(greeting)
```

### Display Relationship Status

```python
rel = await social.get_relationship(user_id, guild_id)
tier = await social.get_relationship_tier(user_id, guild_id)

await ctx.send(
    f"**Your Relationship Status:**\n"
    f"Tier: {tier['name']}\n"
    f"Score: {rel['relationship_level']}/100\n"
    f"Progress: {tier['progress']}%\n"
    f"Interactions: {rel['interaction_count']}\n"
    f"Next Milestone: {tier['next_milestone']}"
)
```

### Milestone Celebration

```python
result = await social.update_relationship(user_id, guild_id, increment=10)

if result['new_milestone']:
    await ctx.send(
        f"🎉 **Milestone Unlocked!**\n"
        f"{result['new_milestone']}\n"
        f"Your relationship level is now {result['relationship_level']}"
    )
```

### Relationship-Based AI Prompt

```python
rel = await social.get_relationship(user_id, guild_id)
tier = social.get_relationship_level_name(rel['relationship_level'])

prompt = f"""
You are Akeno, a tsundere AI. The user {member.name} has relationship level: {tier}

Based on this:
- If Stranger: Be formal and cautious
- If Acquaintance: Be friendly but reserved
- If Friend: Be warm and helpful
- If Close Friend: Show you care (but deny it)
- If Best Friend: Act like they're special to you

User message: {user_message}
"""

response = await api_manager.generate_content(prompt)
```

## Per-Guild Relationships

Relationships are tracked per-guild:
```python
# Different relationship in each server
rel1 = await social.get_relationship(user_id, guild_id_1)
rel2 = await social.get_relationship(user_id, guild_id_2)

# rel1 and rel2 can be completely different
```

## Interaction Counting

Each interaction increments counter:
- Each message: +1
- Compliments: +5
- Commands: +1
- Games played: +2
- etc.

## Storage

Relationships stored in `ai_database.db` table:
- `user_id` - Discord user ID
- `guild_id` - Discord guild ID
- `relationship_level` - 0-100 score
- `interaction_count` - Total interactions
- `last_interaction` - Last message time

## Performance

- **Get relationship**: < 50ms
- **Update relationship**: < 100ms
- **Milestone calculation**: < 10ms
- **All relationships for user**: < 500ms

## Dependencies

- `ai_database` - Persistent storage
- Built-in `datetime` - Timestamp tracking

## Related Documentation

- [Commands Reference](../commands.md) - Relationship commands
- [ai_database.md](./ai_database.md) - Storage details
- [persona_manager.md](./persona_manager.md) - Personality system
- [Modules Overview](../MODULES.md) - Other modules

---

*Last Updated: 2025-11-14*
