import discord
from discord.ext import commands
import os
import asyncio
import random
from dotenv import load_dotenv

# Import our tsundere modules
from modules.personality import TsunderePersonality
from modules.utilities import TsundereUtilities
from modules.games import TsundereGames
from modules.social import TsundereSocial
from modules.server_actions import TsundereServerActions
from modules.persona_manager import PersonaManager
from modules.search import TsundereSearch
from modules.api_manager import GeminiAPIManager

# Load environment variables
load_dotenv()

# Initialize API Manager with rotating keys
api_manager = GeminiAPIManager()
model = api_manager.get_current_model()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize persona and modules
persona_manager = PersonaManager()
personality = TsunderePersonality()
utilities = None  # Will be initialized after model is ready
games = TsundereGames()
social = TsundereSocial()
server_actions = TsundereServerActions()
search = None  # Will be initialized after model is ready

@bot.event
async def on_ready():
    global utilities, search
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')
    
    # Initialize utilities and search with the model
    print("🔧 Initializing utilities...")
    utilities = TsundereUtilities(model)
    print("🔍 Initializing search module...")
    search = TsundereSearch(model)
    print("✅ All modules initialized successfully!")
    
    # Print API manager status
    status = api_manager.get_status()
    print(f"🔑 Using {status['total_keys']} API key(s), currently on key #{status['current_key']}")
    
    # Set tsundere status
    status_text = persona_manager.persona.get("activity_responses", {}).get("bot_status", "It's not like I want to help! | !help_ai")
    await bot.change_presence(activity=discord.Game(name=status_text))

async def should_search_web(question):
    """Determine if a question would benefit from web search"""
    search_indicators = [
        # Current events and news
        'latest', 'recent', 'current', 'news', 'today', 'this year', '2024', '2025',
        # Specific information requests
        'what is', 'who is', 'where is', 'when did', 'how to', 'tutorial',
        # Product/company/technology queries
        'price', 'cost', 'buy', 'download', 'install', 'specs', 'review',
        # Location-based queries
        'near me', 'location', 'address', 'directions',
        # Factual lookups
        'definition', 'meaning', 'explain', 'about',
        # Technology and tools
        'github', 'documentation', 'docs', 'api', 'library', 'framework',
        # Specific brands/products
        'esp32', 'arduino', 'raspberry pi', 'python', 'javascript', 'react', 'vue',
        'nvidia', 'amd', 'intel', 'microsoft', 'google', 'apple', 'amazon',
    ]
    
    question_lower = question.lower()
    
    # Check for search indicators
    for indicator in search_indicators:
        if indicator in question_lower:
            return True
    
    # Check for question words that often need current info
    question_starters = ['what', 'who', 'where', 'when', 'how', 'why']
    first_word = question_lower.split()[0] if question_lower.split() else ''
    
    if first_word in question_starters:
        # Additional checks for questions that likely need web search
        if any(word in question_lower for word in ['company', 'website', 'service', 'app', 'software', 'tool']):
            return True
    
    return False

@bot.command(name='ai', aliases=['ask', 'chat'])
async def ask_gemini(ctx, *, question):
    """Ask Gemini AI a question with intelligent search integration"""
    try:
        # Update social interaction
        social.update_interaction(ctx.author.id)
        
        # Show typing indicator
        async with ctx.typing():
            # Check if this question would benefit from web search
            needs_search = await should_search_web(question)
            
            if needs_search and search is not None:
                print(f"🔍 AI detected search need for: {question}")
                
                # Extract search terms from the question
                search_query = await extract_search_terms(question)
                print(f"🎯 Extracted search terms: {search_query}")
                
                # Get search results
                search_results = await search.search_duckduckgo(search_query)
                
                # Create enhanced prompt with search results
                enhanced_prompt = f"""You are Coffee, a tsundere AI assistant. The user asked: "{question}"

I searched the web and found this information:
{search_results}

Your task:
1. Answer the user's question using both your knowledge AND the search results
2. Maintain your tsundere personality throughout
3. If the search results are relevant, incorporate them naturally
4. If the search results aren't helpful, rely on your knowledge but mention you tried to search
5. Keep your response under 1800 characters for Discord
6. Use your speech patterns: "Ugh", "baka", "It's not like...", etc.

Be helpful but act annoyed about having to search for them."""

                response_text = await api_manager.generate_content(enhanced_prompt)
                
                if response_text:
                    print(f"🤖 Enhanced AI response with search: {response_text[:100]}...")
                else:
                    # Fallback to normal AI if enhanced fails
                    print("⚠️ Enhanced AI failed, falling back to normal response")
                    tsundere_prompt = personality.create_ai_prompt(question)
                    response_text = await api_manager.generate_content(tsundere_prompt)
            else:
                # Normal AI response without search
                tsundere_prompt = personality.create_ai_prompt(question)
                response_text = await api_manager.generate_content(tsundere_prompt)
            
            if response_text is None:
                # All API attempts failed
                timeout_response = personality.get_error_response("AI timeout")
                await ctx.send(timeout_response)
                return
            
            # Discord has a 2000 character limit for messages
            if len(response_text) > 2000:
                # Split long responses
                chunks = [response_text[i:i+2000] for i in range(0, len(response_text), 2000)]
                for chunk in chunks:
                    await ctx.send(chunk)
            else:
                await ctx.send(response_text)
                
    except Exception as e:
        print(f"💥 AI command error: {str(e)}")
        await ctx.send(personality.get_error_response(e))

