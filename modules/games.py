"""
Games module - fun interactive games with persona-driven responses
"""
import random
import asyncio
from .persona_manager import PersonaManager
from .logger import BotLogger

# Initialize logger
logger = BotLogger.get_logger(__name__)

# Game constants
TRIVIA_TIMEOUT = 30
TRIVIA_FAST_THRESHOLD = 5
DEFAULT_GUESSING_MAX = 100
MAGIC_8BALL_DELAY = 2
TRIVIA_START_DELAY = 1
NUMBER_GUESSING_TIMEOUT = 60  # Time limit for number guessing
COUNTDOWN_INTERVAL = 5  # Announce every 5 seconds

class TsundereGames:
    def __init__(self, persona_file="persona_card.json"):
        self.active_games = {}  # {user_id: {game_data}}
        self.active_questions = {}  # {question_id: {question_data, answered_users: set()}}
        self.active_timers = {}  # {timer_id: task} to track active countdown timers
        self.persona_manager = PersonaManager(persona_file)
        self.question_counter = 0
        self.timer_counter = 0
    
    def _get_persona_response(self, category, subcategory, **format_kwargs):
        """Helper method to safely get persona responses from nested dictionaries"""
        try:
            responses = self.persona_manager.persona.get("activity_responses", {}).get(category, {}).get(subcategory, [])
            if responses:
                # Handle both list and single string responses
                if isinstance(responses, list):
                    selected = random.choice(responses)
                else:
                    selected = responses
                return selected.format(**format_kwargs) if format_kwargs else selected
        except (KeyError, TypeError, ValueError) as e:
            print(f"⚠️ Error retrieving persona response: {e}")
        return None
    
    async def start_number_guessing(self, user_id, max_number=DEFAULT_GUESSING_MAX, ctx=None):
        """Start a number guessing game with countdown"""
        secret_number = random.randint(1, max_number)
        
        self.timer_counter += 1
        timer_id = self.timer_counter
        
        self.active_games[user_id] = {
            'type': 'number_guess',
            'secret': secret_number,
            'attempts': 0,
            'max': max_number,
            'start_time': asyncio.get_event_loop().time(),
            'timer_id': timer_id,
            'ctx': ctx
        }
        
        logger.info(f"Number guessing game started for user {user_id} (1-{max_number})")
        persona_msg = self._get_persona_response("games", "start")
        start_text = persona_msg or self.persona_manager.get_game_response("number_guess", "start")
        
        # Start countdown if context provided
        if ctx:
            countdown_task = asyncio.create_task(self._countdown_timer(timer_id, ctx, NUMBER_GUESSING_TIMEOUT, "number guessing"))
            self.active_timers[timer_id] = countdown_task
        
        return f"{start_text} I picked a number between 1 and {max_number}. Try to guess it! You have {NUMBER_GUESSING_TIMEOUT} seconds."
    
    async def guess_number(self, user_id, guess):
        """Process a number guess"""
        if user_id not in self.active_games or self.active_games[user_id]['type'] != 'number_guess':
            logger.info(f"No active number guessing game for user {user_id}")
            return self._get_persona_response("games", "no_active_game") or self.persona_manager.get_game_response("general", "no_active_game")
        
        game = self.active_games[user_id]
        game['attempts'] += 1
        secret = game['secret']
        
        logger.info(f"User {user_id} guessed {guess}, secret is {secret}, attempts: {game['attempts']}")
        
        if guess == secret:
            attempts = game['attempts']
            del self.active_games[user_id]
            logger.info(f"User {user_id} won number guessing game in {attempts} attempts")
            persona_msg = self._get_persona_response("games", "win")
            return f"{persona_msg or self.persona_manager.get_game_response('number_guess', 'win')} It was {secret} in {attempts} tries!"
        elif guess < secret:
            persona_msg = self._get_persona_response("games", "hint_low")
            return persona_msg or self.persona_manager.get_game_response("number_guess", "hint_low")
        else:
            persona_msg = self._get_persona_response("games", "hint_high")
            return persona_msg or self.persona_manager.get_game_response("number_guess", "hint_high")
    
    async def rock_paper_scissors(self, user_choice):
        """Play rock paper scissors"""
        choices = ['rock', 'paper', 'scissors']
        bot_choice = random.choice(choices)
        user_choice = user_choice.lower()
        
        logger.info(f"Rock-paper-scissors: user chose {user_choice}, bot chose {bot_choice}")
        
        if user_choice not in choices:
            logger.warning(f"Invalid choice in rock-paper-scissors: {user_choice}")
            return self.persona_manager.get_validation_response("rps_choice")
        
        if user_choice == bot_choice:
            persona_msg = self._get_persona_response("games", "tie", choice=bot_choice)
            return persona_msg or self.persona_manager.get_game_response("rps", "tie", choice=bot_choice)
        elif (user_choice == 'rock' and bot_choice == 'scissors') or \
             (user_choice == 'paper' and bot_choice == 'rock') or \
             (user_choice == 'scissors' and bot_choice == 'paper'):
            logger.info("Rock-paper-scissors: user won")
            persona_msg = self._get_persona_response("games", "win")
            return f"{persona_msg or self.persona_manager.get_game_response('rps', 'win')} You picked {user_choice}, I picked {bot_choice}."
        else:
            logger.info("Rock-paper-scissors: bot won")
            persona_msg = self._get_persona_response("games", "lose")
            return f"{persona_msg or self.persona_manager.get_game_response('rps', 'lose')} I picked {bot_choice}, you picked {user_choice}."
    
    async def magic_8ball(self, question, ctx=None):
        """Magic 8-ball with persona responses and countdown"""
        # Add dramatic pause using asyncio
        await asyncio.sleep(MAGIC_8BALL_DELAY)  # Tsundere thinking time
        
        persona_msg = self._get_persona_response("magic_8ball", "action")
        answers = self.persona_manager.persona.get("activity_responses", {}).get("magic_8ball", {}).get("answers", ["Maybe?"])
        answer = random.choice(answers)
        
        action_text = persona_msg or "Shakes the 8-ball..."
        response = f"{action_text}\n\n{answer}"
        
        # Start countdown if context provided
        if ctx:
            self.timer_counter += 1
            timer_id = self.timer_counter
            countdown_task = asyncio.create_task(self._countdown_timer(timer_id, ctx, MAGIC_8BALL_DELAY, "magic 8-ball"))
            self.active_timers[timer_id] = countdown_task
        
        return response
    
    async def trivia_game(self, user_id, ctx=None):
        """Start a trivia game with dramatic timing and countdown"""
        questions = [
            {"q": "What's the capital of Japan?", "a": "tokyo"},
            {"q": "What's 7 x 8?", "a": "56"},
            {"q": "What color do you get mixing red and blue?", "a": "purple"},
            {"q": "How many days are in a leap year?", "a": "366"},
            {"q": "What's the largest planet in our solar system?", "a": "jupiter"}
        ]
        
        question_data = random.choice(questions)
        self.question_counter += 1
        question_id = self.question_counter
        
        self.timer_counter += 1
        timer_id = self.timer_counter
        
        # Store the shared question data
        self.active_questions[question_id] = {
            'question': question_data['q'],
            'answer': question_data['a'],
            'start_time': asyncio.get_event_loop().time(),
            'answered_users': set(),
            'timer_id': timer_id,
            'ctx': ctx  # Store context for countdown announcements
        }
        
        # Store user-specific game reference
        self.active_games[user_id] = {
            'type': 'trivia',
            'question_id': question_id
        }
        
        logger.info(f"Trivia game started for user {user_id} (Question ID: {question_id})")
        
        # Dramatic pause before asking
        await asyncio.sleep(TRIVIA_START_DELAY)
        
        persona_msg = self._get_persona_response("games", "trivia_start", question=question_data['q'])
        initial_message = persona_msg or f"Question: {question_data['q']}"
        
        # Start countdown announcements in background
        if ctx:
            countdown_task = asyncio.create_task(self._countdown_timer(timer_id, ctx, TRIVIA_TIMEOUT, "trivia"))
            self.active_timers[timer_id] = countdown_task
        
        return initial_message
    
    async def _countdown_timer(self, timer_id, ctx, timeout_duration, game_name):
        """Generic countdown timer that announces every COUNTDOWN_INTERVAL seconds"""
        start_time = asyncio.get_event_loop().time()
        announced_times = set()
        
        try:
            while True:
                elapsed = asyncio.get_event_loop().time() - start_time
                remaining = timeout_duration - elapsed
                
                if remaining <= 0:
                    # Timer finished
                    if timer_id in self.active_timers:
                        del self.active_timers[timer_id]
                    break
                
                # Announce at COUNTDOWN_INTERVAL boundaries (e.g., 25, 20, 15, 10, 5 seconds)
                for announce_time in range(int(timeout_duration), 0, -COUNTDOWN_INTERVAL):
                    if remaining <= announce_time and announce_time not in announced_times:
                        announced_times.add(announce_time)
                        await ctx.send(f"⏱️ **{announce_time} seconds left for {game_name}!**")
                        break
                
                # Check every 0.5 seconds
                await asyncio.sleep(0.5)
        except Exception as e:
            logger.error(f"Error in countdown timer for {game_name}: {e}")
        finally:
            if timer_id in self.active_timers:
                del self.active_timers[timer_id]
    
    async def answer_trivia(self, user_id, answer):
        """Process trivia answer with timing"""
        if user_id not in self.active_games or self.active_games[user_id]['type'] != 'trivia':
            logger.info(f"No active trivia game for user {user_id}")
            persona_msg = self._get_persona_response("games", "no_active_game")
            return f"{persona_msg or self.persona_manager.get_game_response('trivia', 'no_active_game')} Start one with !trivia"
        
        question_id = self.active_games[user_id]['question_id']
        
        if question_id not in self.active_questions:
            logger.info(f"Question {question_id} not found for user {user_id}")
            del self.active_games[user_id]
            return "The trivia question expired. Start a new one with !trivia"
        
        # Check if user already answered this question
        if user_id in self.active_questions[question_id]['answered_users']:
            logger.info(f"User {user_id} attempted to answer question {question_id} twice")
            return "You already answered this question, baka! Wait for the next one!"
        
        question_data = self.active_questions[question_id]
        elapsed_time = asyncio.get_event_loop().time() - question_data['start_time']
        correct_answer = question_data['answer']
        
        # Check timeout BEFORE processing answer
        if elapsed_time > TRIVIA_TIMEOUT:
            logger.info(f"Trivia answer timed out for user {user_id}")
            del self.active_games[user_id]
            persona_msg = self._get_persona_response("games", "trivia_timeout", answer=correct_answer)
            return persona_msg or self.persona_manager.get_game_response("trivia", "timeout", answer=correct_answer)
        
        # Mark user as answered
        question_data['answered_users'].add(user_id)
        del self.active_games[user_id]
        
        logger.info(f"Trivia answer for user {user_id}: answered '{answer}', correct is '{correct_answer}', time: {elapsed_time:.1f}s")
        
        if answer.lower().strip() == correct_answer:
            if elapsed_time < TRIVIA_FAST_THRESHOLD:
                logger.info(f"User {user_id} answered trivia fast: {elapsed_time:.1f}s")
                persona_msg = self._get_persona_response("games", "trivia_fast_correct", time=int(elapsed_time))
                return persona_msg or f"Wow, {elapsed_time:.1f}s! Impressive!"
            else:
                logger.info(f"User {user_id} answered trivia correctly: {elapsed_time:.1f}s")
                persona_msg = self._get_persona_response("games", "trivia_correct", time=int(elapsed_time))
                return persona_msg or f"Correct! You took {elapsed_time:.1f}s."
        else:
            logger.info(f"User {user_id} answered trivia wrong")
            persona_msg = self._get_persona_response("games", "trivia_wrong", answer=correct_answer)
            return persona_msg or f"Wrong! The answer was {correct_answer}."