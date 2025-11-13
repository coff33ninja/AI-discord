# server_actions Module

Server management operations including role creation/management, channel operations, and user moderation.

## Overview

The `server_actions` module provides:
- Role creation and assignment
- Role removal and management
- Channel creation (text and voice)
- User kicking/banning
- Message relay between channels
- User mention with messaging
- Permission validation

## Key Classes

### ServerActionsManager

Main class for server operations.

```python
from modules.server_actions import ServerActionsManager, get_server_actions

# Get singleton instance
server = get_server_actions()

# Create role
role = await server.create_role(guild, "Member", color="blue")

# Assign role to user
await server.give_role(member, role)

# Create channel
channel = await server.create_channel(guild, "general", "text")
```

## Role Management

### `create_role(guild, role_name, color=None, permissions=None)`
Create a new Discord role.

**Parameters:**
- `guild` (discord.Guild) - Discord guild
- `role_name` (str) - Name of role
- `color` (str or int) - Color (e.g., "blue", 0xFF0000)
- `permissions` (discord.Permissions) - Role permissions

**Returns:** discord.Role - Created role

**Example:**
```python
role = await server.create_role(
    guild,
    "Moderator",
    color="red"
)
print(f"Created role: {role.name}")
```

### `give_role(member, role)`
Assign role to user.

**Parameters:**
- `member` (discord.Member) - Guild member
- `role` (discord.Role) - Role to assign

**Returns:** bool - Success

**Example:**
```python
success = await server.give_role(member, role)
if success:
    await ctx.send(f"Gave {member.name} the {role.name} role")
```

### `remove_role(member, role)`
Remove role from user.

**Parameters:**
- `member` (discord.Member) - Guild member
- `role` (discord.Role) - Role to remove

**Returns:** bool - Success

**Example:**
```python
success = await server.remove_role(member, role)
if success:
    await ctx.send(f"Removed {role.name} from {member.name}")
```

## Channel Management

### `create_channel(guild, channel_name, channel_type='text')`
Create a new channel.

**Parameters:**
- `guild` (discord.Guild) - Discord guild
- `channel_name` (str) - Channel name
- `channel_type` (str) - "text" or "voice"

**Returns:** discord.TextChannel or discord.VoiceChannel

**Example:**
```python
channel = await server.create_channel(
    guild,
    "announcements",
    "text"
)
print(f"Created channel: {channel.name}")
```

### `send_to_channel(channel, message)`
Send message to specific channel.

**Parameters:**
- `channel` (discord.TextChannel) - Target channel
- `message` (str) - Message text

**Returns:** discord.Message - Sent message

**Example:**
```python
msg = await server.send_to_channel(channel, "Hello everyone!")
print(f"Message sent: {msg.jump_url}")
```

## User Management

### `kick_user(member, reason=None)`
Kick user from server.

**Parameters:**
- `member` (discord.Member) - Member to kick
- `reason` (str) - Kick reason (optional)

**Returns:** bool - Success

**Example:**
```python
success = await server.kick_user(member, "Spam")
if success:
    await ctx.send(f"{member.name} has been kicked")
```

### `ban_user(guild, user_id, reason=None)`
Ban user from server.

**Parameters:**
- `guild` (discord.Guild) - Discord guild
- `user_id` (int) - User ID
- `reason` (str) - Ban reason (optional)

**Returns:** bool - Success

**Example:**
```python
success = await server.ban_user(guild, member.id, "Spam and harassment")
if success:
    await ctx.send(f"User has been banned")
```

### `mention_user(user, message=None)`
Mention a user with optional message.

**Parameters:**
- `user` (discord.Member) - User to mention
- `message` (str) - Optional message

**Returns:** str - Mention string

**Example:**
```python
mention = await server.mention_user(member, "You've been mentioned!")
await ctx.send(mention)
```

## Permission Checks

### `check_permissions(member, permission_name)`
Check if user has specific permission.

**Parameters:**
- `member` (discord.Member) - Member to check
- `permission_name` (str) - Permission name

**Returns:** bool - Has permission

**Permissions:**
- "administrator"
- "manage_roles"
- "manage_channels"
- "kick_members"
- "ban_members"
- etc.

**Example:**
```python
has_perm = server.check_permissions(member, "manage_roles")
if has_perm:
    # Can manage roles
else:
    await ctx.send("You don't have permission to manage roles")
```

## Usage Examples

### Create Role and Assign

```python
server = get_server_actions()

# Create role
role = await server.create_role(
    ctx.guild,
    "VIP Member",
    color="gold"
)

# Give to user
await server.give_role(ctx.author, role)

await ctx.send(f"You are now a VIP Member!")
```

### Setup Server Channels

```python
server = get_server_actions()

channels = ["announcements", "general", "help", "off-topic"]

for ch_name in channels:
    channel = await server.create_channel(
        ctx.guild,
        ch_name,
        "text"
    )
    print(f"Created {channel.name}")

await ctx.send("✅ Server channels created!")
```

### Moderation Command

```python
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    server = get_server_actions()
    
    success = await server.kick_user(member, reason)
    if success:
        await ctx.send(f"✅ {member.name} has been kicked")
        
        # Log to mod channel
        if mod_channel := discord.utils.get(ctx.guild.channels, name="mod-log"):
            await server.send_to_channel(
                mod_channel,
                f"**Kick:** {member.name}\n**Reason:** {reason}"
            )
```

### Role Management System

```python
server = get_server_actions()

# Create roles
roles_to_create = {
    "Member": "blue",
    "Moderator": "orange",
    "Admin": "red"
}

for role_name, color in roles_to_create.items():
    await server.create_role(ctx.guild, role_name, color)

# Assign based on interaction
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name="Member")
    await server.give_role(member, role)
```

### Message Relay

```python
server = get_server_actions()

# Announce in all channels
announcement = "Server maintenance in 1 hour!"

for channel in guild.text_channels:
    if channel.permissions_for(guild.me).send_messages:
        await server.send_to_channel(channel, announcement)
```

## Permissions Required

The bot needs these permissions in the server:

- **Manage Roles** - For role creation/assignment
- **Manage Channels** - For channel creation
- **Kick Members** - For kicking users
- **Ban Members** - For banning users
- **Send Messages** - For message relay

## Error Handling

```python
try:
    role = await server.create_role(guild, "Member")
except discord.Forbidden:
    await ctx.send("❌ I don't have permission to create roles")
except discord.HTTPException as e:
    await ctx.send(f"❌ Error: {e}")
```

## Performance

- **Create role**: ~1-2 seconds
- **Assign role**: ~0.5-1 seconds
- **Create channel**: ~1-2 seconds
- **Send message**: ~0.5 seconds
- **Permission check**: < 50ms

## Limitations

1. **Role hierarchy** - Can't manage roles above bot's highest role
2. **Permissions** - Respects Discord permission hierarchy
3. **Rate limits** - Discord API rate limits apply
4. **Moderation** - Limited to Discord's native capabilities

## Dependencies

- `discord.py` - Discord API
- Built-in `asyncio` - Async operations

## Related Documentation

- [Commands Reference](../commands.md#--server-management-commands) - Server commands
- [Modules Overview](../MODULES.md) - Other modules
- [Discord.py Docs](https://discordpy.readthedocs.io/) - Discord.py reference

---

*Last Updated: 2025-11-14*