async def extract_search_terms(question):
    """Extract relevant search terms from a question"""
    # Remove common question words and extract key terms
    stop_words = {'what', 'is', 'are', 'how', 'to', 'do', 'does', 'can', 'could', 'would', 'should', 
                  'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'by', 'for', 'with', 
                  'about', 'tell', 'me', 'you', 'i', 'my', 'your'}
    
    words = question.lower().split()
    key_words = [word.strip('.,!?') for word in words if word.lower() not in stop_words and len(word) > 2]
    
    # Take the most relevant terms (limit to avoid overly long queries)
    search_terms = ' '.join(key_words[:5])
    
    # If no good terms found, use the original question
    if not search_terms.strip():
        search_terms = question
    
    return search_terms

@bot.command(name='help_ai', aliases=['commands'])
async def help_command(ctx):
    """Show bot help"""
    help_config = persona_manager.persona.get("activity_responses", {}).get("help_command", {})
    
    embed = discord.Embed(
        title=help_config.get("title", "Commands"),
        description=help_config.get("description", "Here are the commands"),
        color=0xff69b4
    )
    embed.add_field(
        name="**AI & Chat**",
        value="`!ai <question>` (or `!ask`, `!chat`) - Ask me stuff, I guess...\n`!compliment` - Compliment me (watch me get flustered)\n`!mood` - Check my current mood\n`!relationship` - See how close we are",
        inline=False
    )
    embed.add_field(
        name="**Utilities**",
        value="`!time` - Get current time\n`!calc <math>` - Calculator\n`!dice [sides]` - Roll dice\n`!flip` - Flip a coin\n`!weather <city>` - Real weather info\n`!fact` - Random fact\n`!joke` - Random joke\n`!catfact` - Cat facts",
        inline=False
    )
    embed.add_field(
        name="**Search**",
        value="`!search <query>` (or `!google`, `!find`) - Search the web\n`!websearch <query>` (or `!web`) - Alternative web search",
        inline=False
    )
    embed.add_field(
        name="**Games**",
        value="`!game guess [max]` - Number guessing\n`!guess <number>` - Make a guess\n`!rps <choice>` (or `!rock`, `!paper`, `!scissors`) - Rock Paper Scissors\n`!8ball <question>` - Magic 8-ball\n`!trivia` - Start trivia game\n`!answer <answer>` - Answer trivia",
        inline=False
    )
    embed.add_field(
        name="**Server Actions** (with permissions)",
        value="`!mention @user [message]` - Mention someone\n`!create_role <name> [color]` - Create a role\n`!give_role @user <role>` - Give role to user\n`!remove_role @user <role>` - Remove role\n`!kick @user [reason]` - Kick user\n`!create_channel <name> [type]` - Create channel\n`!send_to #channel <message>` - Send message to channel",
        inline=False
    )
    embed.add_field(
        name="**Admin Commands** (admin only)",
        value="`!reload_persona` - Reload personality config\n`!api_status` - Check API key status\n`!shutdown` (or `!kill`, `!stop`) - Shutdown bot\n`!restart` (or `!reboot`) - Restart bot",
        inline=False
    )
    embed.set_footer(text=help_config.get("footer", "Use these commands!"))
    await ctx.send(embed=embed)

