# ai_database Module

SQLite database for persistent storage of conversations, user data, relationships, reminders, and bot state.

## Overview

The `ai_database` module manages all persistent data storage using SQLite. It provides:
- Conversation history tracking
- User relationship data
- Reminder/subscription storage
- Chat analytics and statistics
- Async database operations

## Key Classes

### AIDatabase

Main class for database operations.

```python
from modules.ai_database import AIDatabase

# Initialize (creates tables if needed)
db = AIDatabase()

# Save conversation
await db.add_conversation(user_id, guild_id, "user_message", "ai_response")

# Get history
history = await db.get_conversation_history(user_id, guild_id)

# Update relationship
await db.update_relationship(user_id, guild_id, 5)
```

## Database Tables

### `conversations`
Stores all user-AI interactions.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Auto-increment ID |
| user_id | TEXT | Discord user ID |
| guild_id | TEXT | Discord server ID |
| user_message | TEXT | User's message |
| ai_response | TEXT | Bot's response |
| timestamp | DATETIME | When conversation happened |

### `relationships`
Tracks friendship levels between users and bot.

| Column | Type | Description |
|--------|------|-------------|
| user_id | TEXT PRIMARY KEY | Discord user ID |
| guild_id | TEXT | Discord server ID |
| interaction_count | INTEGER | Number of interactions |
| relationship_level | INTEGER | 0-100 friendship level |
| last_interaction | DATETIME | Last message timestamp |

### `subscriptions`
Stores user subscriptions to daily features.

| Column | Type | Description |
|--------|------|-------------|
| user_id | TEXT PRIMARY KEY | Discord user ID |
| feature | TEXT | Feature name (daily_fact, daily_joke, etc.) |
| subscribed | BOOLEAN | Subscription status |
| last_sent | DATETIME | Last notification time |

### `reminders`
Stores scheduled reminders.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Reminder ID |
| user_id | TEXT | Discord user ID |
| guild_id | TEXT | Discord server ID |
| message | TEXT | Reminder text |
| scheduled_time | DATETIME | When to notify |
| created_at | DATETIME | Creation timestamp |
| sent | BOOLEAN | Whether sent |

### `facts`
Custom facts added by users.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Fact ID |
| key | TEXT | Fact category/keyword |
| content | TEXT | Fact text |
| added_by | TEXT | User who added it |
| added_at | DATETIME | When added |

### `followups`
Q&A pairs saved by users.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Entry ID |
| question | TEXT | Question text |
| answer | TEXT | Saved answer |
| user_id | TEXT | User who saved |
| created_at | DATETIME | When saved |
| used_count | INTEGER | Times referenced |

## Main Functions

### Conversations

#### `add_conversation(user_id, guild_id, user_message, ai_response)`
Store a conversation exchange.

```python
await db.add_conversation(
    user_id="123456789",
    guild_id="987654321",
    user_message="What is AI?",
    ai_response="AI is artificial intelligence..."
)
```

#### `get_conversation_history(user_id, guild_id, limit=10)`
Retrieve user's conversation history.

```python
history = await db.get_conversation_history(
    user_id="123456789",
    guild_id="987654321",
    limit=20  # Last 20 messages
)
# Returns list of dicts with user_message, ai_response, timestamp
for conv in history:
    print(f"User: {conv['user_message']}")
    print(f"Bot: {conv['ai_response']}")
```

#### `get_recent_context(user_id, guild_id, message_count=5)`
Get recent messages for context.

```python
context = await db.get_recent_context(
    user_id="123456789",
    guild_id="987654321",
    message_count=10
)
# Returns conversation history for AI context
```

### Relationships

#### `update_relationship(user_id, guild_id, increment=1)`
Increment friendship level.

```python
# Increase relationship by 5 points
await db.update_relationship(
    user_id="123456789",
    guild_id="987654321",
    increment=5
)
```

#### `get_relationship(user_id, guild_id)`
Get current relationship level.

```python
rel = await db.get_relationship(
    user_id="123456789",
    guild_id="987654321"
)
print(f"Relationship: {rel['relationship_level']}/100")
print(f"Interactions: {rel['interaction_count']}")
```

#### `get_relationship_level_name(relationship_score)`
Get relationship tier name.

```python
level = db.get_relationship_level_name(45)
print(level)  # "Friend" or "Acquaintance" etc.
```

### Subscriptions

#### `add_subscription(user_id, feature)`
Subscribe user to feature.

```python
await db.add_subscription(
    user_id="123456789",
    feature="daily_fact"
)
```

#### `get_subscriptions(user_id)`
Get user's active subscriptions.

```python
subs = await db.get_subscriptions(user_id="123456789")
# Returns list of subscribed features
for sub in subs:
    print(f"Subscribed to: {sub}")
```

#### `remove_subscription(user_id, feature)`
Unsubscribe from feature.

```python
await db.remove_subscription(
    user_id="123456789",
    feature="daily_joke"
)
```

### Reminders

#### `add_reminder(user_id, guild_id, message, scheduled_time)`
Create a reminder.

