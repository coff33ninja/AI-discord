# time_utilities Module

Time operations and reminder system for scheduling, time management, and reminder notifications.

## Overview

The `time_utilities` module provides:
- Current time retrieval and formatting
- Reminder creation and management
- Scheduled notifications
- Natural language time parsing
- Timezone support
- Reminder persistence

## Key Classes

### TimeUtilities

Main class for time operations.

```python
from modules.time_utilities import TimeUtilities, get_time_utilities

# Get singleton instance
time_util = get_time_utilities()

# Get current time
current = time_util.get_current_time()

# Create reminder
reminder_id = await time_util.create_reminder(
    user_id, guild_id,
    "Take a break",
    datetime.now() + timedelta(minutes=30)
)
```

## Main Functions

### `get_current_time(timezone=None)`
Get current time with optional timezone.

**Parameters:**
- `timezone` (str) - Timezone code (optional, default: UTC)

**Returns:** dict with:
- `time` (str) - Formatted time
- `date` (str) - Formatted date
- `day` (str) - Day of week
- `timezone` (str) - Current timezone
- `unix_timestamp` (int) - Unix timestamp

**Example:**
```python
current = time_util.get_current_time()
print(f"Current time: {current['time']} on {current['date']}")
```

### `create_reminder(user_id, guild_id, message, scheduled_time)`
Create a new reminder.

**Parameters:**
- `user_id` (str) - Discord user ID
- `guild_id` (str) - Discord guild ID
- `message` (str) - Reminder text
- `scheduled_time` (datetime) - When to send reminder

**Returns:** dict with:
- `reminder_id` (int) - Unique ID
- `user_id` (str) - User ID
- `message` (str) - Reminder text
- `scheduled_time` (datetime) - Scheduled time
- `created_at` (datetime) - Creation time

**Example:**
```python
from datetime import datetime, timedelta

reminder = await time_util.create_reminder(
    user_id=user_id,
    guild_id=guild_id,
    message="Take a break",
    scheduled_time=datetime.now() + timedelta(minutes=30)
)

print(f"Reminder #{reminder['reminder_id']} set!")
```

### `parse_time_string(time_string)`
Parse natural language time strings.

**Parameters:**
- `time_string` (str) - Natural language time

**Returns:** datetime object

**Supported Formats:**
- "in 5 minutes"
- "in 1 hour"
- "tomorrow at 3 PM"
- "next Monday"
- "at 5:30 PM"

**Example:**
```python
remind_time = time_util.parse_time_string("in 30 minutes to take a break")
print(f"Will remind at: {remind_time}")
```

### `get_pending_reminders()`
Get all reminders due now.

**Returns:** list of dict with:
- `reminder_id` (int) - ID
- `user_id` (str) - User to notify
- `guild_id` (str) - Guild context
- `message` (str) - Reminder text
- `scheduled_time` (datetime) - Scheduled time

**Example:**
```python
pending = await time_util.get_pending_reminders()
for reminder in pending:
    # Send to user via DM
    await send_reminder_notification(reminder)
```

### `get_user_reminders(user_id)`
Get all reminders for a user.

**Parameters:**
- `user_id` (str) - Discord user ID

**Returns:** list of reminders for user

**Example:**
```python
reminders = await time_util.get_user_reminders(user_id)
for reminder in reminders:
    print(f"#{reminder['reminder_id']}: {reminder['message']} at {reminder['scheduled_time']}")
```

### `cancel_reminder(reminder_id)`
Cancel a scheduled reminder.

**Parameters:**
- `reminder_id` (int) - Reminder to cancel

**Returns:** bool - Success

**Example:**
```python
success = await time_util.cancel_reminder(reminder_id=1)
if success:
    print("Reminder cancelled")
```

### `get_time_until(target_datetime)`
Calculate time until a future datetime.

**Parameters:**
- `target_datetime` (datetime) - Target time

**Returns:** dict with:
- `seconds` (int) - Seconds until
- `formatted` (str) - Human readable (e.g., "5 hours, 30 minutes")