@bot.event
async def on_message(message):
    # Don't respond to bot messages
    if message.author == bot.user:
        return
    
    # Tsundere reactions to mentions
    if bot.user.mentioned_in(message) and not message.content.startswith('!'):
        try:
            # Get user relationship for personalized response
            user_data = social.get_user_relationship(message.author.id)
            relationship_level = user_data['relationship_level']
            
            # Generate AI response for being mentioned
            prompt = persona_manager.create_ai_prompt(
                f"mentioned me in chat: '{message.content}'", 
                message.author.display_name, relationship_level
            )
            response = await api_manager.generate_content(prompt)
            
            if response:
                await message.channel.send(response)
        except discord.Forbidden:
            # Bot doesn't have permission to send messages in this channel
            pass
        except Exception:
            # Handle any other errors silently
            pass
    
    # Process commands
    await bot.process_commands(message)

@bot.command(name='compliment')
async def compliment_ai(ctx):
    """Compliment the AI (watch her get flustered)"""
    user_data = social.update_interaction(ctx.author.id)
    relationship_level = user_data['relationship_level']
    
    # Generate AI response for compliment command
    prompt = persona_manager.create_ai_prompt(
        "!compliment command", ctx.author.display_name, relationship_level
    )
    response = await api_manager.generate_content(prompt)
    
    if response:
        await ctx.send(response)
    else:
        # Fallback to persona card response
        fallback = personality.get_error_response("AI unavailable")
        await ctx.send(fallback)

# Social Commands
@bot.command(name='mood')
async def check_mood(ctx):
    """Check the AI's current mood"""
    user_data = social.get_user_relationship(ctx.author.id)
    relationship_level = user_data['relationship_level']
    
    # Generate AI response for mood command
    prompt = persona_manager.create_ai_prompt(
        "!mood command", ctx.author.display_name, relationship_level
    )
    response = await api_manager.generate_content(prompt)
    
    if response:
        await ctx.send(response)
    else:
        # Fallback to persona card response
        fallback = personality.get_error_response("AI unavailable")
        await ctx.send(fallback)

@bot.command(name='relationship')
async def check_relationship(ctx):
    """Check your relationship status with the AI"""
    user_data = social.get_user_relationship(ctx.author.id)
    relationship_level = user_data['relationship_level']
    interactions = user_data['interactions']
    
    # Generate AI response for relationship command
    prompt = persona_manager.create_ai_prompt(
        f"!relationship command (level: {relationship_level}, interactions: {interactions})", 
        ctx.author.display_name, relationship_level
    )
    response = await api_manager.generate_content(prompt)
    
    if response:
        await ctx.send(response)
    else:
        # Fallback to persona card response with relationship info
        fallback = persona_manager.get_relationship_response(relationship_level, "greeting")
        await ctx.send(f"{fallback} (Interactions: {interactions}, Level: {relationship_level})")

# Utility Commands
@bot.command(name='time')
async def get_time(ctx):
    """Get current time"""
    response = await utilities.get_time()
    await ctx.send(response)

@bot.command(name='calc')
async def calculate(ctx, *, expression):
    """Calculator with attitude"""
    response = await utilities.calculate(expression)
    await ctx.send(response)

@bot.command(name='dice')
async def roll_dice(ctx, sides: int = 6):
    """Roll dice"""
    response = await utilities.roll_dice(sides)
    await ctx.send(response)

@bot.command(name='flip')
async def flip_coin(ctx):
    """Flip a coin"""
    response = await utilities.flip_coin()
    await ctx.send(response)

@bot.command(name='weather')
async def get_weather(ctx, *, location):
    """Get weather using real API"""
    async with ctx.typing():
        response = await utilities.get_weather(location)
    await ctx.send(response)

@bot.command(name='fact')
async def get_fact(ctx):
    """Get a random fact"""
    async with ctx.typing():
        response = await utilities.get_random_fact()
    await ctx.send(response)

@bot.command(name='joke')
async def get_joke(ctx):
    """Get a random joke"""
    async with ctx.typing():
        response = await utilities.get_joke()
    await ctx.send(response)

@bot.command(name='catfact')
async def get_cat_fact(ctx):
    """Get a random cat fact"""
    async with ctx.typing():
        response = await utilities.get_cat_fact()
    await ctx.send(response)