```python
from datetime import datetime, timedelta

scheduled = datetime.now() + timedelta(minutes=5)
reminder_id = await db.add_reminder(
    user_id="123456789",
    guild_id="987654321",
    message="Take a break",
    scheduled_time=scheduled
)
print(f"Reminder #{reminder_id} set")
```

#### `get_pending_reminders()`
Get reminders to send now.

```python
pending = await db.get_pending_reminders()
for reminder in pending:
    print(f"Send to user {reminder['user_id']}: {reminder['message']}")
```

#### `mark_reminder_sent(reminder_id)`
Mark reminder as delivered.

```python
await db.mark_reminder_sent(reminder_id=1)
```

#### `delete_reminder(reminder_id)`
Delete a reminder.

```python
await db.delete_reminder(reminder_id=1)
```

### Facts & Knowledge

#### `add_fact(key, content, added_by)`
Add a custom fact.

```python
await db.add_fact(
    key="gravity",
    content="Gravity pulls objects toward each other",
    added_by="123456789"
)
```

#### `get_fact(key)`
Retrieve a fact.

```python
fact = await db.get_fact("gravity")
if fact:
    print(fact['content'])
```

#### `get_all_facts()`
Get all stored facts.

```python
facts = await db.get_all_facts()
for fact in facts:
    print(f"{fact['key']}: {fact['content']}")
```

### Follow-ups (Q&A)

#### `add_followup(question, answer, user_id)`
Save a Q&A pair.

```python
await db.add_followup(
    question="What is the capital of France?",
    answer="Paris",
    user_id="123456789"
)
```

#### `get_followup(question)`
Retrieve saved answer.

```python
followup = await db.get_followup("What is the capital of France?")
if followup:
    print(followup['answer'])
```

## Usage Examples

### Track Conversation Flow

```python
db = AIDatabase()

# Store interaction
await db.add_conversation(
    user_id=user_id,
    guild_id=guild_id,
    user_message="Hello!",
    ai_response="Hi there!"
)

# Get conversation history for context
history = await db.get_recent_context(user_id, guild_id, 5)
context = "\n".join([
    f"User: {h['user_message']}\nBot: {h['ai_response']}"
    for h in history
])

# Use context in next AI call
response = await api_manager.generate_content(
    f"Previous conversation:\n{context}\n\nUser's new message: {new_message}"
)
```

### Relationship Tracking

```python
# After each interaction
await db.update_relationship(user_id, guild_id, increment=1)

# Check relationship level
rel = await db.get_relationship(user_id, guild_id)
level_name = db.get_relationship_level_name(rel['relationship_level'])

if rel['relationship_level'] > 50:
    response = "I've grown fond of you, but don't tell anyone!"
```

### Reminder System

```python
from datetime import datetime, timedelta

# User sets reminder
target_time = datetime.now() + timedelta(hours=2)
reminder_id = await db.add_reminder(
    user_id=user_id,
    guild_id=guild_id,
    message="Check the oven",
    scheduled_time=target_time
)

# Later, check pending reminders
pending = await db.get_pending_reminders()
for reminder in pending:
    # Send to user...
    await db.mark_reminder_sent(reminder['id'])
```

### Custom Knowledge Base

```python
# User teaches bot
await db.add_fact(
    key="custom_command",
    content="This does something special",
    added_by=user_id
)

# Bot uses knowledge
fact = await db.get_fact("custom_command")
if fact:
    await ctx.send(f"I remember: {fact['content']}")
```

## Database Location

The database file is stored at:
```
data/ai_database.db
```

It's automatically created on first run with all required tables.

## Async Operations

All database operations are async and non-blocking:

```python
import asyncio

async def example():
    db = AIDatabase()
    
    # Non-blocking database calls
    history = await db.get_conversation_history(user_id, guild_id)
    await db.update_relationship(user_id, guild_id, 5)
    
    # Multiple operations in parallel
    results = await asyncio.gather(
        db.get_relationship(user_id, guild_id),
        db.get_subscriptions(user_id),
        db.get_all_facts()
    )

asyncio.run(example())
```

## Maintenance

### Backup Database

```bash
# Windows
Copy-Item -Path data/ai_database.db -Destination data/ai_database.backup.db

# Linux/Mac
cp data/ai_database.db data/ai_database.backup.db
```

### Clear Conversation History

```python
# Not provided - modify database directly or add method
# This is intentional to prevent accidental data loss
```

## Performance

- Uses async SQLite (aiosqlite) for non-blocking operations
- Indexes on frequently queried columns (user_id, guild_id)
- Efficient pagination for history retrieval

## Dependencies

- `aiosqlite` - Async SQLite operations
- Built-in `sqlite3` - Database engine
- Built-in `asyncio` - Async support

## Related Documentation

- [Commands Reference](../commands.md) - Commands using database
- [Modules Overview](../MODULES.md) - Other modules
- See docstrings in `ai_database.py` for full API

---

*Last Updated: 2025-11-14*
