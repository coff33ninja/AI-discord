"""
Server Actions module - Server management with tsundere attitude
"""
import discord
import re
from .persona_manager import PersonaManager

class TsundereServerActions:
    def __init__(self, persona_file="persona_card.json"):
        self.persona_manager = PersonaManager(persona_file)
    
    async def mention_user(self, ctx, user_mention, message=None):
        """Mention a user with a message"""
        try:
            # Handle both discord.Member objects and mention strings
            if hasattr(user_mention, 'mention'):
                # It's a discord.Member object
                user = user_mention
            else:
                # It's a mention string, extract user ID
                user_id = re.findall(r'<@!?(\d+)>', user_mention)
                if not user_id:
                    return self.persona_manager.get_response("missing_args")
                
                user = ctx.guild.get_member(int(user_id[0]))
                if not user:
                    return self.persona_manager.get_activity_response("server_actions", "user_not_found")
            
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
                return self.persona_manager.get_activity_response("server_actions", "no_permission")
            
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
            
            return self.persona_manager.get_activity_response("server_actions", "success_role_create", 
                                                            role_name=role.name)
            
        except discord.Forbidden:
            return self.persona_manager.get_activity_response("server_actions", "no_permission")
        except Exception as e:
            return self.persona_manager.format_error_response(e)
    
    async def give_role(self, ctx, user_mention, role_name):
        """Give a role to a user"""
        try:
            if not ctx.author.guild_permissions.manage_roles:
                return self.persona_manager.get_activity_response("server_actions", "no_permission")
            
            # Handle both discord.Member objects and mention strings
            if hasattr(user_mention, 'mention'):
                # It's a discord.Member object
                user = user_mention
            else:
                # It's a mention string, extract user ID
                user_id = re.findall(r'<@!?(\d+)>', user_mention)
                if not user_id:
                    return self.persona_manager.get_response("missing_args")
                
                user = ctx.guild.get_member(int(user_id[0]))
                if not user:
                    return self.persona_manager.get_activity_response("server_actions", "user_not_found")
            
            # Find role
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if not role:
                return self.persona_manager.get_activity_response("server_actions", "role_not_found")
            
            if role in user.roles:
                return self.persona_manager.get_activity_response("server_actions", "already_has_role", 
                                                                user=user.display_name)
            
            await user.add_roles(role)
            
            return self.persona_manager.get_activity_response("server_actions", "success_role_give", 
                                                            user=user.display_name, role=role.mention)
            
        except discord.Forbidden:
            return self.persona_manager.get_activity_response("server_actions", "hierarchy_error")
        except Exception as e:
            return self.persona_manager.format_error_response(e)
    
    async def remove_role(self, ctx, user_mention, role_name):
        """Remove a role from a user"""
        try:
            if not ctx.author.guild_permissions.manage_roles:
                return self.persona_manager.get_activity_response("server_actions", "no_permission")
            
            # Handle both discord.Member objects and mention strings
            if hasattr(user_mention, 'mention'):
                # It's a discord.Member object
                user = user_mention
            else:
                # It's a mention string, extract user ID
                user_id = re.findall(r'<@!?(\d+)>', user_mention)
                if not user_id:
                    return self.persona_manager.get_response("missing_args")
                
                user = ctx.guild.get_member(int(user_id[0]))
                if not user:
                    return self.persona_manager.get_activity_response("server_actions", "user_not_found")
            
            # Find role
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if not role:
                return self.persona_manager.get_activity_response("server_actions", "role_not_found")
            
            if role not in user.roles:
                return self.persona_manager.get_activity_response("server_actions", "doesnt_have_role", 
                                                                user=user.display_name)
            
            await user.remove_roles(role)
            
            return self.persona_manager.get_activity_response("server_actions", "success_role_remove", 
                                                            user=user.display_name, role=role.mention)
            
        except discord.Forbidden:
            return self.persona_manager.get_activity_response("server_actions", "hierarchy_error")
        except Exception as e:
            return self.persona_manager.format_error_response(e)
    
    async def kick_user(self, ctx, user_mention, reason=None):
        """Kick a user from the server"""
        try:
            if not ctx.author.guild_permissions.kick_members:
                return self.persona_manager.get_activity_response("server_actions", "no_permission")
            
            # Handle both discord.Member objects and mention strings
            if hasattr(user_mention, 'mention'):
                # It's a discord.Member object
                user = user_mention
            else:
                # It's a mention string, extract user ID
                user_id = re.findall(r'<@!?(\d+)>', user_mention)
                if not user_id:
                    return self.persona_manager.get_response("missing_args")
                
                user = ctx.guild.get_member(int(user_id[0]))
                if not user:
                    return self.persona_manager.get_activity_response("server_actions", "user_not_found")
            
            if user == ctx.author:
                return self.persona_manager.get_activity_response("server_actions", "cant_kick_self")
            
            if user.top_role >= ctx.guild.me.top_role:
                return self.persona_manager.get_activity_response("server_actions", "hierarchy_error")
            
            kick_reason = reason or f"Kicked by {ctx.author.display_name} via tsundere bot"
            
            await user.kick(reason=kick_reason)
            
            return self.persona_manager.get_activity_response("server_actions", "success_kick", 
                                                            user=user.display_name)
            
        except discord.Forbidden:
            return self.persona_manager.get_activity_response("server_actions", "hierarchy_error")
        except Exception as e:
            return self.persona_manager.format_error_response(e)
    
    async def create_channel(self, ctx, channel_name, channel_type="text"):
        """Create a new channel"""
        try:
            if not ctx.author.guild_permissions.manage_channels:
                return self.persona_manager.get_activity_response("server_actions", "no_permission")
            
            if channel_type.lower() == "voice":
                channel = await ctx.guild.create_voice_channel(channel_name)
                channel_type_str = "voice channel"
            else:
                channel = await ctx.guild.create_text_channel(channel_name)
                channel_type_str = "text channel"
            
            return self.persona_manager.get_activity_response("server_actions", "success_channel", 
                                                            type=channel_type_str, channel=channel.mention)
            
        except discord.Forbidden:
            return self.persona_manager.get_activity_response("server_actions", "no_permission")
        except Exception as e:
            return self.persona_manager.format_error_response(e)
    
    async def send_message_to_channel(self, ctx, channel_mention, message):
        """Send a message to a specific channel"""
        try:
            # Extract channel ID from mention
            channel_id = re.findall(r'<#(\d+)>', channel_mention)
            if not channel_id:
                return self.persona_manager.get_response("missing_args")
            
            channel = ctx.guild.get_channel(int(channel_id[0]))
            if not channel:
                return self.persona_manager.get_activity_response("server_actions", "channel_not_found")
            
            await channel.send(message)
            
            return self.persona_manager.get_activity_response("server_actions", "success_message", 
                                                            channel=channel.mention)
            
        except discord.Forbidden:
            return self.persona_manager.get_activity_response("server_actions", "no_permission")
        except Exception as e:
            return self.persona_manager.format_error_response(e)