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
from modules.config_manager import ConfigManager
from modules.response_handler import ResponseHandler
from modules.logger import BotLogger

# Initialize logger
logger = BotLogger.get_logger(__name__)

# Load environment variables
load_dotenv()

# Initialize Config Manager (defer validation until bot starts)
config = ConfigManager(validate=False)

# Initialize API Manager with rotating keys
api_manager = GeminiAPIManager()
model = api_manager.get_current_model()  # May be None if no keys are loaded yet

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
    global utilities, search, model
    
    # Validate configuration on first connection
    try:
        config.validate_config()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration validation failed: {e}")
        print(f"❌ Configuration Error: {e}")
        await bot.close()
        return
    
    # Reinitialize model and API manager after config is validated
    logger.info("Reinitializing API manager with validated configuration")
    api_manager._load_keys_from_env()
    api_manager._init_usage_tracking()
    model = api_manager.get_current_model()
    
    if model is None:
        logger.error("Failed to initialize model after configuration validation")
        print("❌ Failed to initialize model")
        await bot.close()
        return
    
    logger.info(f"Bot {bot.user} connected to Discord")
    logger.info(f"Bot is in {len(bot.guilds)} guilds")
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')
    
    # Initialize utilities and search with the model
    logger.info("Initializing utilities module")
    print("🔧 Initializing utilities...")
    utilities = TsundereUtilities(model)
    
    logger.info("Initializing search module")
    print("🔍 Initializing search module...")
    search = TsundereSearch(model)
    
    logger.info("All modules initialized successfully")
    print("✅ All modules initialized successfully!")
    
    # Print API manager status
    status = api_manager.get_status()
    logger.info(f"API manager initialized: {status['total_keys']} keys, current key #{status['current_key']}")
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
        logger.info(f"AI command called by user {ctx.author.id}, question: {question[:100]}")
        
        # Update social interaction
        social.update_interaction(ctx.author.id)
        
        # Show typing indicator
        async with ctx.typing():
            # Check if this question would benefit from web search
            needs_search = await should_search_web(question)
            logger.info(f"Search needed for question: {needs_search}")
            
            if needs_search and search is not None:
                logger.info(f"Performing web search for: {question}")
                print(f"🔍 AI detected search need for: {question}")
                
                # Extract search terms from the question
                search_query = await extract_search_terms(question)
                logger.info(f"Extracted search terms: {search_query}")
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
                    logger.info("Enhanced AI response generated successfully")
                    print(f"🤖 Enhanced AI response with search: {response_text[:100]}...")
                else:
                    # Fallback to normal AI if enhanced fails
                    logger.warning("Enhanced AI failed, falling back to normal response")
                    print("⚠️ Enhanced AI failed, falling back to normal response")
                    tsundere_prompt = personality.create_ai_prompt(question)
                    response_text = await api_manager.generate_content(tsundere_prompt)
            else:
                # Normal AI response without search
                logger.info("Generating normal AI response without search")
                tsundere_prompt = personality.create_ai_prompt(question)
                response_text = await api_manager.generate_content(tsundere_prompt)
            
            if response_text is None:
                # All API attempts failed
                logger.error("All API attempts failed for AI command")
                timeout_response = personality.get_error_response("AI timeout")
                await ctx.send(timeout_response)
                return
            
            # Discord has a 2000 character limit for messages
            if len(response_text) > 2000:
                logger.info(f"Response too long ({len(response_text)} chars), splitting into chunks")
                # Split long responses
                chunks = [response_text[i:i+2000] for i in range(0, len(response_text), 2000)]
                for chunk in chunks:
                    await ctx.send(chunk)
            else:
                await ctx.send(response_text)
            
            logger.info("AI response sent successfully")
                
    except Exception as e:
        logger.error(f"AI command error: {str(e)}")
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
    logger.info(f"Help command called by user {ctx.author.id}")
    
    help_config = persona_manager.persona.get("activity_responses", {}).get("help_command", {})
    
    # Use ResponseHandler to create a formatted embed
    embed = ResponseHandler.create_info_embed(
        title=help_config.get("title", "Coffee's Commands"),
        description=help_config.get("description", "Here are the commands I 'reluctantly' offer..."),
        fields=[
            {
                'name': "**AI & Chat**",
                'value': "`!ai <question>` (or `!ask`, `!chat`) - Ask me stuff, I guess...\n`!compliment` - Compliment me (watch me get flustered)\n`!mood` - Check my current mood\n`!relationship` - See how close we are",
                'inline': False
            },
            {
                'name': "**Utilities**",
                'value': "`!time` - Get current time\n`!calc <math>` - Calculator\n`!dice [sides]` - Roll dice\n`!flip` - Flip a coin\n`!weather <city>` - Real weather info\n`!fact` - Random fact\n`!joke` - Random joke\n`!catfact` - Cat facts",
                'inline': False
            },
            {
                'name': "**Search**",
                'value': "`!search <query>` (or `!google`, `!find`) - Search the web\n`!websearch <query>` (or `!web`) - Alternative web search",
                'inline': False
            },
            {
                'name': "**Games**",
                'value': "`!game guess [max]` - Number guessing\n`!guess <number>` - Make a guess\n`!rps <choice>` (or `!rock`, `!paper`, `!scissors`) - Rock Paper Scissors\n`!8ball <question>` - Magic 8-ball\n`!trivia` - Start trivia game\n`!answer <answer>` - Answer trivia",
                'inline': False
            },
            {
                'name': "**Server Actions** (with permissions)",
                'value': "`!mention @user [message]` - Mention someone\n`!create_role <name> [color]` - Create a role\n`!give_role @user <role>` - Give role to user\n`!remove_role @user <role>` - Remove role\n`!kick @user [reason]` - Kick user\n`!create_channel <name> [type]` - Create channel\n`!send_to #channel <message>` - Send message to channel",
                'inline': False
            },
            {
                'name': "**Admin Commands** (admin only)",
                'value': "`!reload_persona` - Reload personality config\n`!api_status` - Check API key status\n`!shutdown` (or `!kill`, `!stop`) - Shutdown bot\n`!restart` (or `!reboot`) - Restart bot",
                'inline': False
            }
        ],
        footer_text=help_config.get("footer", "Use these commands!")
    )
    
    await ctx.send(embed=embed)