**Example:**
```python
reminder_time = datetime.now() + timedelta(hours=2)
until = time_util.get_time_until(reminder_time)
print(f"Reminder in: {until['formatted']}")
```

## Usage Examples

### Set a Reminder

```python
from datetime import datetime, timedelta

time_util = get_time_utilities()

# Simple reminder
await time_util.create_reminder(
    user_id=user_id,
    guild_id=guild_id,
    message="Check the oven",
    scheduled_time=datetime.now() + timedelta(minutes=30)
)

await ctx.send("⏰ Reminder set for 30 minutes from now")
```

### Natural Language Reminders

```python
# User: "!remind in 1 hour to call mom"
time_str = "in 1 hour"
reminder_text = "call mom"

scheduled = time_util.parse_time_string(time_str)
reminder = await time_util.create_reminder(
    user_id=user_id,
    guild_id=guild_id,
    message=reminder_text,
    scheduled_time=scheduled
)

until = time_util.get_time_until(scheduled)
await ctx.send(f"✅ I'll remind you to '{reminder_text}' {until['formatted']} from now")
```

### List User's Reminders

```python
reminders = await time_util.get_user_reminders(user_id)

if not reminders:
    await ctx.send("You don't have any reminders")
else:
    message = "📋 **Your Reminders:**\n"
    for r in reminders:
        until = time_util.get_time_until(r['scheduled_time'])
        message += f"#{r['reminder_id']}: {r['message']} (in {until['formatted']})\n"
    
    await ctx.send(message)
```

### Cancel Reminder

```python
# User: "!cancelreminder 1"
success = await time_util.cancel_reminder(reminder_id=1)

if success:
    await ctx.send("✅ Reminder cancelled")
else:
    await ctx.send("❌ Reminder not found")
```

### Reminder Check Loop

```python
# Run periodically (every minute)
async def check_reminders():
    pending = await time_util.get_pending_reminders()
    
    for reminder in pending:
        user = bot.get_user(int(reminder['user_id']))
        
        # Send DM
        await user.send(
            f"🔔 **Reminder:** {reminder['message']}"
        )
        
        # Mark as sent
        await time_util.mark_reminder_sent(reminder['reminder_id'])
```

## Supported Time Formats

### Relative Times
- "in 5 minutes"
- "in 1 hour"
- "in 2 days"
- "in 1 week"

### Absolute Times
- "at 3:00 PM"
- "at 15:30"
- "tomorrow at 9 AM"
- "next Monday at 2 PM"

### Specific Dates
- "on December 25 at 12 PM"
- "12/25/2025 at 3 PM"

## Time Zones

```python
# Get time in specific timezone
current = time_util.get_current_time(timezone='America/New_York')
print(f"Time in NY: {current['time']}")
```

Supported timezones: All Python `pytz` timezones

## Storage

Reminders stored in `ai_database.db` table:
- `reminder_id` - Auto-increment ID
- `user_id` - Discord user
- `guild_id` - Server context
- `message` - Reminder text
- `scheduled_time` - When to send
- `created_at` - Creation timestamp
- `sent` - Whether sent

## Performance

- **Parse time string**: < 100ms
- **Create reminder**: < 150ms
- **Get pending reminders**: < 200ms
- **Check all user reminders**: < 100ms

## Limitations

1. **Timezone handling** - Assumes server timezone by default
2. **Precision** - Checked every minute minimum
3. **Persistence** - Lost if bot crashes before sent

## Dependencies

- `ai_database` - Reminder storage
- `dateutil` - Date/time parsing
- Built-in `datetime` - Time operations
- Built-in `asyncio` - Async operations

## Related Documentation

- [Commands Reference](../commands.md#-time--reminder-commands) - Reminder commands
- [ai_database.md](./ai_database.md) - Storage details
- [Modules Overview](../MODULES.md) - Other modules

---

*Last Updated: 2025-11-14*
