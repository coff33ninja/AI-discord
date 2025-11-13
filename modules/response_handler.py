"""
Response Handler - Centralized response formatting and sending
"""
import discord
from typing import Optional, List, Dict, Any

# Response Configuration Constants
MAX_EMBED_DESCRIPTION = 4096
MAX_EMBED_FIELD_VALUE = 1024
MAX_EMBED_FIELDS = 25
DEFAULT_EMBED_COLOR = 0x9C27B0  # Purple
SUCCESS_COLOR = 0x4CAF50  # Green
ERROR_COLOR = 0xF44336  # Red
WARNING_COLOR = 0xFF9800  # Orange
INFO_COLOR = 0x2196F3  # Blue

class ResponseHandler:
    """Handles formatted responses and embeds for bot messages"""
    
    @staticmethod
    def create_embed(
        title: str,
        description: str = "",
        color: int = DEFAULT_EMBED_COLOR,
        fields: Optional[List[Dict[str, Any]]] = None,
        thumbnail_url: Optional[str] = None,
        image_url: Optional[str] = None,
        footer_text: Optional[str] = None,
        author_name: Optional[str] = None,
        author_url: Optional[str] = None
    ) -> discord.Embed:
        """
        Create a formatted Discord embed
        
        Args:
            title: Embed title
            description: Embed description
            color: Embed color (default purple)
            fields: List of dicts with 'name', 'value', 'inline' keys
            thumbnail_url: URL for thumbnail image
            image_url: URL for main image
            footer_text: Footer text
            author_name: Author name
            author_url: Author URL
            
        Returns:
            discord.Embed: Formatted embed object
        """
        # Truncate description if too long
        if len(description) > MAX_EMBED_DESCRIPTION:
            description = description[:MAX_EMBED_DESCRIPTION-3] + "..."
        
        embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )
        
        # Add fields
        if fields:
            for field in fields[:MAX_EMBED_FIELDS]:  # Limit to 25 fields
                name = field.get('name', 'Unnamed')
                value = field.get('value', '')
                inline = field.get('inline', True)
                
                # Truncate field value if too long
                if len(value) > MAX_EMBED_FIELD_VALUE:
                    value = value[:MAX_EMBED_FIELD_VALUE-3] + "..."
                
                embed.add_field(name=name, value=value, inline=inline)
        
        # Add media
        if thumbnail_url:
            embed.set_thumbnail(url=thumbnail_url)
        
        if image_url:
            embed.set_image(url=image_url)
        
        # Add author
        if author_name:
            embed.set_author(name=author_name, url=author_url)
        
        # Add footer
        if footer_text:
            embed.set_footer(text=footer_text)
        
        return embed
    
    @staticmethod
    def create_success_embed(title: str, description: str = "", **kwargs) -> discord.Embed:
        """Create a success-styled embed (green)"""
        return ResponseHandler.create_embed(
            title=title,
            description=description,
            color=SUCCESS_COLOR,
            **kwargs
        )
    
    @staticmethod
    def create_error_embed(title: str, description: str = "", **kwargs) -> discord.Embed:
        """Create an error-styled embed (red)"""
        return ResponseHandler.create_embed(
            title=title,
            description=description,
            color=ERROR_COLOR,
            **kwargs
        )
    
    @staticmethod
    def create_warning_embed(title: str, description: str = "", **kwargs) -> discord.Embed:
        """Create a warning-styled embed (orange)"""
        return ResponseHandler.create_embed(
            title=title,
            description=description,
            color=WARNING_COLOR,
            **kwargs
        )
    
    @staticmethod
    def create_info_embed(title: str, description: str = "", **kwargs) -> discord.Embed:
        """Create an info-styled embed (blue)"""
        return ResponseHandler.create_embed(
            title=title,
            description=description,
            color=INFO_COLOR,
            **kwargs
        )
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 1024) -> str:
        """
        Truncate text to specified length
        
        Args:
            text: Text to truncate
            max_length: Maximum length
            
        Returns:
            str: Truncated text with ellipsis if needed
        """
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    @staticmethod
    def format_code_block(code: str, language: str = "") -> str:
        """
        Format code in a Discord code block
        
        Args:
            code: Code to format
            language: Programming language for syntax highlighting
            
        Returns:
            str: Formatted code block
        """
        return f"```{language}\n{code}\n```"
    
    @staticmethod
    def format_list(items: List[str], bullet: str = "•") -> str:
        """
        Format a list of items with bullets
        
        Args:
            items: List of items
            bullet: Bullet character
            
        Returns:
            str: Formatted list
        """
        return "\n".join(f"{bullet} {item}" for item in items)
    
    @staticmethod
    def format_key_value_pairs(pairs: Dict[str, str], separator: str = ": ") -> str:
        """
        Format key-value pairs
        
        Args:
            pairs: Dictionary of key-value pairs
            separator: Separator between key and value
            
        Returns:
            str: Formatted pairs
        """
        return "\n".join(f"**{key}**{separator}{value}" for key, value in pairs.items())