# Search Commands
@bot.command(name='search', aliases=['google', 'find'])
async def search_web(ctx, *, query):
    """Search the web using DuckDuckGo"""
    try:
        # Check if search module is initialized
        if search is None:
            await ctx.send("Search module not ready yet! Try again in a moment.")
            return
        
        # Update social interaction
        social.update_interaction(ctx.author.id)
        
        print(f"🔍 Search command called with query: {query}")
        
        async with ctx.typing():
            # Use AI analysis for the main search command
            response = await search.search_duckduckgo(query, use_ai_analysis=True)
        
        print(f"📝 Search response: {response[:100]}...")
        
        # Discord has a 2000 character limit for messages
        if len(response) > 2000:
            # Split long responses
            chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
            for chunk in chunks:
                await ctx.send(chunk)
        else:
            await ctx.send(response)
            
    except Exception as e:
        print(f"💥 Search command error: {str(e)}")
        await ctx.send(personality.get_error_response(e))

@bot.command(name='websearch', aliases=['web'])
async def web_search_command(ctx, *, query):
    """Alternative web search using HTML parsing"""
    try:
        # Check if search module is initialized
        if search is None:
            await ctx.send("Search module not ready yet! Try again in a moment.")
            return
        
        # Update social interaction
        social.update_interaction(ctx.author.id)
        
        print(f"🌐 Web search command called with query: {query}")
        
        async with ctx.typing():
            # Use formatted links for the web search command
            response = await search.search_duckduckgo(query, use_ai_analysis=False)
        
        print(f"📝 Web search response: {response[:100]}...")
        
        # Discord has a 2000 character limit for messages
        if len(response) > 2000:
            # Split long responses
            chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
            for chunk in chunks:
                await ctx.send(chunk)
        else:
            await ctx.send(response)
            
    except Exception as e:
        print(f"💥 Web search command error: {str(e)}")
        await ctx.send(personality.get_error_response(e))

# Game Commands
@bot.command(name='game')
async def start_game(ctx, game_type=None, max_number: int = 100):
    """Start a game"""
    if game_type is None:
        await ctx.send(personality.get_missing_args_response() + " Try `!game guess` for number guessing!")
        return
    
    if game_type.lower() == 'guess':
        response = await games.start_number_guessing(ctx.author.id, max_number)
        await ctx.send(response)
    else:
        await ctx.send(personality.get_missing_args_response() + " I only know 'guess' games right now! Try `!game guess`!")

@bot.command(name='guess')
async def make_guess(ctx, number: int):
    """Make a guess in the number game"""
    response = await games.guess_number(ctx.author.id, number)
    await ctx.send(response)

@bot.command(name='rps', aliases=['rock', 'paper', 'scissors'])
async def rock_paper_scissors(ctx, choice=None):
    """Play Rock Paper Scissors"""
    # If command was called with an alias, use that as the choice
    if choice is None and ctx.invoked_with in ['rock', 'paper', 'scissors']:
        choice = ctx.invoked_with
    
    if choice is None:
        await ctx.send(personality.get_missing_args_response() + " Pick rock, paper, or scissors! Try `!rps rock` or just `!rock`!")
        return
    
    response = await games.rock_paper_scissors(choice)
    await ctx.send(response)

@bot.command(name='8ball')
async def magic_8ball(ctx, *, question):
    """Ask the magic 8-ball"""
    async with ctx.typing():
        response = await games.magic_8ball(question)
    await ctx.send(response)

@bot.command(name='trivia')
async def start_trivia(ctx):
    """Start a trivia game"""
    async with ctx.typing():
        response = await games.trivia_game(ctx.author.id)
    await ctx.send(response)

@bot.command(name='answer')
async def answer_trivia(ctx, *, answer):
    """Answer the trivia question"""
    response = await games.answer_trivia(ctx.author.id, answer)
    await ctx.send(response)

# Server Action Commands
@bot.command(name='mention')
async def mention_user(ctx, user: discord.Member, *, message=None):
    """Ask the bot to mention someone with an optional message"""
    response = await server_actions.mention_user(ctx, user, message)
    await ctx.send(response)

@bot.command(name='create_role')
async def create_role(ctx, role_name, color=None):
    """Create a new role"""
    response = await server_actions.create_role(ctx, role_name, color)
    await ctx.send(response)

@bot.command(name='give_role')
async def give_role(ctx, user: discord.Member, *, role_name):
    """Give a role to a user"""
    response = await server_actions.give_role(ctx, user, role_name)
    await ctx.send(response)