@bot.event
async def on_message(message):
    # Don't respond to bot messages
    if message.author == bot.user:
        return
    
    # Tsundere reactions to mentions
    if bot.user.mentioned_in(message) and not message.content.startswith('!'):
        try:
            logger.info(f"Bot mentioned by user {message.author.id} in guild {message.guild.id}: {message.content[:100]}")
            
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
                logger.info(f"Response sent to mention in guild {message.guild.id}")
        except discord.Forbidden:
            logger.warning(f"No permission to send message in channel {message.channel.id}")
            # Bot doesn't have permission to send messages in this channel
            pass
        except Exception as e:
            logger.error(f"Error handling mention: {e}")
            # Handle any other errors silently
            pass
    
    # Process commands
    await bot.process_commands(message)

@bot.command(name='compliment')
async def compliment_ai(ctx):
    """Compliment the AI (watch her get flustered)"""
    logger.info(f"Compliment command called by user {ctx.author.id}")
    
    user_data = social.update_interaction(ctx.author.id)
    relationship_level = user_data['relationship_level']
    
    # Generate AI response for compliment command
    prompt = persona_manager.create_ai_prompt(
        "!compliment command", ctx.author.display_name, relationship_level
    )
    response = await api_manager.generate_content(prompt)
    
    if response:
        await ctx.send(response)
        logger.info(f"Compliment response sent to user {ctx.author.id}")
    else:
        # Fallback to persona card response
        logger.warning("AI response failed, using fallback for compliment")
        fallback = personality.get_error_response("AI unavailable")
        await ctx.send(fallback)

