"""
Server Actions module - Server management with tsundere attitude
"""
import discord
import re
from .persona_manager import PersonaManager
from .logger import BotLogger

# Initialize logger
logger = BotLogger.get_logger(__name__)

# Regex patterns for Discord mentions
USER_MENTION_REGEX = r'<@!?(\d+)>'
CHANNEL_MENTION_REGEX = r'<#(\d+)>'

class TsundereServerActions:
    def __init__(self, persona_file="persona_card.json"):
        self.persona_manager = PersonaManager(persona_file)
    
    def _parse_user_mention(self, ctx, user_mention):
        """Helper method to extract user ID from mention string and get member object"""
        if hasattr(user_mention, 'mention'):
            # It's a discord.Member object already
            return user_mention
        
        # It's a mention string, extract user ID
        user_id = re.findall(USER_MENTION_REGEX, user_mention)
        if not user_id:
            return None
        
        user = ctx.guild.get_member(int(user_id[0]))
        return user
    
    def _parse_channel_mention(self, ctx, channel_mention):
        """Helper method to extract channel ID from mention string and get channel object"""
        channel_id = re.findall(CHANNEL_MENTION_REGEX, channel_mention)
        if not channel_id:
            return None
        
        channel = ctx.guild.get_channel(int(channel_id[0]))
        return channel
    
    async def mention_user(self, ctx, user_mention, message=None):
        """Mention a user with a message"""
        try:
            user = self._parse_user_mention(ctx, user_mention)
            if not user:
                return self.persona_manager.get_response("missing_args")
            
            if message:
                response = f"{user.mention} {message}"
            else:
                # Default tsundere mention
                base_response = self.persona_manager.get_activity_response("server_actions", "success_mention")
                response = base_response.format(user=user.mention)
            
            return response
            
        except Exception as e:
            return self.persona_manager.format_error_response(e)
    
    async def create_role(self, ctx, role_name, color=None):
        """Create a new role"""
        try:
            if not ctx.author.guild_permissions.manage_roles:
                logger.warning(f"User {ctx.author.id} attempted to create role without permission")
                return self.persona_manager.get_activity_response("server_actions", "no_permission")
            
            logger.info(f"Creating role '{role_name}' in guild {ctx.guild.id}")
            
            # Parse color if provided
            role_color = discord.Color.default()
            if color:
                try:
                    if color.startswith('#'):
                        role_color = discord.Color(int(color[1:], 16))
                    else:
                        role_color = getattr(discord.Color, color.lower(), discord.Color.default)()
                except (ValueError, AttributeError):
                    pass  # Use default color if parsing fails
            
            role = await ctx.guild.create_role(name=role_name, color=role_color)
            logger.info(f"Role '{role_name}' created successfully")
            
            return self.persona_manager.get_activity_response("server_actions", "success_role_create", 
                                                            role_name=role.name)
            
        except discord.Forbidden:
            logger.error(f"Permission denied creating role in guild {ctx.guild.id}")
            return self.persona_manager.get_activity_response("server_actions", "no_permission")
        except Exception as e:
            logger.error(f"Error creating role: {e}")
            return self.persona_manager.format_error_response(e)
    
    async def give_role(self, ctx, user_mention, role_name):
        """Give a role to a user"""
        try:
            if not ctx.author.guild_permissions.manage_roles:
                logger.warning(f"User {ctx.author.id} attempted to give role without permission")
                return self.persona_manager.get_activity_response("server_actions", "no_permission")
            
            user = self._parse_user_mention(ctx, user_mention)
            if not user:
                logger.warning(f"Invalid user mention: {user_mention}")
                return self.persona_manager.get_response("missing_args")
            
            # Find role
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if not role:
                logger.warning(f"Role not found: {role_name}")
                return self.persona_manager.get_activity_response("server_actions", "role_not_found")
            
            if role in user.roles:
                logger.info(f"User {user.id} already has role {role.name}")
                return self.persona_manager.get_activity_response("server_actions", "already_has_role", 
                                                                user=user.display_name)
            
            await user.add_roles(role)
            logger.info(f"Role '{role.name}' given to user {user.id}")
            
            return self.persona_manager.get_activity_response("server_actions", "success_role_give", 
                                                            user=user.display_name, role=role.mention)
            
        except discord.Forbidden:
            logger.error(f"Permission denied giving role in guild {ctx.guild.id}")
            return self.persona_manager.get_activity_response("server_actions", "hierarchy_error")
        except Exception as e:
            logger.error(f"Error giving role: {e}")
            return self.persona_manager.format_error_response(e)
    
    async def remove_role(self, ctx, user_mention, role_name):
        """Remove a role from a user"""
        try:
            if not ctx.author.guild_permissions.manage_roles:
                logger.warning(f"User {ctx.author.id} attempted to remove role without permission")
                return self.persona_manager.get_activity_response("server_actions", "no_permission")
            
            user = self._parse_user_mention(ctx, user_mention)
            if not user:
                logger.warning(f"Invalid user mention: {user_mention}")
                return self.persona_manager.get_response("missing_args")
            
            # Find role
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if not role:
                logger.warning(f"Role not found: {role_name}")
                return self.persona_manager.get_activity_response("server_actions", "role_not_found")
            
            if role not in user.roles:
                logger.info(f"User {user.id} doesn't have role {role.name}")
                return self.persona_manager.get_activity_response("server_actions", "doesnt_have_role", 
                                                                user=user.display_name)
            
            await user.remove_roles(role)
            logger.info(f"Role '{role.name}' removed from user {user.id}")
            
            return self.persona_manager.get_activity_response("server_actions", "success_role_remove", 
                                                            user=user.display_name, role=role.mention)
            
        except discord.Forbidden:
            logger.error(f"Permission denied removing role in guild {ctx.guild.id}")
            return self.persona_manager.get_activity_response("server_actions", "hierarchy_error")
        except Exception as e:
            logger.error(f"Error removing role: {e}")
            return self.persona_manager.format_error_response(e)
    
    async def kick_user(self, ctx, user_mention, reason=None):
        """Kick a user from the server"""
        try:
            if not ctx.author.guild_permissions.kick_members:
                logger.warning(f"User {ctx.author.id} attempted to kick without permission")
                return self.persona_manager.get_activity_response("server_actions", "no_permission")
            
            user = self._parse_user_mention(ctx, user_mention)
            if not user:
                logger.warning(f"Invalid user mention: {user_mention}")
                return self.persona_manager.get_response("missing_args")
            
            if user == ctx.author:
                logger.warning(f"User {ctx.author.id} attempted to kick themselves")
                return self.persona_manager.get_activity_response("server_actions", "cant_kick_self")
            
            if user.top_role >= ctx.guild.me.top_role:
                logger.warning(f"Insufficient permissions to kick user {user.id}")
                return self.persona_manager.get_activity_response("server_actions", "hierarchy_error")
            
            kick_reason = reason or f"Kicked by {ctx.author.display_name} via tsundere bot"
            
            await user.kick(reason=kick_reason)
            logger.info(f"User {user.id} kicked from guild {ctx.guild.id}, reason: {kick_reason}")
            
            return self.persona_manager.get_activity_response("server_actions", "success_kick", 
                                                            user=user.display_name)
            
        except discord.Forbidden:
            logger.error(f"Permission denied kicking user in guild {ctx.guild.id}")
            return self.persona_manager.get_activity_response("server_actions", "hierarchy_error")
        except Exception as e:
            logger.error(f"Error kicking user: {e}")
            return self.persona_manager.format_error_response(e)
    
    async def create_channel(self, ctx, channel_name, channel_type="text"):
        """Create a new channel"""
        try:
            if not ctx.author.guild_permissions.manage_channels:
                logger.warning(f"User {ctx.author.id} attempted to create channel without permission")
                return self.persona_manager.get_activity_response("server_actions", "no_permission")
            
            logger.info(f"Creating {channel_type} channel '{channel_name}' in guild {ctx.guild.id}")
            
            if channel_type.lower() == "voice":
                channel = await ctx.guild.create_voice_channel(channel_name)
                channel_type_str = "voice channel"
            else:
                channel = await ctx.guild.create_text_channel(channel_name)
                channel_type_str = "text channel"
            
            logger.info(f"Channel '{channel_name}' created successfully")
            
            return self.persona_manager.get_activity_response("server_actions", "success_channel", 
                                                            type=channel_type_str, channel=channel.mention)
            
        except discord.Forbidden:
            logger.error(f"Permission denied creating channel in guild {ctx.guild.id}")
            return self.persona_manager.get_activity_response("server_actions", "no_permission")
        except Exception as e:
            logger.error(f"Error creating channel: {e}")
            return self.persona_manager.format_error_response(e)
    
    async def send_message_to_channel(self, ctx, channel_mention, message):
        """Send a message to a specific channel"""
        try:
            channel = self._parse_channel_mention(ctx, channel_mention)
            if not channel:
                logger.warning(f"Invalid channel mention: {channel_mention}")
                return self.persona_manager.get_response("missing_args")
            
            await channel.send(message)
            logger.info(f"Message sent to channel {channel.id}: {message[:50]}...")
            
            return self.persona_manager.get_activity_response("server_actions", "success_message", 
                                                            channel=channel.mention)
            
        except discord.Forbidden:
            logger.error(f"Permission denied sending message to channel")
            return self.persona_manager.get_activity_response("server_actions", "no_permission")
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return self.persona_manager.format_error_response(e)