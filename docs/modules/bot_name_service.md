# bot_name_service Module

Bot name resolution service for handling and managing the bot's display name across different contexts and servers.

## Overview

The `bot_name_service` module handles:
- Bot name resolution
- Context-aware name usage
- Name customization per server
- Server nicknames
- Global name management
- Name caching
- Display name formatting

## Key Classes

### BotNameService

Singleton service for name management.

```python
from modules.bot_name_service import BotNameService, get_name_service

# Get singleton instance
name_service = get_name_service()

# Get bot name
name = name_service.get_name()

# Get context-aware name
server_name = name_service.get_name_for_server(guild_id)

# Set server nickname
await name_service.set_server_name(guild_id, "CustomName")
```

## Main Functions

### `get_name()`

Get bot's global name.

**Returns:** str - Bot name

**Example:**
```python
name = name_service.get_name()
print(f"I am {name}")  # "I am Akeno"
```

### `get_name_for_server(guild_id)`

Get name customized for server.

**Parameters:**
- `guild_id` (int) - Discord server ID

**Returns:** str - Server-specific name or global name

**Example:**
```python
guild_id = ctx.guild.id
server_name = name_service.get_name_for_server(guild_id)
```

### `set_server_name(guild_id, name)`

Set custom name for server.

**Parameters:**
- `guild_id` (int) - Discord server ID
- `name` (str) - Custom name

**Returns:** bool - Success

**Example:**
```python
success = await name_service.set_server_name(guild_id, "LocalAkeno")
```

### `get_formatted_name(ctx, style="default")`

Get formatted name for display.

**Parameters:**
- `ctx` (discord.Context) - Command context
- `style` (str) - Format style ("default", "mention", "title")

**Returns:** str - Formatted name

**Example:**
```python
name = name_service.get_formatted_name(ctx, style="title")
await ctx.send(f"Greetings, I am {name}")
```

### `clear_server_name(guild_id)`

Remove server-specific name.

**Parameters:**
- `guild_id` (int) - Discord server ID

**Returns:** bool - Success

**Example:**
```python
await name_service.clear_server_name(guild_id)
```

### `get_all_server_names()`

Get all server-specific names.

**Returns:** dict - {guild_id: name}

**Example:**
```python
server_names = name_service.get_all_server_names()
for guild_id, name in server_names.items():
    print(f"Guild {guild_id}: {name}")
```

### `update_nickname(member)`

Update bot's nickname in server.

**Parameters:**
- `member` (discord.Member) - Bot member object

**Returns:** bool - Success

**Example:**
```python
bot_member = ctx.guild.me
await name_service.update_nickname(bot_member)
```

## Display Styles

| Style | Format | Example |
|-------|--------|---------|
| **default** | Plain name | "Akeno" |
| **title** | Title case | "Akeno" |
| **mention** | With indicator | "🤖 Akeno" |
| **formal** | Formal address | "Ms. Akeno" |
| **casual** | Casual address | "Hey, it's Akeno" |

## Usage Examples

### Get Bot Name in Response

```python
name_service = get_name_service()

@bot.command()
async def hello(ctx):
    name = name_service.get_name()
    await ctx.send(f"Hello! I'm {name}")
```

### Use Server-Specific Names

```python
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # Use server-specific name if set
    name = name_service.get_name_for_server(message.guild.id)
    
    response = await get_response(message.content, name)
    await message.reply(response)
```

### Customize Name Per Server

```python
@bot.command()
@commands.has_permissions(administrator=True)
async def set_bot_name(ctx, new_name: str):
    if len(new_name) > 32:
        await ctx.send("Name too long (max 32 chars)")
        return
    
    success = await name_service.set_server_name(ctx.guild.id, new_name)
    
    if success:
        await ctx.send(f"✅ Changed name to {new_name}")
    else:
        await ctx.send("❌ Failed to change name")
```

### Reset to Global Name

```python
@bot.command()
@commands.has_permissions(administrator=True)
async def reset_bot_name(ctx):
    await name_service.clear_server_name(ctx.guild.id)
    
    global_name = name_service.get_name()
    await ctx.send(f"Reset name to {global_name}")
```

### Show Current Identity

```python
@bot.command()
async def whoami(ctx):
    # Get name for this server
    name = name_service.get_name_for_server(ctx.guild.id)
    
    # Get formatted version
    formatted = name_service.get_formatted_name(ctx, style="title")
    
    embed = discord.Embed(
        title="Identity",
        description=f"I am {formatted}",
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="Server Name",
        value=name,
        inline=False
    )
    
    embed.add_field(
        name="Global Name",
        value=name_service.get_name(),
        inline=False
    )
    
    await ctx.send(embed=embed)
```

### Sync Discord Nickname

```python
@bot.event
async def on_ready():
    name_service = get_name_service()
    
    for guild in bot.guilds:
        member = guild.me
        name = name_service.get_name_for_server(guild.id)
        
        try:
            await name_service.update_nickname(member)
            print(f"Updated nickname in {guild.name}")
        except Exception as e:
            print(f"Failed to update in {guild.name}: {e}")
```

### List All Names

```python
@bot.command()
@commands.is_owner()
async def list_names(ctx):
    global_name = name_service.get_name()
    server_names = name_service.get_all_server_names()
    
    embed = discord.Embed(
        title="Bot Names",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="Global Name",
        value=global_name,
        inline=False
    )
    
    if server_names:
        names_str = "\n".join(
            f"{bot.get_guild(gid).name}: {name}"
            for gid, name in server_names.items()
        )
        embed.add_field(
            name="Server Names",
            value=names_str,
            inline=False
        )
    else:
        embed.add_field(
            name="Server Names",
            value="None set",
            inline=False
        )
    
    await ctx.send(embed=embed)
```

## Name Resolution Order

When getting name:

1. **Check server-specific** - Is there a custom name?
2. **Check cache** - Is it cached?
3. **Get global** - Use default global name
4. **Cache result** - Store for next time

## Storage

Server names are stored in database:

```sql
CREATE TABLE server_names (
    guild_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    set_by INTEGER,
    set_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Performance

- **Get global name**: < 1ms
- **Get server name**: ~5ms (cached)
- **Set server name**: ~20ms
- **Update nickname**: ~500ms (Discord API)

## Limitations

1. **Discord limit**: 32 character max
2. **Rate limit**: Can't change too frequently
3. **Permissions**: Bot needs permission to change nickname
4. **Server scope**: Names are per-server only

## Best Practices

1. **Keep names short** - Easier to remember
2. **Make sense** - Use recognizable names
3. **Avoid duplicates** - Clear what the name is
4. **Update display** - Use current name in responses
5. **Check permissions** - Verify bot can change nickname

## Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| Name too long | Limit to 32 characters |
| Can't update nickname | Check bot permissions in server |
| Name not changing | Call update_nickname() after set |
| Changes not persisting | Ensure database save completed |

## Dependencies

- **ai_database.py** - Database storage
- Built-in `asyncio` - Async operations

## Related Documentation

- [persona_manager.py](./persona_manager.md) - Personality management
- [ai_database.py](./ai_database.md) - Database operations
- [Modules Overview](../MODULES.md) - Other modules

---

*Last Updated: 2025-11-14*