# Social Commands
@bot.command(name='mood')
async def check_mood(ctx):
    """Check the AI's current mood"""
    logger.info(f"Mood command called by user {ctx.author.id}")
    
    user_data = social.get_user_relationship(ctx.author.id)
    relationship_level = user_data['relationship_level']
    
    # Generate AI response for mood command
    prompt = persona_manager.create_ai_prompt(
        "!mood command", ctx.author.display_name, relationship_level
    )
    response = await api_manager.generate_content(prompt)
    
    if response:
        await ctx.send(response)
        logger.info(f"Mood response sent to user {ctx.author.id}")
    else:
        # Fallback to persona card response
        logger.warning("AI response failed, using fallback for mood command")
        fallback = personality.get_error_response("AI unavailable")
        await ctx.send(fallback)

@bot.command(name='relationship')
async def check_relationship(ctx):
    """Check your relationship status with the AI"""
    logger.info(f"Relationship command called by user {ctx.author.id}")
    
    user_data = social.get_user_relationship(ctx.author.id)
    relationship_level = user_data['relationship_level']
    interactions = user_data['interactions']
    
    logger.info(f"User {ctx.author.id} relationship level: {relationship_level}, interactions: {interactions}")
    
    # Generate AI response for relationship command
    prompt = persona_manager.create_ai_prompt(
        f"!relationship command (level: {relationship_level}, interactions: {interactions})", 
        ctx.author.display_name, relationship_level
    )
    response = await api_manager.generate_content(prompt)
    
    if response:
        await ctx.send(response)
        logger.info(f"Relationship response sent to user {ctx.author.id}")
    else:
        # Fallback to persona card response with relationship info
        logger.warning("AI response failed, using fallback for relationship command")
        fallback = persona_manager.get_relationship_response(relationship_level, "greeting")
        await ctx.send(f"{fallback} (Interactions: {interactions}, Level: {relationship_level})")

# Utility Commands
@bot.command(name='time')
async def get_time(ctx):
    """Get current time"""
    logger.info(f"Time command called by user {ctx.author.id}")
    response = await utilities.get_time()
    await ctx.send(response)

@bot.command(name='calc')
async def calculate(ctx, *, expression):
    """Calculator with attitude"""
    logger.info(f"Calc command called by user {ctx.author.id}, expression: {expression}")
    response = await utilities.calculate(expression)
    await ctx.send(response)

@bot.command(name='dice')
async def roll_dice(ctx, sides: int = 6):
    """Roll dice"""
    logger.info(f"Dice command called by user {ctx.author.id}, sides: {sides}")
    response = await utilities.roll_dice(sides)
    await ctx.send(response)

@bot.command(name='flip')
async def flip_coin(ctx):
    """Flip a coin"""
    logger.info(f"Flip command called by user {ctx.author.id}")
    response = await utilities.flip_coin()
    await ctx.send(response)

@bot.command(name='weather')
async def get_weather(ctx, *, location):
    """Get weather using real API"""
    logger.info(f"Weather command called by user {ctx.author.id}, location: {location}")
    async with ctx.typing():
        response = await utilities.get_weather(location)
    await ctx.send(response)

@bot.command(name='fact')
async def get_fact(ctx):
    """Get a random fact"""
    logger.info(f"Fact command called by user {ctx.author.id}")
    async with ctx.typing():
        response = await utilities.get_random_fact()
    await ctx.send(response)

@bot.command(name='joke')
async def get_joke(ctx):
    """Get a random joke"""
    logger.info(f"Joke command called by user {ctx.author.id}")
    async with ctx.typing():
        response = await utilities.get_joke()
    await ctx.send(response)

@bot.command(name='catfact')
async def get_cat_fact(ctx):
    """Get a random cat fact"""
    logger.info(f"Cat fact command called by user {ctx.author.id}")
    async with ctx.typing():
        response = await utilities.get_cat_fact()
    await ctx.send(response)

