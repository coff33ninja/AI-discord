import discord
from discord.ext import commands
import google.generativeai as genai
import os
import asyncio
import concurrent.futures
from dotenv import load_dotenv

# Import our tsundere modules
from modules.personality import TsunderePersonality
from modules.utilities import TsundereUtilities
from modules.games import TsundereGames
from modules.social import TsundereSocial
from modules.server_actions import TsundereServerActions
from modules.persona_manager import PersonaManager

# Load environment variables
load_dotenv()

# Configure Gemini AI
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-flash')

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

@bot.event
async def on_ready():
    global utilities
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')
    
    # Initialize utilities with the model
    utilities = TsundereUtilities(model)
    
    # Set tsundere status
    status = persona_manager.persona.get("activity_responses", {}).get("bot_status", "It's not like I want to help! | !help_ai")
    await bot.change_presence(activity=discord.Game(name=status))

@bot.command(name='ai', aliases=['ask', 'chat'])
async def ask_gemini(ctx, *, question):
    """Ask Gemini AI a question"""
    try:
        # Update social interaction
        social.update_interaction(ctx.author.id)
        
        # Show typing indicator
        async with ctx.typing():
            # Create tsundere persona prompt
            tsundere_prompt = personality.create_ai_prompt(question)
            
            # Generate response using Gemini with timeout protection
            # Run the blocking API call in a thread pool with timeout
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                try:
                    response = await asyncio.wait_for(
                        loop.run_in_executor(executor, model.generate_content, tsundere_prompt),
                        timeout=30.0  # 30 second timeout
                    )
                except asyncio.TimeoutError:
                    await ctx.send("Ugh! The AI is taking too long to respond, baka! Try again later!")
                    return
            
            # Discord has a 2000 character limit for messages
            if len(response.text) > 2000:
                # Split long responses
                chunks = [response.text[i:i+2000] for i in range(0, len(response.text), 2000)]
                for chunk in chunks:
                    await ctx.send(chunk)
            else:
                await ctx.send(response.text)
                
    except Exception as e:
        await ctx.send(personality.get_error_response(e))

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
        value="`!reload_persona` - Reload personality config\n`!shutdown` (or `!kill`, `!stop`) - Shutdown bot\n`!restart` (or `!reboot`) - Restart bot",
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
            await message.channel.send(personality.get_mention_response())
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
    social.update_interaction(ctx.author.id)
    response = await social.give_compliment(ctx.author.id)
    await ctx.send(response)

# Social Commands
@bot.command(name='mood')
async def check_mood(ctx):
    """Check the AI's current mood"""
    response = await social.get_mood()
    await ctx.send(response)

@bot.command(name='relationship')
async def check_relationship(ctx):
    """Check your relationship status with the AI"""
    response = await social.get_relationship_status(ctx.author.id)
    await ctx.send(response)

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
        admin_config = persona_manager.persona.get("activity_responses", {}).get("admin", {})
        response = admin_config.get("reload_success", "Reloaded: {result}").format(result=result)
        await ctx.send(response)
    else:
        admin_config = persona_manager.persona.get("activity_responses", {}).get("admin", {})
        response = admin_config.get("no_permission", "No permission!")
        await ctx.send(response)

@bot.command(name='shutdown', aliases=['kill', 'stop'])
async def shutdown_bot(ctx):
    """Shutdown the bot (admin only)"""
    if ctx.author.guild_permissions.administrator:
        admin_config = persona_manager.persona.get("activity_responses", {}).get("admin", {})
        response = admin_config.get("shutdown", "Ugh, fine! I'm shutting down... It's not like I'll miss you or anything, baka!")
        await ctx.send(response)
        print(f"Bot shutdown requested by {ctx.author}")
        await bot.close()
    else:
        admin_config = persona_manager.persona.get("activity_responses", {}).get("admin", {})
        response = admin_config.get("no_permission", "No permission!")
        await ctx.send(response)

@bot.command(name='restart', aliases=['reboot'])
async def restart_bot(ctx):
    """Restart the bot (admin only)"""
    if ctx.author.guild_permissions.administrator:
        admin_config = persona_manager.persona.get("activity_responses", {}).get("admin", {})
        response = admin_config.get("restart", "Hmph! Fine, I'll restart... Don't expect me to be happy about it!")
        await ctx.send(response)
        print(f"Bot restart requested by {ctx.author}")
        
        # Save any pending data
        social.save_user_data()
        
        # Close and restart
        await bot.close()
        
        # Note: This requires the bot to be run in a loop or with auto-restart
        import os
        import sys
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        admin_config = persona_manager.persona.get("activity_responses", {}).get("admin", {})
        response = admin_config.get("no_permission", "No permission!")
        await ctx.send(response)

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
    bot.run(os.getenv('DISCORD_TOKEN'))