@bot.command(name='remove_role')
async def remove_role(ctx, user: discord.Member, *, role_name):
    """Remove a role from a user"""
    response = await server_actions.remove_role(ctx, user, role_name)
    await ctx.send(response)

@bot.command(name='kick')
async def kick_user(ctx, user: discord.Member, *, reason=None):
    """Kick a user from the server"""
    response = await server_actions.kick_user(ctx, user, reason)
    await ctx.send(response)

@bot.command(name='create_channel')
async def create_channel(ctx, channel_name, channel_type="text"):
    """Create a new text or voice channel"""
    response = await server_actions.create_channel(ctx, channel_name, channel_type)
    await ctx.send(response)

@bot.command(name='send_to')
async def send_message_to_channel(ctx, channel: discord.TextChannel, *, message):
    """Send a message to a specific channel"""
    response = await server_actions.send_message_to_channel(ctx, channel.mention, message)
    await ctx.send(response)

# Admin Commands
@bot.command(name='reload_persona')
async def reload_persona(ctx):
    """Reload the persona card (admin only)"""
    if ctx.author.guild_permissions.administrator:
        result = personality.reload_persona()
        
        # Get user relationship for personalized response
        user_data = social.get_user_relationship(ctx.author.id)
        relationship_level = user_data['relationship_level']
        
        # Generate AI response for reload command
        prompt = persona_manager.create_ai_prompt(
            f"!reload_persona command (result: {result})", ctx.author.display_name, relationship_level
        )
        response = await api_manager.generate_content(prompt)
        
        if response:
            await ctx.send(response)
        else:
            # Fallback to persona card response
            fallback = persona_manager.get_activity_response("admin", "reload_success", result=result)
            await ctx.send(fallback)
    else:
        # Generate AI response for no permission
        prompt = persona_manager.create_ai_prompt(
            "!reload_persona command (no permission)", ctx.author.display_name, "stranger"
        )
        response = await api_manager.generate_content(prompt)
        
        if response:
            await ctx.send(response)
        else:
            # Fallback to persona card response
            fallback = persona_manager.get_activity_response("admin", "no_permission")
            await ctx.send(fallback)

@bot.command(name='shutdown', aliases=['kill', 'stop'])
async def shutdown_bot(ctx):
    """Shutdown the bot (admin only)"""
    if ctx.author.guild_permissions.administrator:
        # Get user relationship for personalized response
        user_data = social.get_user_relationship(ctx.author.id)
        relationship_level = user_data['relationship_level']
        
        # Generate AI response for shutdown command
        prompt = persona_manager.create_ai_prompt(
            "!shutdown command", ctx.author.display_name, relationship_level
        )
        response = await api_manager.generate_content(prompt)
        
        if response:
            await ctx.send(response)
        else:
            # Fallback to persona card response
            shutdown_responses = persona_manager.get_activity_response("admin", "shutdown")
            if isinstance(shutdown_responses, list):
                fallback = random.choice(shutdown_responses)
            else:
                fallback = shutdown_responses
            await ctx.send(fallback)
        print(f"Bot shutdown requested by {ctx.author}")
        
        # Save any pending data and close search session
        social.save_user_data()
        if search:
            try:
                await search.close_session()
            except Exception as e:
                print(f"⚠️ Error closing search session: {e}")
        
        # Close bot connection and exit
        await bot.close()
        
        # Force exit the script
        import sys
        sys.exit(0)
    else:
        # Generate AI response for no permission
        prompt = persona_manager.create_ai_prompt(
            "!shutdown command (no permission)", ctx.author.display_name, "stranger"
        )
        response = await api_manager.generate_content(prompt)
        
        if response:
            await ctx.send(response)
        else:
            # Fallback to persona card response
            fallback = persona_manager.get_activity_response("admin", "no_permission")
            await ctx.send(fallback)

