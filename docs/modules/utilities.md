# utilities Module

General utility functions for text processing, formatting, data manipulation, and common helper operations used throughout the bot.

## Overview

The `utilities` module provides:
- Text formatting and cleaning
- String manipulation
- Data validation
- Common helper functions
- Parsing utilities
- Formatting decorators
- Error handling utilities

## Main Functions

### Text Processing

#### `clean_text(text)`

Remove markdown, formatting, and special characters.

**Parameters:**
- `text` (str) - Text to clean

**Returns:** str - Cleaned text

**Example:**
```python
from modules.utilities import clean_text

text = "**Hello** _world_ `code`"
clean = clean_text(text)  # "Hello world code"
```

#### `truncate(text, max_length, suffix="...")`

Truncate text to maximum length.

**Parameters:**
- `text` (str) - Text to truncate
- `max_length` (int) - Maximum length
- `suffix` (str) - Suffix if truncated

**Returns:** str - Truncated text

**Example:**
```python
text = "This is a very long message"
short = truncate(text, 15)  # "This is a ve..."
```

#### `remove_mentions(text)`

Remove @mentions from text.

**Parameters:**
- `text` (str) - Text to process

**Returns:** str - Text without mentions

**Example:**
```python
text = "Hello @John and @Jane"
clean = remove_mentions(text)  # "Hello and"
```

#### `add_prefix(text, prefix)`

Add prefix to text.

**Parameters:**
- `text` (str) - Text to prefix
- `prefix` (str) - Prefix to add

**Returns:** str - Prefixed text

**Example:**
```python
text = "Error occurred"
msg = add_prefix(text, "❌")  # "❌ Error occurred"
```

### Data Validation

#### `is_valid_url(url)`

Check if string is valid URL.

**Parameters:**
- `url` (str) - String to check

**Returns:** bool

**Example:**
```python
is_valid = is_valid_url("https://example.com")  # True
```

#### `is_valid_email(email)`

Check if string is valid email.

**Parameters:**
- `email` (str) - Email to check

**Returns:** bool

**Example:**
```python
is_valid = is_valid_email("user@example.com")  # True
```

#### `is_number(text, allow_float=False)`

Check if text is number.

**Parameters:**
- `text` (str) - Text to check
- `allow_float` (bool) - Allow floats

**Returns:** bool

**Example:**
```python
is_number("42")  # True
is_number("3.14", allow_float=True)  # True
```

### Formatting

#### `format_time(seconds)`

Format seconds to human-readable time.

**Parameters:**
- `seconds` (int/float) - Seconds

**Returns:** str - Formatted time

**Example:**
```python
formatted = format_time(3661)  # "1h 1m 1s"
```

#### `format_bytes(bytes_size)`

Format bytes to human-readable size.

**Parameters:**
- `bytes_size` (int) - Bytes

**Returns:** str - Formatted size

**Example:**
```python
size = format_bytes(1024000)  # "1000 KB"
```

#### `pluralize(word, count)`

Pluralize word if count != 1.

**Parameters:**
- `word` (str) - Word to pluralize
- `count` (int) - Count

**Returns:** str - Pluralized word

**Example:**
```python
text = f"Found {count} {pluralize('apple', count)}"
# "Found 5 apples"
```

#### `format_list(items, style="bullet")`

Format list for display.

**Parameters:**
- `items` (list) - Items to format
- `style` (str) - "bullet", "number", "comma"

**Returns:** str - Formatted list

**Example:**
```python
items = ["Python", "Discord.py", "SQLite"]

# Bullet style
formatted = format_list(items, "bullet")
# "• Python\n• Discord.py\n• SQLite"

# Comma style
formatted = format_list(items, "comma")
# "Python, Discord.py, and SQLite"
```

### Number Handling

#### `clamp(value, min_val, max_val)`

Clamp value between min and max.

**Parameters:**
- `value` (int/float) - Value to clamp
- `min_val` (int/float) - Minimum
- `max_val` (int/float) - Maximum

**Returns:** int/float - Clamped value

**Example:**
```python
clamped = clamp(150, 0, 100)  # 100
```

#### `percentage(value, total)`

Calculate percentage.

**Parameters:**
- `value` (int/float) - Value
- `total` (int/float) - Total

**Returns:** float - Percentage

**Example:**
```python
pct = percentage(25, 100)  # 25.0
```

#### `is_between(value, min_val, max_val)`

