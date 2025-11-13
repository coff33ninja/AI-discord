import discord
from discord.ext import commands
import os
import asyncio
import random
from datetime import datetime
from dotenv import load_dotenv

# Import our tsundere modules
# Removed: from modules.personality import TsunderePersonality - now using persona_manager
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
from modules.ai_database import initialize_ai_database, save_ai_conversation, ai_db
from modules.time_utilities import initialize_time_utilities, time_utils

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
# Removed: personality = TsunderePersonality() - now using persona_manager for all responses
utilities = None  # Will be initialized after model is ready
games = TsundereGames()
# Inject api_manager early so commands that prefer AI can use it immediately
try:
    games.set_api_manager(api_manager)
    games.set_ai_db(ai_db)
    logger.info("Pre-wired games with api_manager and ai_db at module import time")
except Exception:
    logger.warning("Failed to pre-wire games with api_manager or ai_db; will attempt again on_ready")
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
    
    # Initialize AI database
    logger.info("Initializing AI database")
    print("🗄️ Initializing AI database...")
    try:
        await initialize_ai_database()
        logger.info("AI database initialized successfully")
        print("✅ AI database ready!")
    except Exception as e:
        logger.error(f"Failed to initialize AI database: {e}")
        print(f"❌ AI database initialization failed: {e}")

    # Inject dependencies into games module (so games can use AI/search/DB)
    try:
        games.set_api_manager(api_manager)
        games.set_search(search)
        games.set_ai_db(ai_db)
        logger.info("Injected api_manager, search, and ai_db into games module")
        print("🔌 Games module wired to AI/search/DB")
    except Exception as e:
        logger.warning(f"Failed to inject dependencies into games: {e}")
    
    # Initialize time-based utilities
    logger.info("Initializing time-based utilities")
    print("⏰ Initializing time-based utilities...")
    try:
        await initialize_time_utilities(bot)
        logger.info("Time-based utilities initialized successfully")
        print("✅ Time utilities ready!")
    except Exception as e:
        logger.error(f"Failed to initialize time utilities: {e}")
        print(f"❌ Time utilities initialization failed: {e}")
    
    # Print API manager status
    status = api_manager.get_status()
    logger.info(f"API manager initialized: {status['total_keys']} keys, current key #{status['current_key']}")
    print(f"🔑 Using {status['total_keys']} API key(s), currently on key #{status['current_key']}")
    
    # Send startup message to subscribed channels
    try:
        event_subscriptions = await time_utils.get_subscriptions_by_type("events")
        logger.info(f"Found {len(event_subscriptions)} channels subscribed to events")
        
        for sub in event_subscriptions:
            try:
                channel = bot.get_channel(int(sub['channel_id']))
                if channel:
                    await channel.send("✅ **Bot is starting up!** I'm back online and ready to help!")
                    logger.info(f"Sent startup message to channel {sub['channel_id']}")
            except Exception as e:
                logger.warning(f"Error sending startup message to channel {sub['channel_id']}: {e}")
    except Exception as e:
        logger.warning(f"Error getting event subscriptions for startup message: {e}")
    
    # Set bot status with fallback using dynamic bot name
    try:
        bot_name = persona_manager.get_name()
        status_template = persona_manager.persona.get("activity_responses", {}).get("bot_status", "{bot_name} ready to help! | Use !help_ai for commands")
        # If the status template doesn't contain {bot_name}, use it as-is for backward compatibility
        if "{bot_name}" in status_template:
            status_text = status_template.format(bot_name=bot_name)
        else:
            status_text = status_template
    except Exception:
        # Fallback if persona manager fails
        bot_name = "Discord AI"  # Fallback name
        status_text = f"{bot_name} ready to help! | Use !help_ai for commands"
    
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
    import time
    start_time = time.time()
    
    try:
        logger.info(f"AI command called by user {ctx.author.id}, question: {question[:100]}")
        
        # Update social interaction
        social.update_interaction(ctx.author.id)
        
        # Show typing indicator
        async with ctx.typing():
            # Get conversation history for context
            try:
                user_prefs = await ai_db.get_user_preferences(str(ctx.author.id))
                memory_limit = user_prefs.get('conversation_memory', 5)
                conversation_history = await ai_db.get_conversation_history(
                    str(ctx.author.id), 
                    limit=memory_limit,
                    channel_id=str(ctx.channel.id)
                )
                logger.info(f"Retrieved {len(conversation_history)} previous conversations for context")
                if conversation_history:
                    print(f"🧠 Memory: Found {len(conversation_history)} previous conversations")
                    # Debug: Show what conversations were found
                    for i, conv in enumerate(conversation_history[-2:]):
                        print(f"🧠 Memory {i+1}: User: {conv['message_content'][:50]}...")
                        print(f"🧠 Memory {i+1}: Bot: {conv['ai_response'][:50]}...")
                else:
                    print("🧠 Memory: No previous conversations found")
            except Exception as e:
                logger.warning(f"Failed to retrieve conversation history: {e}")
                conversation_history = []
            
            # Check if this question would benefit from web search
            needs_search = await should_search_web(question)
            logger.info(f"Search needed for question: {needs_search}")
            
            model_used = "gemini-pro"
            tokens_used = 0
            
            if needs_search and search is not None:
                logger.info(f"Performing web search for: {question}")
                print(f"🔍 AI detected search need for: {question}")
                
                # Extract search terms from the question
                search_query = await extract_search_terms(question)
                logger.info(f"Extracted search terms: {search_query}")
                print(f"🎯 Extracted search terms: {search_query}")
                
                # Get search results
                search_results = await search.search_duckduckgo(search_query)
                
                # Create conversation context
                context_text = ""
                if conversation_history:
                    context_text = "\n\nPrevious conversation context:\n"
                    for conv in conversation_history[-3:]:  # Last 3 conversations for context
                        context_text += f"User: {conv['message_content'][:100]}...\n"
                        context_text += f"You: {conv['ai_response'][:100]}...\n"
                
                # Create enhanced prompt with search results using persona card
                try:
                    # Get relationship level for user-aware prompting if available
                    try:
                        user_rel = social.get_user_relationship(ctx.author.id)
                        relationship_level = user_rel.get('relationship_level', 'stranger')
                    except Exception:
                        relationship_level = 'stranger'

                    user_question = f"""The user {ctx.author.display_name} asked: \"{question}\"\n{context_text}\nI searched the web and found this information:\n{search_results}\n\nYour task:\n1. Answer using both your knowledge AND the search results\n2. Use the conversation history to provide continuity and remember what you've discussed\n3. If the search results are relevant, incorporate them naturally\n4. If the search results aren't helpful, rely on your knowledge but mention you tried to search\n5. Keep your response under 1800 characters for Discord"""

                    enhanced_prompt = persona_manager.get_ai_prompt(user_question, relationship_level)
                except Exception:
                    # Fallback to generic prompt if persona manager fails
                    enhanced_prompt = f"""You are a helpful AI assistant. The user {ctx.author.display_name} asked: \"{question}\"\n{context_text}\nI found this information:\n{search_results}\n\nPlease answer the user's question using both your knowledge and these search results. Keep your response under 1800 characters."""

                response_text = await api_manager.generate_content(enhanced_prompt)
                model_used = "gemini-pro-search"
                tokens_used = len(enhanced_prompt.split()) + (len(response_text.split()) if response_text else 0)
                
                if response_text:
                    logger.info("Enhanced AI response generated successfully")
                    print(f"🤖 Enhanced AI response with search: {response_text[:100]}...")
                else:
                    # Fallback to normal AI if enhanced fails
                    logger.warning("Enhanced AI failed, falling back to normal response")
                    print("⚠️ Enhanced AI failed, falling back to normal response")
                    tsundere_prompt = create_memory_enhanced_prompt(question, ctx.author.display_name, conversation_history)
                    response_text = await api_manager.generate_content(tsundere_prompt)
                    model_used = "gemini-pro"
                    tokens_used = len(tsundere_prompt.split()) + (len(response_text.split()) if response_text else 0)
            else:
                # Normal AI response without search
                logger.info("Generating normal AI response without search")
                tsundere_prompt = create_memory_enhanced_prompt(question, ctx.author.display_name, conversation_history)
                response_text = await api_manager.generate_content(tsundere_prompt)
                tokens_used = len(tsundere_prompt.split()) + (len(response_text.split()) if response_text else 0)
            
            if response_text is None:
                # All API attempts failed
                logger.error("All API attempts failed for AI command")
                timeout_response = persona_manager.get_timeout_response("AI")
                await ctx.send(timeout_response)
                return
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Save conversation to database
            try:
                conversation_id = await save_ai_conversation(
                    user_id=str(ctx.author.id),
                    message=question,
                    response=response_text,
                    model=model_used,
                    tokens_used=tokens_used,
                    response_time=response_time,
                    channel_id=str(ctx.channel.id),
                    guild_id=str(ctx.guild.id) if ctx.guild else None,
                    context_data={
                        'username': ctx.author.display_name,
                        'search_used': needs_search,
                        'command_used': ctx.invoked_with
                    }
                )
                logger.info(f"Conversation saved to database with ID: {conversation_id}")
                
                # Track model performance
                await ai_db.track_model_performance(model_used, tokens_used, response_time, True)
                
            except Exception as db_error:
                logger.error(f"Failed to save conversation to database: {db_error}")
            
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
        
        # Track failed request
        try:
            response_time = time.time() - start_time
            await ai_db.track_model_performance("gemini-pro", 0, response_time, False)
        except Exception:
            pass
        
        await ctx.send(persona_manager.get_error_response("ai_command_error", error=str(e)))

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