@bot.command(name='restart', aliases=['reboot'])
async def restart_bot(ctx):
    """Restart the bot (admin only)"""
    if ctx.author.guild_permissions.administrator:
        # Get user relationship for personalized response
        user_data = social.get_user_relationship(ctx.author.id)
        relationship_level = user_data['relationship_level']
        
        # Generate AI response for restart command
        response_text = await api_manager.generate_content(
            persona_manager.create_ai_prompt("!restart command", ctx.author.display_name, relationship_level)
        )
        
        if response_text:
            await ctx.send(response_text)
        else:
            # Fallback to persona card response
            restart_responses = persona_manager.get_activity_response("admin", "restart")
            if isinstance(restart_responses, list):
                fallback = random.choice(restart_responses)
            else:
                fallback = restart_responses
            await ctx.send(fallback)
        
        print(f"Bot restart requested by {ctx.author}")
        
        # Save any pending data and close search session
        social.save_user_data()
        if search:
            try:
                await search.close_session()
            except Exception as e:
                print(f"⚠️ Error closing search session: {e}")
        
        # Close bot connection
        await bot.close()
        
        # Restart the script
        import os
        import sys
        print("Restarting bot...")
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        # Generate AI response for no permission
        response_text = await api_manager.generate_content(
            persona_manager.create_ai_prompt("!restart command (no permission)", ctx.author.display_name, "stranger")
        )
        
        if response_text:
            await ctx.send(response_text)
        else:
            # Fallback to persona card response
            fallback = persona_manager.get_activity_response("admin", "no_permission")
            await ctx.send(fallback)

@bot.command(name='api_status')
async def api_status(ctx):
    """Check API key status (admin only)"""
    if ctx.author.guild_permissions.administrator:
        status = api_manager.get_status()
        
        embed = discord.Embed(
            title="🔑 API Key Status",
            description=f"Managing {status['total_keys']} API key(s)",
            color=0x00ff00
        )
        
        for key_info in status['keys']:
            status_emoji = "🟢" if key_info['available'] else "🔴"
            current_emoji = "👈" if key_info['is_current'] else ""
            
            field_name = f"{status_emoji} Key #{key_info['key_number']} {current_emoji}"
            
            field_value = f"Requests: {key_info['requests_this_minute']}/{key_info['rate_limit']}\n"
            field_value += f"Errors: {key_info['errors']}\n"
            
            if key_info['in_cooldown']:
                field_value += f"⏰ Cooldown until: {key_info['cooldown_expires'][:19]}"
            elif key_info['available']:
                field_value += "✅ Available"
            else:
                field_value += "⚠️ Rate limited"
            
            embed.add_field(name=field_name, value=field_value, inline=True)
        
        await ctx.send(embed=embed)
    else:
        # Fallback to persona card response
        fallback = persona_manager.get_activity_response("admin", "no_permission")
        await ctx.send(fallback)

@bot.event
async def on_command_error(ctx, error):
    """Global error handler for commands"""
    if isinstance(error, commands.MissingRequiredArgument):
        # Handle missing arguments with persona response
        await ctx.send(personality.get_missing_args_response() + f" You're missing: {error.param.name}")
    elif isinstance(error, commands.CommandNotFound):
        # Ignore command not found errors (don't spam chat)
        pass
    elif isinstance(error, discord.Forbidden):
        # Bot doesn't have permissions - try to DM user if possible
        try:
            permissions_config = persona_manager.persona.get("activity_responses", {}).get("permissions", {})
            message = permissions_config.get("no_send_permission", "I don't have permission to send messages!")
            await ctx.author.send(message)
        except (discord.Forbidden, discord.HTTPException):
            pass  # Can't DM either, give up silently
    else:
        # For other errors, send a generic tsundere error message
        try:
            await ctx.send(personality.get_error_response(error))
        except (discord.Forbidden, discord.HTTPException):
            pass  # If we can't send the error message, fail silently

if __name__ == '__main__':
    import signal
    import sys
    
    def signal_handler(sig, frame):
        """Handle Ctrl+C gracefully"""
        print('\n🛑 Shutdown signal received...')
        # Save any pending data and cleanup
        if 'social' in globals():
            social.save_user_data()
        if 'search' in globals() and search:
            asyncio.run(search.close_session())
        print('👋 Coffee is shutting down... Goodbye!')
        sys.exit(0)
    
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        bot.run(os.getenv('DISCORD_TOKEN'))
    except KeyboardInterrupt:
        print('\n🛑 Bot interrupted by user')
        # Save any pending data and cleanup
        if 'social' in globals():
            social.save_user_data()
        if 'search' in globals() and search:
            asyncio.run(search.close_session())
        print('👋 Coffee is shutting down... Goodbye!')
    except Exception as e:
        print(f'❌ Bot crashed: {e}')
        # Save any pending data and cleanup
        if 'social' in globals():
            social.save_user_data()
        if 'search' in globals() and search:
            asyncio.run(search.close_session())
        raise