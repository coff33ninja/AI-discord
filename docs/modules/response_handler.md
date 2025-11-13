# response_handler Module

Discord embed and message formatting utilities for creating rich, formatted responses with consistent styling.

## Overview

The `response_handler` module provides:
- Rich embed creation
- Message formatting utilities
- Embed templates
- Color management
- Field organization
- Error message formatting

## Key Classes

### ResponseHandler

Static class for creating formatted responses.

```python
from modules.response_handler import ResponseHandler

# Create info embed
embed = ResponseHandler.create_info_embed(
    title="Help",
    description="How to use commands",
    fields=[
        {'name': 'Command', 'value': '!ai', 'inline': False}
    ]
)

await ctx.send(embed=embed)
```

## Main Functions

### `create_info_embed(title, description, fields=None, footer_text=None, color=None)`
Create informational embed.

**Parameters:**
- `title` (str) - Embed title
- `description` (str) - Main description
- `fields` (list) - Field list with name/value/inline
- `footer_text` (str) - Footer text
- `color` (int) - Embed color

**Returns:** discord.Embed

**Example:**
```python
embed = ResponseHandler.create_info_embed(
    title="Commands",
    description="Available commands:",
    fields=[
        {'name': '!ai', 'value': 'Ask AI', 'inline': True},
        {'name': '!search', 'value': 'Search web', 'inline': True}
    ]
)
```

### `create_success_embed(title, description, fields=None)`
Create success (green) embed.

**Parameters:**
- `title` (str) - Embed title
- `description` (str) - Main description
- `fields` (list) - Field list

**Returns:** discord.Embed (green color)

**Example:**
```python
embed = ResponseHandler.create_success_embed(
    title="Success",
    description="Command completed successfully"
)
```

### `create_error_embed(title, description, error_detail=None)`
Create error (red) embed.

**Parameters:**
- `title` (str) - Error title
- `description` (str) - Error description
- `error_detail` (str) - Technical details

**Returns:** discord.Embed (red color)

**Example:**
```python
embed = ResponseHandler.create_error_embed(
    title="Command Error",
    description="Invalid parameters",
    error_detail=str(error)
)
```

### `create_warning_embed(title, description)`
Create warning (yellow) embed.

**Parameters:**
- `title` (str) - Warning title
- `description` (str) - Warning message

**Returns:** discord.Embed (yellow color)

**Example:**
```python
embed = ResponseHandler.create_warning_embed(
    title="Warning",
    description="This action is irreversible"
)
```

### `format_field(name, value, inline=False)`
Create formatted field dict.

**Parameters:**
- `name` (str) - Field name
- `value` (str) - Field value
- `inline` (bool) - Inline with other fields

**Returns:** dict

**Example:**
```python
field = ResponseHandler.format_field(
    "User",
    "John#1234",
    inline=True
)
```

### `create_table_embed(title, headers, rows, color=None)`
Create embed with table format.

**Parameters:**
- `title` (str) - Embed title
- `headers` (list) - Column headers
- `rows` (list) - Data rows
- `color` (int) - Embed color

**Returns:** discord.Embed

**Example:**
```python
embed = ResponseHandler.create_table_embed(
    title="Stats",
    headers=["Stat", "Value"],
    rows=[
        ["Games", "10"],
        ["Wins", "7"],
        ["Win Rate", "70%"]
    ]
)
```

## Color Codes

Pre-defined colors:
- `SUCCESS` - Green (0x00FF00)
- `ERROR` - Red (0xFF0000)
- `WARNING` - Yellow (0xFFFF00)
- `INFO` - Blue (0x0000FF)
- `NEUTRAL` - Gray (0x808080)

## Embed Templates

### Info Embed
```python
embed = ResponseHandler.create_info_embed(
    title="Information",
    description="Description here",
    fields=[...],
    footer_text="Footer"
)
```

### Success Embed
```python
embed = ResponseHandler.create_success_embed(
    title="Success!",
    description="Action completed"
)
```

### Error Embed
```python
embed = ResponseHandler.create_error_embed(
    title="Error",
    description="Something went wrong",
    error_detail="Technical error info"
)
```

### Warning Embed
```python
embed = ResponseHandler.create_warning_embed(
    title="Warning",
    description="Be careful!"
)
```

## Usage Examples

### Command Help

```python
embed = ResponseHandler.create_info_embed(
    title="!ai Command",
    description="Ask the bot anything",
    fields=[
        {'name': 'Usage', 'value': '!ai <question>', 'inline': False},
        {'name': 'Example', 'value': '!ai What is AI?', 'inline': False},
        {'name': 'Alias', 'value': '!ask, !chat', 'inline': True}
    ],
    footer_text="Use !help_ai for all commands"
)

await ctx.send(embed=embed)
```

### User Stats

```python
embed = ResponseHandler.create_table_embed(
    title=f"{member.name}'s Statistics",
    headers=["Metric", "Value"],
    rows=[
        ["Messages", "142"],
        ["Commands", "23"],
        ["Games", "5"],
        ["Relationship", "Friend"]
    ]
)

await ctx.send(embed=embed)
```

### Command Response

```python
try:
    # Do something
    result = await some_operation()
    
    embed = ResponseHandler.create_success_embed(
        title="Operation Complete",
        description=f"Result: {result}"
    )
except Exception as e:
    embed = ResponseHandler.create_error_embed(
        title="Operation Failed",
        description="An error occurred",
        error_detail=str(e)
    )

await ctx.send(embed=embed)
```

### Confirmation Message

```python
embed = ResponseHandler.create_warning_embed(
    title="Confirm Action",
    description="This action cannot be undone. React to confirm."
)

msg = await ctx.send(embed=embed)
await msg.add_reaction("✅")
await msg.add_reaction("❌")
```

## Field Organization

Fields can be organized as columns:
```python
fields = [
    ResponseHandler.format_field("Command", "!ai", inline=True),
    ResponseHandler.format_field("Use", "Ask AI", inline=True),
    ResponseHandler.format_field("Alias", "!ask", inline=True),
]

embed = ResponseHandler.create_info_embed(
    title="Commands",
    description="All commands",
    fields=fields
)
```

## Message Formatting

### Text Formatting
- **Bold**: `**text**`
- *Italic*: `*text*`
- ***Bold Italic***: `***text***`
- `Code`: `` `code` ``
- Code Block:
  ```python
  ```python
  code here
  ```
  ```

### Embed Text Formatting

Supports Discord markdown:
```python
description = "**Bold** and *italic* text\n`inline code`"
```

## Best Practices

1. **Use consistent colors** - Info=Blue, Success=Green, Error=Red, Warning=Yellow
2. **Keep descriptions short** - Embeds have character limits
3. **Use fields for structure** - Better readability
4. **Add footer** - Helps with context
5. **Use timestamps** - Shows when created

## Performance

- **Embed creation**: < 10ms
- **Field formatting**: < 1ms
- **Embed sending**: ~0.5 seconds

## Limitations

1. **Character limits** - Description 2048 chars, field value 1024 chars
2. **Field limits** - Max 25 fields per embed
3. **Color format** - Must be integer (0xRRGGBB)
4. **Formatting** - Limited to Discord markdown

## Dependencies

- `discord.py` - Discord API and embeds

## Related Documentation

- [Commands Reference](../commands.md) - Commands using embeds
- [Modules Overview](../MODULES.md) - Other modules

---

*Last Updated: 2025-11-14*