Check if value is between min and max.

**Parameters:**
- `value` (int/float) - Value
- `min_val` (int/float) - Minimum
- `max_val` (int/float) - Maximum

**Returns:** bool

**Example:**
```python
in_range = is_between(50, 0, 100)  # True
```

### Dictionary Utilities

#### `safe_get(dictionary, path, default=None)`

Safely get nested dictionary value.

**Parameters:**
- `dictionary` (dict) - Dictionary
- `path` (str) - Path with dots (e.g., "user.name.first")
- `default` (any) - Default value

**Returns:** any - Value or default

**Example:**
```python
data = {"user": {"name": {"first": "John"}}}
name = safe_get(data, "user.name.first")  # "John"
missing = safe_get(data, "user.age", 0)  # 0
```

#### `merge_dicts(dict1, dict2)`

Merge two dictionaries.

**Parameters:**
- `dict1` (dict) - Base dictionary
- `dict2` (dict) - Dictionary to merge

**Returns:** dict - Merged dictionary

**Example:**
```python
config1 = {"debug": True, "port": 8000}
config2 = {"port": 9000}
merged = merge_dicts(config1, config2)
# {"debug": True, "port": 9000}
```

## Usage Examples

### Clean User Input

```python
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    from modules.utilities import clean_text, remove_mentions
    
    # Clean and process message
    text = clean_text(message.content)
    text = remove_mentions(text)
    
    # Now safe to process
    response = await process_user_input(text)
```

### Format Response with Utilities

```python
from modules.utilities import truncate, format_list

# Truncate long text
description = "Long text..."
short_desc = truncate(description, 100)

# Format list
items = ["Feature 1", "Feature 2", "Feature 3"]
formatted = format_list(items, "bullet")

embed = discord.Embed(
    title="Features",
    description=short_desc
)

embed.add_field(
    name="Available",
    value=formatted,
    inline=False
)
```

### Validate Input

```python
from modules.utilities import is_valid_email, is_valid_url

@bot.command()
async def register(ctx, email: str):
    if not is_valid_email(email):
        await ctx.send("Invalid email format!")
        return
    
    # Process registration
    await ctx.send(f"Registered {email}")
```

### Calculate and Display Statistics

```python
from modules.utilities import format_time, format_bytes, percentage

# Display stats
uptime_seconds = 123456
uptime_str = format_time(uptime_seconds)

used_bytes = 512000000
used_str = format_bytes(used_bytes)

usage_pct = percentage(512000000, 1000000000)

await ctx.send(f"""
📊 **Statistics**
Uptime: {uptime_str}
Memory: {used_str} ({usage_pct:.1f}%)
""")
```

### Safe Data Access

```python
from modules.utilities import safe_get, merge_dicts

# Safely access nested data
user_data = {
    "profile": {
        "info": {
            "name": "John",
            "age": 25
        }
    }
}

name = safe_get(user_data, "profile.info.name")
city = safe_get(user_data, "profile.location.city", "Unknown")

# Merge configurations
default_config = {"debug": False, "timeout": 30}
user_config = {"debug": True}
final_config = merge_dicts(default_config, user_config)
```

### Format Time Display

```python
from modules.utilities import format_time, pluralize

@bot.command()
async def uptime(ctx):
    # Calculate uptime
    start_time = bot.start_time
    uptime = datetime.now() - start_time
    uptime_seconds = uptime.total_seconds()
    
    # Format nicely
    uptime_str = format_time(int(uptime_seconds))
    
    await ctx.send(f"Bot has been running for {uptime_str}")
```

### Clamp Values

```python
from modules.utilities import clamp

# Ensure mood stays 0-100
mood = clamp(personality.mood + change, 0, 100)

# Ensure level between 1-100
level = clamp(user_level + bonus, 1, 100)
```

## Performance

- **Text cleaning**: ~5ms
- **Validation checks**: ~1ms
- **Formatting**: ~2ms
- **Dictionary access**: ~1ms
- **Clamping/math**: < 1ms

## Dependencies

- Built-in `re` - Regex operations
- Built-in `urllib.parse` - URL validation
- Built-in `math` - Math operations

## Related Documentation

- [response_handler.py](./response_handler.md) - Message formatting
- [logger.py](./logger.md) - Logging utilities
- [Modules Overview](../MODULES.md) - Other modules

---

*Last Updated: 2025-11-14*