def create_memory_enhanced_prompt(question, username, conversation_history):
    """Create a prompt that includes conversation history for memory"""
    base_prompt = persona_manager.create_ai_prompt(question)
    
    if not conversation_history:
        return base_prompt
    
    # Add conversation context
    context_text = f"\n\nRECENT CONVERSATION HISTORY with {username}:\n"
    for conv in conversation_history[-3:]:  # Last 3 conversations for context
        context_text += f"User ({username}): {conv['message_content'][:150]}\n"
        context_text += f"You: {conv['ai_response'][:150]}\n\n"
    
    context_text += "IMPORTANT: Remember this conversation history and maintain continuity. You know this user from previous interactions.\n"
    
    # Insert context into the base prompt before the user question
    enhanced_prompt = base_prompt.replace(
        f'USER QUESTION: {question}',
        f'{context_text}\nUSER QUESTION: {question}'
    )
    
    # Debug: Check if replacement worked
    if context_text in enhanced_prompt:
        print("🧠 Memory: Context successfully added to prompt")
    else:
        print("🧠 Memory: WARNING - Context not found in enhanced prompt")
        print(f"🧠 Memory: Looking for: 'USER QUESTION: {question}'")
        print(f"🧠 Memory: Base prompt preview: {base_prompt[:200]}...")
    
    return enhanced_prompt