# Search Commands
@bot.command(name='search', aliases=['google', 'find'])
async def search_web(ctx, *, query):
    """Search the web using DuckDuckGo"""
    try:
        logger.info(f"Search command called by user {ctx.author.id}, query: {query}")
        
        # Check if search module is initialized
        if search is None:
            logger.warning("Search module not initialized")
            await ctx.send("Search module not ready yet! Try again in a moment.")
            return
        
        # Update social interaction
        social.update_interaction(ctx.author.id)
        
        print(f"🔍 Search command called with query: {query}")
        
        async with ctx.typing():
            # Use AI analysis for the main search command
            response = await search.search_duckduckgo(query, use_ai_analysis=True)
        
        print(f"📝 Search response: {response[:100]}...")
        logger.info(f"Search completed, response length: {len(response)}")
        
        # Discord has a 2000 character limit for messages
        if len(response) > 2000:
            logger.info("Response too long, splitting into chunks")
            # Split long responses
            chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
            for chunk in chunks:
                await ctx.send(chunk)
        else:
            await ctx.send(response)
            
    except Exception as e:
        logger.error(f"Search command error: {str(e)}")
        print(f"💥 Search command error: {str(e)}")
        await ctx.send(personality.get_error_response(e))

@bot.command(name='websearch', aliases=['web'])
async def web_search_command(ctx, *, query):
    """Alternative web search using HTML parsing"""
    try:
        logger.info(f"Web search command called by user {ctx.author.id}, query: {query}")
        
        # Check if search module is initialized
        if search is None:
            logger.warning("Search module not initialized")
            await ctx.send("Search module not ready yet! Try again in a moment.")
            return
        
        # Update social interaction
        social.update_interaction(ctx.author.id)
        
        print(f"🌐 Web search command called with query: {query}")
        
        async with ctx.typing():
            # Use formatted links for the web search command
            response = await search.search_duckduckgo(query, use_ai_analysis=False)
        
        print(f"📝 Web search response: {response[:100]}...")
        logger.info(f"Web search completed, response length: {len(response)}")
        
        # Discord has a 2000 character limit for messages
        if len(response) > 2000:
            logger.info("Response too long, splitting into chunks")
            # Split long responses
            chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
            for chunk in chunks:
                await ctx.send(chunk)
        else:
            await ctx.send(response)
            
    except Exception as e:
        logger.error(f"Web search command error: {str(e)}")
        print(f"💥 Web search command error: {str(e)}")
        await ctx.send(personality.get_error_response(e))

# Game Commands
@bot.command(name='game')
async def start_game(ctx, game_type=None, max_number: int = 100):
    """Start a game"""
    logger.info(f"Game command called by user {ctx.author.id}, type: {game_type}, max: {max_number}")
    
    if game_type is None:
        logger.warning(f"Game command missing arguments from user {ctx.author.id}")
        await ctx.send(personality.get_missing_args_response() + " Try `!game guess` for number guessing!")
        return
    
    if game_type.lower() == 'guess':
        response = await games.start_number_guessing(ctx.author.id, max_number)
        await ctx.send(response)
    else:
        logger.warning(f"Unknown game type requested by user {ctx.author.id}: {game_type}")
        await ctx.send(personality.get_missing_args_response() + " I only know 'guess' games right now! Try `!game guess`!")

@bot.command(name='guess')
async def make_guess(ctx, number: int):
    """Make a guess in the number game"""
    logger.info(f"Guess command called by user {ctx.author.id}, number: {number}")
    response = await games.guess_number(ctx.author.id, number)
    await ctx.send(response)

@bot.command(name='rps', aliases=['rock', 'paper', 'scissors'])
async def rock_paper_scissors(ctx, choice=None):
    """Play Rock Paper Scissors"""
    # If command was called with an alias, use that as the choice
    if choice is None and ctx.invoked_with in ['rock', 'paper', 'scissors']:
        choice = ctx.invoked_with
    
    logger.info(f"RPS command called by user {ctx.author.id}, choice: {choice}")
    
    if choice is None:
        logger.warning(f"RPS command missing arguments from user {ctx.author.id}")
        await ctx.send(personality.get_missing_args_response() + " Pick rock, paper, or scissors! Try `!rps rock` or just `!rock`!")
        return
    
    response = await games.rock_paper_scissors(choice)
    await ctx.send(response)

@bot.command(name='8ball')
async def magic_8ball(ctx, *, question):
    """Ask the magic 8-ball"""
    logger.info(f"8-ball command called by user {ctx.author.id}, question: {question[:50]}")
    async with ctx.typing():
        response = await games.magic_8ball(question)
    await ctx.send(response)

@bot.command(name='trivia')
async def start_trivia(ctx):
    """Start a trivia game"""
    logger.info(f"Trivia command called by user {ctx.author.id}")
    async with ctx.typing():
        response = await games.trivia_game(ctx.author.id)
    await ctx.send(response)

@bot.command(name='answer')
async def answer_trivia(ctx, *, answer):
    """Answer the trivia question"""
    logger.info(f"Answer command called by user {ctx.author.id}, answer: {answer[:50]}")
    response = await games.answer_trivia(ctx.author.id, answer)
    await ctx.send(response)

# Server Action Commands
@bot.command(name='mention')
async def mention_user(ctx, user: discord.Member, *, message=None):
    """Ask the bot to mention someone with an optional message"""
    logger.info(f"Mention command called by user {ctx.author.id}, target: {user.id}, message: {message[:50] if message else 'None'}")
    response = await server_actions.mention_user(ctx, user, message)
    await ctx.send(response)

@bot.command(name='create_role')
async def create_role(ctx, role_name, color=None):
    """Create a new role"""
    logger.info(f"Create role command called by user {ctx.author.id}, role: {role_name}, color: {color}")
    response = await server_actions.create_role(ctx, role_name, color)
    await ctx.send(response)

@bot.command(name='give_role')
async def give_role(ctx, user: discord.Member, *, role_name):
    """Give a role to a user"""
    logger.info(f"Give role command called by user {ctx.author.id}, target: {user.id}, role: {role_name}")
    response = await server_actions.give_role(ctx, user, role_name)
    await ctx.send(response)

@bot.command(name='remove_role')
async def remove_role(ctx, user: discord.Member, *, role_name):
    """Remove a role from a user"""
    logger.info(f"Remove role command called by user {ctx.author.id}, target: {user.id}, role: {role_name}")
    response = await server_actions.remove_role(ctx, user, role_name)
    await ctx.send(response)

@bot.command(name='kick')
async def kick_user(ctx, user: discord.Member, *, reason=None):
    """Kick a user from the server"""
    logger.info(f"Kick command called by user {ctx.author.id}, target: {user.id}, reason: {reason}")
    response = await server_actions.kick_user(ctx, user, reason)
    await ctx.send(response)

@bot.command(name='create_channel')
async def create_channel(ctx, channel_name, channel_type="text"):
    """Create a new text or voice channel"""
    logger.info(f"Create channel command called by user {ctx.author.id}, name: {channel_name}, type: {channel_type}")
    response = await server_actions.create_channel(ctx, channel_name, channel_type)
    await ctx.send(response)

@bot.command(name='send_to')
async def send_message_to_channel(ctx, channel: discord.TextChannel, *, message):
    """Send a message to a specific channel"""
    logger.info(f"Send to channel command called by user {ctx.author.id}, channel: {channel.id}, message length: {len(message)}")
    response = await server_actions.send_message_to_channel(ctx, channel.mention, message)
    await ctx.send(response)