@bot.command(name='help_ai', aliases=['commands'])
async def help_command(ctx):
    """Show bot help"""
    logger.info(f"Help command called by user {ctx.author.id}")
    
    # Get help command configuration with fallbacks
    try:
        help_config = persona_manager.persona.get("activity_responses", {}).get("help_command", {})
        bot_name = persona_manager.get_name()
    except Exception:
        help_config = {}
        bot_name = "Discord AI"
    
    # Ensure we have fallback values for all help config fields with dynamic bot name
    help_config = {
        "title": help_config.get("title", f"{bot_name} - Available Commands"),
        "description": help_config.get("description", f"Here are the commands you can use with {bot_name}:"),
        "footer": help_config.get("footer", f"Use these commands to interact with {bot_name}!")
    }
    
    # Use ResponseHandler to create a formatted embed
    embed = ResponseHandler.create_info_embed(
        title=help_config.get("title", "Available Commands"),
        description=help_config.get("description", "Here are the commands I can help you with:"),
        fields=[
            {
                'name': "**AI & Chat**",
                'value': "`!ai <question>` (or `!ask`, `!chat`) - Ask me anything\n`!compliment` - Send a compliment\n`!mood` - Check my current mood\n`!relationship` - See your relationship status\n`!memory [number]` - View/adjust conversation memory",
                'inline': False
            },
            {
                'name': "**Utilities**",
                'value': "`!time` - Get current time\n`!calc <math>` - Calculator\n`!dice [sides]` - Roll dice\n`!flip` - Flip a coin\n`!weather <city>` - Real weather info\n`!fact` - Random fact\n`!joke` - Random joke\n`!catfact` - Cat facts\n`!stats` - Your usage statistics",
                'inline': False
            },
            {
                'name': "**Search**",
                'value': "`!search <query>` (or `!google`, `!find`) - Search the web\n`!websearch <query>` (or `!web`) - Alternative web search",
                'inline': False
            },
            {
                'name': "**Games**",
                'value': "`!game guess [max]` - Number guessing\n`!guess <number>` - Make a guess\n`!rps <choice>` (or `!rock`, `!paper`, `!scissors`) - Rock Paper Scissors\n`!8ball <question>` - Magic 8-ball\n`!trivia` - Start a trivia question (30 seconds to answer)\n`!answer <answer>` - Answer the current trivia question",
                'inline': False
            },
            {
                'name': "**Server Actions** (with permissions)",
                'value': "`!mention @user [message]` - Mention someone\n`!create_role <name> [color]` - Create a role\n`!give_role @user <role>` - Give role to user\n`!remove_role @user <role>` - Remove role\n`!kick @user [reason]` - Kick user\n`!create_channel <name> [type]` - Create channel\n`!send_to #channel <message>` - Send message to channel",
                'inline': False
            },
            {
                'name': "**Time & Reminders**",
                'value': "`!remind <time> to <message>` - Set a reminder\n`!reminders` - List your reminders\n`!cancelreminder <id>` - Cancel a reminder\n`!subscribe <feature>` - Subscribe to daily features\n`!unsubscribe <feature>` - Unsubscribe from features\n`!subscriptions` - List your subscriptions",
                'inline': False
            },
            {
                'name': "**Admin Commands** (admin only)",
                'value': "`!reload_persona` - Reload personality config\n`!persona_health` - Check persona configuration health\n`!persona_report` - Generate detailed persona report\n`!api_status` - Check API key status\n`!ai_analytics` - View AI usage stats\n`!shutdown` (or `!kill`, `!stop`) - Shutdown bot\n`!restart` (or `!reboot`) - Restart bot",
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
            
            # Update social interaction
            social.update_interaction(message.author.id)
            
            # Get conversation history for context
            try:
                conversation_history = await ai_db.get_conversation_history(
                    str(message.author.id), 
                    limit=3,
                    channel_id=str(message.channel.id)
                )
            except Exception:
                conversation_history = []
            
            # Generate AI response for being mentioned with memory
            mention_text = f"mentioned me in chat: '{message.content}'"
            prompt = create_memory_enhanced_prompt(mention_text, message.author.display_name, conversation_history)
            response = await api_manager.generate_content(prompt)
            
            # Save the mention interaction
            if response:
                try:
                    await save_ai_conversation(
                        user_id=str(message.author.id),
                        message=message.content,
                        response=response,
                        model="gemini-pro-mention",
                        channel_id=str(message.channel.id),
                        guild_id=str(message.guild.id) if message.guild else None,
                        context_data={
                            'username': message.author.display_name,
                            'interaction_type': 'mention'
                        }
                    )
                except Exception as db_error:
                    logger.error(f"Failed to save mention conversation: {db_error}")
            
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
        fallback = persona_manager.get_error_response("ai_unavailable")
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
        fallback = persona_manager.get_error_response("ai_unavailable")
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
        try:
            fallback = persona_manager.get_relationship_response(relationship_level, "greeting")
        except Exception:
            fallback = persona_manager.get_response("greeting")
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
        response = await utilities.get_weather(location, str(ctx.author.id))
    await ctx.send(response)

@bot.command(name='fact')
async def get_fact(ctx):
    """Get a random fact"""
    logger.info(f"Fact command called by user {ctx.author.id}")
    async with ctx.typing():
        response = await utilities.get_random_fact(str(ctx.author.id))
    await ctx.send(response)

@bot.command(name='joke')
async def get_joke(ctx):
    """Get a random joke"""
    logger.info(f"Joke command called by user {ctx.author.id}")
    async with ctx.typing():
        response = await utilities.get_joke(str(ctx.author.id))
    await ctx.send(response)

@bot.command(name='catfact')
async def get_cat_fact(ctx):
    """Get a random cat fact"""
    logger.info(f"Cat fact command called by user {ctx.author.id}")
    async with ctx.typing():
        response = await utilities.get_cat_fact()
    await ctx.send(response)

@bot.command(name='stats', aliases=['mystats', 'usage'])
async def get_user_stats(ctx):
    """Get your personal usage statistics"""
    logger.info(f"Stats command called by user {ctx.author.id}")
    async with ctx.typing():
        response = await utilities.get_usage_stats(str(ctx.author.id))
    await ctx.send(response)

# Time-based Commands
@bot.command(name='remind', aliases=['reminder', 'remindme'])
async def set_reminder(ctx, *, reminder_input):
    """Set a reminder - Usage: !remind in 5 minutes take a break"""
    try:
        logger.info(f"Remind command called by user {ctx.author.id}")
        
        # Parse the input to separate time and message
        parts = reminder_input.split(" to ", 1)
        if len(parts) != 2:
            parts = reminder_input.split(" ", 3)
            if len(parts) < 4:
                await ctx.send(persona_manager.get_validation_response("reminder_format"))
                return
            
            time_part = " ".join(parts[:3])  # "in 5 minutes" or "at 3pm"
            message_part = " ".join(parts[3:])
        else:
            time_part = parts[0]
            message_part = parts[1]
        
        # Parse the time
        remind_time = time_utils.parse_time_input(time_part)
        if not remind_time:
            await ctx.send(persona_manager.get_validation_response("time_format"))
            return
        
        # Set the reminder
        reminder_id = await time_utils.set_reminder(
            str(ctx.author.id),
            str(ctx.channel.id),
            str(ctx.guild.id) if ctx.guild else None,
            message_part,
            remind_time
        )
        
        # Create tsundere response from persona card
        time_str = remind_time.strftime("%I:%M %p on %B %d")
        try:
            response = persona_manager.get_activity_response("reminders", "reminder_created",
                                                          message=message_part, time=time_str, reminder_id=reminder_id)
        except Exception:
            response = f"Reminder set for '{message_part}' at {time_str}. (Reminder ID: {reminder_id})"

        await ctx.send(response)
        logger.info(f"Reminder set for user {ctx.author.id}: {message_part} at {remind_time}")
        
    except Exception as e:
        logger.error(f"Error in remind command: {e}")
        await ctx.send(persona_manager.get_error_response("reminder_error", error=str(e)))

@bot.command(name='reminders', aliases=['myreminders', 'listreminders'])
async def list_reminders(ctx):
    """List your active reminders"""
    try:
        logger.info(f"Reminders command called by user {ctx.author.id}")
        
        reminders = await time_utils.get_user_reminders(str(ctx.author.id))
        
        if not reminders:
            try:
                no_reminders_msg = persona_manager.get_activity_response("reminders", "no_reminders")
            except Exception:
                no_reminders_msg = "You don't have any active reminders."
            await ctx.send(no_reminders_msg)
            return
        
        # Use persona-provided titles/descriptions when available
        reminders_cfg = persona_manager.persona.get("activity_responses", {}).get("reminders", {})
        embed_title = reminders_cfg.get("list_title", "📝 Your Active Reminders")
        embed_description = reminders_cfg.get("list_description", "Here are your active reminders:")

        embed = discord.Embed(
            title=embed_title,
            description=embed_description,
            color=0x00ff00
        )
        
        for reminder in reminders[:10]:  # Limit to 10 reminders
            remind_time = datetime.fromisoformat(reminder['remind_time'])
            time_str = remind_time.strftime("%I:%M %p on %B %d")
            
            embed.add_field(
                name=f"ID: {reminder['id']}",
                value=f"**Message:** {reminder['reminder_text']}\n**Time:** {time_str}",
                inline=False
            )
        
        if len(reminders) > 10:
            embed.set_footer(text=f"Showing 10 of {len(reminders)} reminders")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error in reminders command: {e}")
        await ctx.send(persona_manager.get_error_response("reminders_error", error=str(e)))

@bot.command(name='cancelreminder', aliases=['deletereminder', 'removereminder'])
async def cancel_reminder(ctx, reminder_id: int):
    """Cancel a specific reminder by ID"""
    try:
        logger.info(f"Cancel reminder command called by user {ctx.author.id} for reminder {reminder_id}")
        
        success = await time_utils.cancel_reminder(reminder_id, str(ctx.author.id))
        
        if success:
            try:
                msg = persona_manager.get_activity_response("reminders", "reminder_cancelled", reminder_id=reminder_id)
            except Exception:
                msg = persona_manager.get_success_response("reminder_cancelled", reminder_id=reminder_id)
            await ctx.send(msg)
        else:
            try:
                msg = persona_manager.get_activity_response("reminders", "reminder_not_found", reminder_id=reminder_id)
            except Exception:
                msg = persona_manager.get_error_response("reminder_not_found", reminder_id=reminder_id)
            await ctx.send(msg)
        
    except Exception as e:
        logger.error(f"Error in cancel reminder command: {e}")
        await ctx.send(persona_manager.get_error_response("cancel_reminder_error", error=str(e)))

@bot.command(name='subscribe')
async def subscribe_feature(ctx, feature_type: str):
    """Subscribe to time-based features like daily facts, jokes, etc."""
    try:
        logger.info(f"Subscribe command called by user {ctx.author.id} for {feature_type}")
        
        valid_features = ['daily_fact', 'daily_joke', 'weekly_stats', 'mood_check', 'events']
        
        if feature_type not in valid_features:
            await ctx.send(persona_manager.get_validation_response("invalid_feature", features=', '.join(valid_features)))
            return
        
        success = await time_utils.subscribe_to_feature(
            str(ctx.author.id),
            str(ctx.channel.id),
            str(ctx.guild.id) if ctx.guild else None,
            feature_type
        )
        
        if success:
            feature_names = {
                'daily_fact': 'daily facts',
                'daily_joke': 'daily jokes',
                'weekly_stats': 'weekly statistics',
                'mood_check': 'mood check-ins',
                'events': 'bot startup and shutdown notifications'
            }
            feature_name = feature_names.get(feature_type, feature_type)
            try:
                msg = persona_manager.get_activity_response("subscriptions", "subscribed", feature_name=feature_name)
            except Exception:
                msg = persona_manager.get_success_response("subscription_added", feature_name=feature_name)
            await ctx.send(msg)
        else:
            await ctx.send(persona_manager.get_error_response("subscription_error"))
        
    except Exception as e:
        logger.error(f"Error in subscribe command: {e}")
        await ctx.send(persona_manager.get_error_response("subscribe_error", error=str(e)))

@bot.command(name='unsubscribe')
async def unsubscribe_feature(ctx, feature_type: str):
    """Unsubscribe from time-based features"""
    try:
        logger.info(f"Unsubscribe command called by user {ctx.author.id} for {feature_type}")
        
        success = await time_utils.unsubscribe_from_feature(
            str(ctx.author.id),
            str(ctx.channel.id),
            feature_type
        )
        
        if success:
            try:
                msg = persona_manager.get_activity_response("subscriptions", "unsubscribed", feature_name=feature_type)
            except Exception:
                msg = persona_manager.get_success_response("subscription_removed", feature_name=feature_type)
            await ctx.send(msg)
        else:
            try:
                msg = persona_manager.get_activity_response("subscriptions", "not_subscribed", feature_name=feature_type)
            except Exception:
                msg = persona_manager.get_error_response("not_subscribed", feature_name=feature_type)
            await ctx.send(msg)
        
    except Exception as e:
        logger.error(f"Error in unsubscribe command: {e}")
        await ctx.send(persona_manager.get_error_response("unsubscribe_error", error=str(e)))

@bot.command(name='subscriptions', aliases=['mysubscriptions'])
async def list_subscriptions(ctx):
    """List your active subscriptions"""
    try:
        logger.info(f"Subscriptions command called by user {ctx.author.id}")
        
        subscriptions = await time_utils.get_user_subscriptions(str(ctx.author.id))
        
        if not subscriptions:
            try:
                msg = persona_manager.get_activity_response("subscriptions", "no_subscriptions")
            except Exception:
                msg = "You don't have any active subscriptions."
            await ctx.send(msg)
            return
        
        embed = discord.Embed(
            title="📋 Your Subscriptions",
            description="Here's what you're subscribed to:",
            color=0x00ff00
        )
        
        for sub in subscriptions:
            embed.add_field(
                name=sub['subscription_type'].replace('_', ' ').title(),
                value=f"Channel: <#{sub['channel_id']}>\nActive since: {sub['created_at'][:10]}",
                inline=True
            )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error in subscriptions command: {e}")
        await ctx.send(persona_manager.get_error_response("subscriptions_error", error=str(e)))

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
        await ctx.send(persona_manager.get_error_response("search_error", error=str(e)))

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
        await ctx.send(persona_manager.get_error_response("web_search_error", error=str(e)))

# Game Commands
@bot.command(name='game')
async def start_game(ctx, game_type=None, max_number: int = 100):
    """Start a game"""
    logger.info(f"Game command called by user {ctx.author.id}, type: {game_type}, max: {max_number}")
    
    if game_type is None:
        logger.warning(f"Game command missing arguments from user {ctx.author.id}")
        await ctx.send(persona_manager.get_response("missing_args") + " Try `!game guess` for number guessing!")
        return
    
    if game_type.lower() == 'guess':
        response = await games.start_number_guessing(ctx.author.id, max_number, ctx)
        await ctx.send(response)
    else:
        logger.warning(f"Unknown game type requested by user {ctx.author.id}: {game_type}")
        await ctx.send(persona_manager.get_response("missing_args") + " I only know 'guess' games right now! Try `!game guess`!")

@bot.command(name='guess')
async def make_guess(ctx, number: int):
    """Make a guess in the number game"""
    logger.info(f"Guess command called by user {ctx.author.id}, number: {number}")
    response = await games.guess_number(ctx.author.id, number, ctx)
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
        await ctx.send(persona_manager.get_response("missing_args") + " Pick rock, paper, or scissors! Try `!rps rock` or just `!rock`!")
        return
    
    response = await games.rock_paper_scissors(choice, ctx.author.id, ctx)
    await ctx.send(response)

@bot.command(name='8ball')
async def magic_8ball(ctx, *, question):
    """Ask the magic 8-ball"""
    logger.info(f"8-ball command called by user {ctx.author.id}, question: {question[:50]}")
    async with ctx.typing():
        response = await games.magic_8ball(question, ctx)
    await ctx.send(response)

@bot.command(name='trivia')
async def start_trivia(ctx, source: str = None):
    """Start a trivia game. Optional `source` can be 'db' or 'ai' to force source."""
    logger.info(f"Trivia command called by user {ctx.author.id}, source={source}")
    async with ctx.typing():
        response = await games.trivia_game(ctx.author.id, ctx, source=source)
    await ctx.send(response)

@bot.command(name='answer', aliases=['g'])
async def answer_trivia(ctx, *, answer):
    """Answer the current game question - works for trivia, number guessing, etc. Alias: !g"""
    logger.info(f"Answer command called by user {ctx.author.id}, answer: {answer[:50]}")
    response = await games.answer(ctx.author.id, answer, ctx)
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
        
        # Store old configuration for comparison and rollback
        old_name = persona_manager.get_name()
        old_persona_backup = persona_manager.persona.copy()
        
        # Validate persona card before reloading
        try:
            validation_result = persona_manager.validate_persona_completeness()
            logger.info(f"Persona validation: Valid={validation_result['valid']}, Completeness={validation_result['completeness']:.1%}")
        except Exception as e:
            logger.warning(f"Persona validation failed: {e}")
            validation_result = {"valid": False, "errors": [str(e)], "warnings": [], "completeness": 0.0}
        
        # Reload persona (this also reloads the bot name service)
        reload_success = False
        changes_made = []
        
        try:
            result = persona_manager.reload_persona()
            logger.info(f"Persona reloaded: {result}")
            reload_success = True
            
            # Check what changed
            new_name = persona_manager.get_name()
            if old_name != new_name:
                changes_made.append(f"Name: '{old_name}' → '{new_name}'")
                logger.info(f"Bot name changed from '{old_name}' to '{new_name}', updating presence")
                try:
                    # Update bot status with new name
                    bot_name = new_name
                    status_template = persona_manager.persona.get("activity_responses", {}).get("bot_status", "{bot_name} ready to help! | Use !help_ai for commands")
                    if "{bot_name}" in status_template:
                        status_text = status_template.format(bot_name=bot_name)
                    else:
                        status_text = status_template
                    await bot.change_presence(activity=discord.Game(name=status_text))
                    logger.info(f"Discord presence updated with new name: {new_name}")
                    changes_made.append("Discord presence updated")
                except Exception as e:
                    logger.error(f"Failed to update Discord presence: {e}")
                    changes_made.append(f"Discord presence update failed: {str(e)}")
            
            # Check for other personality changes
            new_personality = persona_manager.persona.get("personality", "unknown")
            old_personality = old_persona_backup.get("personality", "unknown")
            if new_personality != old_personality:
                changes_made.append(f"Personality: '{old_personality}' → '{new_personality}'")
            
            # Check response template changes
            old_templates = len(old_persona_backup.get("response_templates", {}))
            new_templates = len(persona_manager.persona.get("response_templates", {}))
            if old_templates != new_templates:
                changes_made.append(f"Response templates: {old_templates} → {new_templates}")
            
            # Validate new configuration
            new_validation = persona_manager.validate_persona_completeness()
            if new_validation["completeness"] != validation_result["completeness"]:
                changes_made.append(f"Completeness: {validation_result['completeness']:.1%} → {new_validation['completeness']:.1%}")
            
            # Create detailed result message
            if changes_made:
                result = f"Persona reloaded successfully! Changes: {', '.join(changes_made)}"
            else:
                result = "Persona reloaded (no changes detected)"
            
            # Add validation warnings if any
            if new_validation.get("warnings"):
                result += f" | Warnings: {len(new_validation['warnings'])}"
            
        except Exception as e:
            logger.error(f"Failed to reload persona: {e}")
            # Rollback to previous configuration
            try:
                persona_manager.persona = old_persona_backup
                persona_manager.bot_name_service.reload_bot_name()
                logger.info("Rolled back to previous persona configuration")
                result = f"Reload failed: {str(e)} | Rolled back to previous configuration"
            except Exception as rollback_error:
                logger.error(f"Rollback failed: {rollback_error}")
                result = f"Reload failed: {str(e)} | Rollback also failed: {str(rollback_error)}"
            
            new_name = old_name  # Keep the old name if reload failed
            reload_success = False
        
        # Get user relationship for personalized response
        user_data = social.get_user_relationship(ctx.author.id)
        relationship_level = user_data['relationship_level']
        
        # Generate comprehensive response with validation details
        try:
            # Create detailed prompt with validation info
            validation_info = ""
            if reload_success:
                current_validation = persona_manager.validate_persona_completeness()
                validation_info = f" | Validation: {current_validation['completeness']:.1%} complete"
                if current_validation.get("warnings"):
                    validation_info += f", {len(current_validation['warnings'])} warnings"
                if current_validation.get("errors"):
                    validation_info += f", {len(current_validation['errors'])} errors"
            
            prompt = persona_manager.create_ai_prompt(
                f"!reload_persona command (result: {result}{validation_info})", 
                ctx.author.display_name, relationship_level
            )
            response = await api_manager.generate_content(prompt)
            
            if response:
                await ctx.send(response)
                
                # Send additional validation details if there are warnings or errors
                if reload_success:
                    current_validation = persona_manager.validate_persona_completeness()
                    if current_validation.get("warnings") or current_validation.get("errors"):
                        details = []
                        if current_validation.get("errors"):
                            details.append(f"❌ **Errors:** {', '.join(current_validation['errors'])}")
                        if current_validation.get("warnings"):
                            details.append(f"⚠️ **Warnings:** {', '.join(current_validation['warnings'])}")
                        if current_validation.get("missing_elements"):
                            details.append(f"📋 **Missing:** {', '.join(current_validation['missing_elements'])}")
                        
                        if details:
                            await ctx.send(f"**Persona Validation Details:**\n" + "\n".join(details))
            else:
                # Fallback to persona card response
                logger.warning("AI response failed for reload_persona, using fallback")
                try:
                    if not reload_success:
                        fallback = persona_manager.get_error_response("reload_failed", result=result)
                    else:
                        fallback = persona_manager.get_activity_response("admin", "reload_success", result=result)
                except Exception:
                    if not reload_success:
                        fallback = persona_manager.get_error_response("reload_failed", result=result)
                    else:
                        fallback = persona_manager.get_success_response("configuration_reloaded", result=result)
                await ctx.send(fallback)
                
        except Exception as e:
            logger.error(f"Error generating reload response: {e}")
            # Ultimate fallback
            if not reload_success:
                await ctx.send(persona_manager.get_error_response("reload_failed", result=result))
            else:
                await ctx.send(persona_manager.get_success_response("configuration_reloaded", result=result))
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
            try:
                fallback = persona_manager.get_activity_response("admin", "no_permission")
            except Exception:
                fallback = "You don't have permission to use that command."
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
            try:
                shutdown_responses = persona_manager.get_activity_response("admin", "shutdown")
                if isinstance(shutdown_responses, list):
                    fallback = random.choice(shutdown_responses)
                else:
                    fallback = shutdown_responses
            except Exception:
                fallback = "Shutting down now. Goodbye!"
            await ctx.send(fallback)
        print(f"Bot shutdown requested by {ctx.author}")
        
        # Send shutdown message to subscribed channels
        try:
            event_subscriptions = await time_utils.get_subscriptions_by_type("events")
            logger.info(f"Sending shutdown message to {len(event_subscriptions)} subscribed channels")
            
            for sub in event_subscriptions:
                try:
                    channel = bot.get_channel(int(sub['channel_id']))
                    if channel:
                        await channel.send("🛑 **Bot is shutting down!** I'll be back online soon!")
                        logger.info(f"Sent shutdown message to channel {sub['channel_id']}")
                except Exception as e:
                    logger.warning(f"Error sending shutdown message to channel {sub['channel_id']}: {e}")
        except Exception as e:
            logger.warning(f"Error getting event subscriptions for shutdown message: {e}")
        
        # Save any pending data and close search session
        social.save_user_data()
        logger.info("User data saved before shutdown")
        
        # Close AI database
        try:
            await ai_db.close()
            logger.info("AI database closed")
        except Exception as e:
            logger.warning(f"Error closing AI database: {e}")
            print(f"⚠️ Error closing AI database: {e}")
        
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
            try:
                fallback = persona_manager.get_activity_response("admin", "no_permission")
            except Exception:
                fallback = "You don't have permission to use that command."
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
            try:
                restart_responses = persona_manager.get_activity_response("admin", "restart")
                if isinstance(restart_responses, list):
                    fallback = random.choice(restart_responses)
                else:
                    fallback = restart_responses
            except Exception:
                fallback = "Restarting the system now. I'll be back shortly!"
            await ctx.send(fallback)
        
        print(f"Bot restart requested by {ctx.author}")
        
        # Save any pending data and close search session
        social.save_user_data()
        logger.info("User data saved before restart")
        
        # Close AI database
        try:
            await ai_db.close()
            logger.info("AI database closed")
        except Exception as e:
            logger.warning(f"Error closing AI database: {e}")
            print(f"⚠️ Error closing AI database: {e}")
        
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
            try:
                fallback = persona_manager.get_activity_response("admin", "no_permission")
            except Exception:
                fallback = "You don't have permission to use that command."
            await ctx.send(fallback)

@bot.command(name='persona_health', aliases=['persona_status', 'personality_check'])
async def persona_health(ctx):
    """Check persona card health and completeness (admin only)"""
    logger.info(f"Persona health command called by user {ctx.author.id}")
    
    if ctx.author.guild_permissions.administrator:
        logger.info(f"Admin permission verified for user {ctx.author.id}")
        
        try:
            # Get comprehensive validation report
            validation = persona_manager.validate_persona_completeness()
            
            # Create detailed health report
            embed = discord.Embed(
                title=f"🔍 {persona_manager.get_name()} - Persona Health Report",
                color=0x00ff00 if validation["valid"] else 0xff0000
            )
            
            # Basic info
            embed.add_field(
                name="📊 Overall Status",
                value=f"**Valid:** {'✅ Yes' if validation['valid'] else '❌ No'}\n"
                      f"**Completeness:** {validation['completeness']:.1%}\n"
                      f"**Name:** {persona_manager.get_name()}\n"
                      f"**Personality:** {persona_manager.persona.get('personality', 'Unknown')}",
                inline=False
            )
            
            # Configuration details
            config_details = []
            response_templates = len(persona_manager.persona.get("response_templates", {}))
            activity_responses = len(persona_manager.persona.get("activity_responses", {}))
            relationship_responses = len(persona_manager.persona.get("relationship_responses", {}))
            speech_patterns = len(persona_manager.persona.get("speech_patterns", {}))
            
            config_details.append(f"Response Templates: {response_templates}")
            config_details.append(f"Activity Responses: {activity_responses}")
            config_details.append(f"Relationship Responses: {relationship_responses}")
            config_details.append(f"Speech Patterns: {speech_patterns}")
            
            embed.add_field(
                name="⚙️ Configuration",
                value="\n".join(config_details),
                inline=True
            )
            
            # Issues and warnings
            issues = []
            if validation.get("errors"):
                issues.extend([f"❌ {error}" for error in validation["errors"]])
            if validation.get("warnings"):
                issues.extend([f"⚠️ {warning}" for warning in validation["warnings"]])
            
            if issues:
                embed.add_field(
                    name="🚨 Issues Found",
                    value="\n".join(issues[:5]) + (f"\n... and {len(issues)-5} more" if len(issues) > 5 else ""),
                    inline=False
                )
            
            # Missing elements
            if validation.get("missing_elements"):
                missing = validation["missing_elements"]
                embed.add_field(
                    name="📋 Missing Elements",
                    value=", ".join(missing[:10]) + ("..." if len(missing) > 10 else ""),
                    inline=False
                )
            
            # Recommendations
            recommendations = []
            if validation["completeness"] < 0.5:
                recommendations.append("Consider adding more response templates for better personality")
            if not persona_manager.persona.get("speech_patterns"):
                recommendations.append("Add speech patterns for more natural responses")
            if validation.get("errors"):
                recommendations.append("Fix configuration errors for optimal performance")
            
            if recommendations:
                embed.add_field(
                    name="💡 Recommendations",
                    value="\n".join(recommendations),
                    inline=False
                )
            
            embed.set_footer(text=f"Persona file: {persona_manager.bot_name_service.get_persona_card_path()}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in persona health check: {e}")
            await ctx.send(persona_manager.get_error_response("health_check_error", error=str(e)))
    else:
        logger.warning(f"Non-admin user {ctx.author.id} attempted persona_health command")
        await ctx.send(persona_manager.get_permission_response("admin_command"))

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
        try:
            fallback = persona_manager.get_activity_response("admin", "no_permission")
        except Exception:
            fallback = "You don't have permission to use that command."
        await ctx.send(fallback)

@bot.command(name='memory', aliases=['memory_settings'])
async def memory_settings(ctx, memory_length: int = None):
    """View or adjust AI memory settings"""
    logger.info(f"Memory settings command called by user {ctx.author.id}")
    
    try:
        user_prefs = await ai_db.get_user_preferences(str(ctx.author.id))
        current_memory = user_prefs.get('conversation_memory', 5)
        
        if memory_length is None:
            # Just show current settings
            embed = discord.Embed(
                title="🧠 Memory Settings",
                description=f"Your current conversation memory: **{current_memory}** messages",
                color=0x00ff00
            )
            embed.add_field(
                name="How it works",
                value="I remember our last few conversations to provide better context.\n"
                      "Higher numbers = more memory but slower responses.\n"
                      "Range: 1-10 messages",
                inline=False
            )
            embed.add_field(
                name="Change Settings",
                value="Use `!memory <number>` to adjust\nExample: `!memory 8`",
                inline=False
            )
            await ctx.send(embed=embed)
        else:
            # Update memory settings
            if 1 <= memory_length <= 10:
                await ai_db.update_user_preferences(str(ctx.author.id), {
                    'conversation_memory': memory_length
                })
                
                # Generate AI response about the memory change
                prompt = create_memory_enhanced_prompt(
                    f"changed memory settings to {memory_length} messages", 
                    ctx.author.display_name, 
                    []
                )
                response = await api_manager.generate_content(prompt)
                
                if response:
                    await ctx.send(response)
                else:
                    await ctx.send(f"✅ Memory updated to {memory_length} messages!")
                
                logger.info(f"User {ctx.author.id} updated memory to {memory_length}")
            else:
                await ctx.send("❌ Memory length must be between 1 and 10 messages!")
                
    except Exception as e:
        logger.error(f"Error in memory settings: {e}")
        await ctx.send(f"❌ Error updating memory settings: {e}")

@bot.command(name='persona_report', aliases=['personality_report'])
async def persona_report(ctx):
    """Generate detailed persona usage and fallback report (admin only)"""
    logger.info(f"Persona report command called by user {ctx.author.id}")
    
    if ctx.author.guild_permissions.administrator:
        logger.info(f"Admin permission verified for user {ctx.author.id}")
        
        try:
            # Get validation report
            validation = persona_manager.validate_persona_completeness()
            
            # Create comprehensive report
            report_lines = []
            report_lines.append(f"# {persona_manager.get_name()} - Persona Report")
            report_lines.append(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append("")
            
            # Validation summary
            report_lines.append("## Validation Summary")
            report_lines.append(f"- **Status:** {'✅ Valid' if validation['valid'] else '❌ Invalid'}")
            report_lines.append(f"- **Completeness:** {validation['completeness']:.1%}")
            report_lines.append(f"- **Errors:** {len(validation.get('errors', []))}")
            report_lines.append(f"- **Warnings:** {len(validation.get('warnings', []))}")
            report_lines.append("")
            
            # Configuration details
            report_lines.append("## Configuration Details")
            persona_data = persona_manager.persona
            report_lines.append(f"- **Name:** {persona_data.get('name', 'Not set')}")
            report_lines.append(f"- **Personality:** {persona_data.get('personality', 'Not set')}")
            report_lines.append(f"- **Description:** {persona_data.get('description', 'Not set')[:100]}...")
            report_lines.append(f"- **Response Templates:** {len(persona_data.get('response_templates', {}))}")
            report_lines.append(f"- **Activity Responses:** {len(persona_data.get('activity_responses', {}))}")
            report_lines.append(f"- **Relationship Responses:** {len(persona_data.get('relationship_responses', {}))}")
            report_lines.append(f"- **Speech Patterns:** {len(persona_data.get('speech_patterns', {}))}")
            report_lines.append("")
            
            # Issues
            if validation.get("errors") or validation.get("warnings"):
                report_lines.append("## Issues")
                for error in validation.get("errors", []):
                    report_lines.append(f"- ❌ **Error:** {error}")
                for warning in validation.get("warnings", []):
                    report_lines.append(f"- ⚠️ **Warning:** {warning}")
                report_lines.append("")
            
            # Missing elements
            if validation.get("missing_elements"):
                report_lines.append("## Missing Elements")
                for element in validation["missing_elements"]:
                    report_lines.append(f"- 📋 {element}")
                report_lines.append("")
            
            # Recommendations
            recommendations = []
            if validation["completeness"] < 0.8:
                recommendations.append("Consider expanding persona configuration for richer personality")
            if not persona_data.get("speech_patterns"):
                recommendations.append("Add speech patterns for more natural conversation flow")
            if len(persona_data.get("response_templates", {})) < 5:
                recommendations.append("Add more response templates for varied reactions")
            
            if recommendations:
                report_lines.append("## Recommendations")
                for rec in recommendations:
                    report_lines.append(f"- 💡 {rec}")
                report_lines.append("")
            
            # Create the report text
            report_text = "\n".join(report_lines)
            
            # Send as file if too long, otherwise as message
            if len(report_text) > 1900:
                import io
                report_file = io.StringIO(report_text)
                file = discord.File(report_file, filename=f"{persona_manager.get_name()}_persona_report.md")
                await ctx.send("📊 **Persona Report Generated**", file=file)
            else:
                await ctx.send(f"```markdown\n{report_text}\n```")
                
        except Exception as e:
            logger.error(f"Error generating persona report: {e}")
            await ctx.send(persona_manager.get_error_response("report_generation_error", error=str(e)))
    else:
        logger.warning(f"Non-admin user {ctx.author.id} attempted persona_report command")
        await ctx.send(persona_manager.get_permission_response("admin_command"))

@bot.command(name='ai_analytics')
async def ai_analytics(ctx, days: int = 7):
    """View AI usage analytics (admin only)"""
    logger.info(f"AI analytics command called by user {ctx.author.id}, days: {days}")
    
    if ctx.author.guild_permissions.administrator:
        logger.info(f"Admin permission verified for user {ctx.author.id}")
        
        try:
            analytics = await ai_db.get_analytics(days)
            logger.info(f"Analytics retrieved for {days} days")
            
            embed = discord.Embed(
                title="🤖 AI Usage Analytics",
                description=f"Statistics for the last {days} days",
                color=0x00ff00
            )
            
            embed.add_field(
                name="📊 Usage Stats",
                value=f"**Conversations:** {analytics['total_conversations']}\n"
                      f"**Unique Users:** {analytics['unique_users']}\n"
                      f"**Total Tokens:** {analytics['total_tokens']:,}\n"
                      f"**Avg Response Time:** {analytics['avg_response_time']}s",
                inline=False
            )
            
            if analytics['model_usage']:
                model_stats = []
                for model, count in analytics['model_usage'].items():
                    model_stats.append(f"**{model}:** {count}")
                
                embed.add_field(
                    name="🔧 Model Usage",
                    value="\n".join(model_stats),
                    inline=False
                )
            
            await ctx.send(embed=embed)
            logger.info(f"AI analytics embed sent to user {ctx.author.id}")
            
        except Exception as e:
            logger.error(f"Error retrieving AI analytics: {e}")
            await ctx.send(f"❌ Error retrieving analytics: {e}")
    else:
        logger.warning(f"Non-admin user {ctx.author.id} attempted ai_analytics command")
        try:
            fallback = persona_manager.get_activity_response("admin", "no_permission")
        except Exception:
            fallback = "You don't have permission to use that command."
        await ctx.send(fallback)

@bot.event
async def on_command_error(ctx, error):
    """Global error handler for commands"""
    logger.error(f"Command error from user {ctx.author.id} in {ctx.command}: {str(error)}")
    
    if isinstance(error, commands.MissingRequiredArgument):
        # Handle missing arguments with persona response
        logger.warning(f"Missing required argument: {error.param.name}")
        await ctx.send(persona_manager.get_response("missing_args") + f" You're missing: {error.param.name}")
    elif isinstance(error, commands.CommandNotFound):
        # Ignore command not found errors (don't spam chat)
        logger.debug("Command not found error ignored")
        pass
    elif isinstance(error, discord.Forbidden):
        # Bot doesn't have permissions - try to DM user if possible
        logger.warning(f"Forbidden action, attempting DM to user {ctx.author.id}")
        try:
            # Get permission error message with fallback
            try:
                permissions_config = persona_manager.persona.get("activity_responses", {}).get("permissions", {})
                message = permissions_config.get("no_send_permission", "I don't have permission to send messages!")
            except Exception:
                message = persona_manager.get_permission_response("send_messages")
            await ctx.author.send(message)
        except (discord.Forbidden, discord.HTTPException):
            logger.warning(f"Could not DM user {ctx.author.id} about permission error")
            pass  # Can't DM either, give up silently
    else:
        # For other errors, send a generic tsundere error message
        logger.error(f"Unhandled command error: {type(error).__name__}: {str(error)}")
        try:
            await ctx.send(persona_manager.get_error_response("command_error", error=str(error)))
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
        if 'ai_db' in globals():
            asyncio.run(ai_db.close())
        if 'search' in globals() and search:
            asyncio.run(search.close_session())
        # Get bot name for shutdown message
        try:
            bot_name = persona_manager.get_name() if 'persona_manager' in globals() else "Discord AI"
        except:
            bot_name = "Discord AI"
        print(f'👋 {bot_name} is shutting down... Goodbye!')
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
        if 'ai_db' in globals():
            asyncio.run(ai_db.close())
        if 'search' in globals() and search:
            asyncio.run(search.close_session())
        # Get bot name for shutdown message
        try:
            bot_name = persona_manager.get_name() if 'persona_manager' in globals() else "Discord AI"
        except:
            bot_name = "Discord AI"
        print(f'👋 {bot_name} is shutting down... Goodbye!')
    except Exception as e:
        print(f'❌ Bot crashed: {e}')
        # Save any pending data and cleanup
        if 'social' in globals():
            social.save_user_data()
        if 'ai_db' in globals():
            asyncio.run(ai_db.close())
        if 'search' in globals() and search:
            asyncio.run(search.close_session())
        raise