# Admin Commands
@bot.command(name='reload_persona')
async def reload_persona(ctx):
    """Reload the persona card (admin only)"""
    logger.info(f"Reload persona command called by user {ctx.author.id}")
    
    if ctx.author.guild_permissions.administrator:
        logger.info(f"Admin permission verified for user {ctx.author.id}")
        result = personality.reload_persona()
        logger.info(f"Persona reloaded: {result}")
        
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
            logger.warning("AI response failed for reload_persona, using fallback")
            fallback = persona_manager.get_activity_response("admin", "reload_success", result=result)
            await ctx.send(fallback)
    else:
        logger.warning(f"Non-admin user {ctx.author.id} attempted reload_persona command")
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
    logger.info(f"Shutdown command called by user {ctx.author.id}")
    
    if ctx.author.guild_permissions.administrator:
        logger.info(f"Admin permission verified for user {ctx.author.id}, initiating shutdown")
        
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
        logger.info("User data saved before shutdown")
        
        if search:
            try:
                await search.close_session()
                logger.info("Search session closed")
            except Exception as e:
                logger.warning(f"Error closing search session: {e}")
                print(f"⚠️ Error closing search session: {e}")
        
        # Close bot connection and exit
        logger.info("Closing bot connection")
        await bot.close()
        
        # Force exit the script
        import sys
        sys.exit(0)
    else:
        logger.warning(f"Non-admin user {ctx.author.id} attempted shutdown command")
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
    logger.info(f"Restart command called by user {ctx.author.id}")
    
    if ctx.author.guild_permissions.administrator:
        logger.info(f"Admin permission verified for user {ctx.author.id}, initiating restart")
        
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
            logger.warning("AI response failed for restart, using fallback")
            restart_responses = persona_manager.get_activity_response("admin", "restart")
            if isinstance(restart_responses, list):
                fallback = random.choice(restart_responses)
            else:
                fallback = restart_responses
            await ctx.send(fallback)
        
        print(f"Bot restart requested by {ctx.author}")
        
        # Save any pending data and close search session
        social.save_user_data()
        logger.info("User data saved before restart")
        
        if search:
            try:
                await search.close_session()
                logger.info("Search session closed")
            except Exception as e:
                logger.warning(f"Error closing search session: {e}")
                print(f"⚠️ Error closing search session: {e}")
        
        # Close bot connection
        logger.info("Closing bot connection for restart")
        await bot.close()
        
        # Restart the script
        import os
        import sys
        print("Restarting bot...")
        logger.info("Restarting bot process")
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        logger.warning(f"Non-admin user {ctx.author.id} attempted restart command")
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
    logger.info(f"API status command called by user {ctx.author.id}")
    
    if ctx.author.guild_permissions.administrator:
        logger.info(f"Admin permission verified for user {ctx.author.id}")
        status = api_manager.get_status()
        logger.info(f"API status retrieved, total keys: {status['total_keys']}")
        
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
        logger.info(f"API status embed sent to user {ctx.author.id}")
    else:
        logger.warning(f"Non-admin user {ctx.author.id} attempted api_status command")
        # Fallback to persona card response
        fallback = persona_manager.get_activity_response("admin", "no_permission")
        await ctx.send(fallback)

@bot.event
async def on_command_error(ctx, error):
    """Global error handler for commands"""
    logger.error(f"Command error from user {ctx.author.id} in {ctx.command}: {str(error)}")
    
    if isinstance(error, commands.MissingRequiredArgument):
        # Handle missing arguments with persona response
        logger.warning(f"Missing required argument: {error.param.name}")
        await ctx.send(personality.get_missing_args_response() + f" You're missing: {error.param.name}")
    elif isinstance(error, commands.CommandNotFound):
        # Ignore command not found errors (don't spam chat)
        logger.debug("Command not found error ignored")
        pass
    elif isinstance(error, discord.Forbidden):
        # Bot doesn't have permissions - try to DM user if possible
        logger.warning(f"Forbidden action, attempting DM to user {ctx.author.id}")
        try:
            permissions_config = persona_manager.persona.get("activity_responses", {}).get("permissions", {})
            message = permissions_config.get("no_send_permission", "I don't have permission to send messages!")
            await ctx.author.send(message)
        except (discord.Forbidden, discord.HTTPException):
            logger.warning(f"Could not DM user {ctx.author.id} about permission error")
            pass  # Can't DM either, give up silently
    else:
        # For other errors, send a generic tsundere error message
        logger.error(f"Unhandled command error: {type(error).__name__}: {str(error)}")
        try:
            await ctx.send(personality.get_error_response(error))
        except (discord.Forbidden, discord.HTTPException):
            logger.error(f"Could not send error response to user {ctx.author.id}")
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
        token = os.getenv('DISCORD_BOT_TOKEN')
        if not token:
            print("❌ Error: DISCORD_BOT_TOKEN environment variable not set!")
            print("📋 Please create a .env file with your Discord bot token.")
            print("📝 You can copy .env.example and fill in your values.")
            sys.exit(1)
        
        bot.run(token)
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