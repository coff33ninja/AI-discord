"""
Games module - fun interactive games with persona-driven responses
"""
import random
import asyncio
from .persona_manager import PersonaManager

# Game constants
TRIVIA_TIMEOUT = 30
TRIVIA_FAST_THRESHOLD = 5
DEFAULT_GUESSING_MAX = 100
MAGIC_8BALL_DELAY = 2
TRIVIA_START_DELAY = 1

class TsundereGames:
    def __init__(self, persona_file="persona_card.json"):
        self.active_games = {}
        self.persona_manager = PersonaManager(persona_file)
    
    def _get_persona_response(self, category, subcategory, **format_kwargs):
        """Helper method to safely get persona responses from nested dictionaries"""
        try:
            responses = self.persona_manager.persona.get("activity_responses", {}).get(category, {}).get(subcategory, [])
            if responses:
                selected = random.choice(responses)
                return selected.format(**format_kwargs) if format_kwargs else selected
        except (KeyError, TypeError, ValueError) as e:
            print(f"⚠️ Error retrieving persona response: {e}")
        return None
    
    async def start_number_guessing(self, user_id, max_number=DEFAULT_GUESSING_MAX):
        """Start a number guessing game"""
        secret_number = random.randint(1, max_number)
        self.active_games[user_id] = {
            'type': 'number_guess',
            'secret': secret_number,
            'attempts': 0,
            'max': max_number
        }
        
        persona_msg = self._get_persona_response("games", "start")
        start_text = persona_msg or "Let's play!"
        return f"{start_text} I picked a number between 1 and {max_number}. Try to guess it!"
    
    async def guess_number(self, user_id, guess):
        """Process a number guess"""
        if user_id not in self.active_games or self.active_games[user_id]['type'] != 'number_guess':
            return self._get_persona_response("games", "no_active_game") or "No active game."
        
        game = self.active_games[user_id]
        game['attempts'] += 1
        secret = game['secret']
        
        if guess == secret:
            attempts = game['attempts']
            del self.active_games[user_id]
            persona_msg = self._get_persona_response("games", "win")
            return f"{persona_msg or 'Congrats!'} It was {secret} in {attempts} tries!"
        elif guess < secret:
            persona_msg = self._get_persona_response("games", "hint_low")
            return persona_msg or "Too low! Try again."
        else:
            persona_msg = self._get_persona_response("games", "hint_high")
            return persona_msg or "Too high! Try again."
    
    async def rock_paper_scissors(self, user_choice):
        """Play rock paper scissors"""
        choices = ['rock', 'paper', 'scissors']
        bot_choice = random.choice(choices)
        user_choice = user_choice.lower()
        
        if user_choice not in choices:
            return "Pick rock, paper, or scissors!"
        
        if user_choice == bot_choice:
            persona_msg = self._get_persona_response("games", "tie", choice=bot_choice)
            return persona_msg or f"We both picked {bot_choice}!"
        elif (user_choice == 'rock' and bot_choice == 'scissors') or \
             (user_choice == 'paper' and bot_choice == 'rock') or \
             (user_choice == 'scissors' and bot_choice == 'paper'):
            persona_msg = self._get_persona_response("games", "win")
            return f"{persona_msg or 'You won!'} You picked {user_choice}, I picked {bot_choice}."
        else:
            persona_msg = self._get_persona_response("games", "lose")
            return f"{persona_msg or 'I won!'} I picked {bot_choice}, you picked {user_choice}."
    
    async def magic_8ball(self, question):
        """Magic 8-ball with persona responses"""
        # Add dramatic pause using asyncio
        await asyncio.sleep(MAGIC_8BALL_DELAY)  # Tsundere thinking time
        
        persona_msg = self._get_persona_response("magic_8ball", "action")
        answers = self.persona_manager.persona.get("activity_responses", {}).get("magic_8ball", {}).get("answers", ["Maybe?"])
        answer = random.choice(answers)
        
        action_text = persona_msg or "Shakes the 8-ball..."
        return f"{action_text}\n\n{answer}"
    
    async def trivia_game(self, user_id):
        """Start a trivia game with dramatic timing"""
        questions = [
            {"q": "What's the capital of Japan?", "a": "tokyo"},
            {"q": "What's 7 x 8?", "a": "56"},
            {"q": "What color do you get mixing red and blue?", "a": "purple"},
            {"q": "How many days are in a leap year?", "a": "366"},
            {"q": "What's the largest planet in our solar system?", "a": "jupiter"}
        ]
        
        question_data = random.choice(questions)
        self.active_games[user_id] = {
            'type': 'trivia',
            'answer': question_data['a'],
            'start_time': asyncio.get_event_loop().time()
        }
        
        # Dramatic pause before asking
        await asyncio.sleep(TRIVIA_START_DELAY)
        
        persona_msg = self._get_persona_response("games", "trivia_start", question=question_data['q'])
        return persona_msg or f"Question: {question_data['q']}"
    
    async def answer_trivia(self, user_id, answer):
        """Process trivia answer with timing"""
        if user_id not in self.active_games or self.active_games[user_id]['type'] != 'trivia':
            persona_msg = self._get_persona_response("games", "no_active_game")
            return f"{persona_msg or 'No active game.'} Start one with !trivia"
        
        game = self.active_games[user_id]
        elapsed_time = asyncio.get_event_loop().time() - game['start_time']
        correct_answer = game['answer']
        
        del self.active_games[user_id]
        
        if elapsed_time > TRIVIA_TIMEOUT:
            persona_msg = self._get_persona_response("games", "trivia_timeout", answer=correct_answer)
            return persona_msg or f"Time's up! The answer was {correct_answer}."
        
        if answer.lower().strip() == correct_answer:
            if elapsed_time < TRIVIA_FAST_THRESHOLD:
                persona_msg = self._get_persona_response("games", "trivia_fast_correct", time=int(elapsed_time))
                return persona_msg or f"Wow, {elapsed_time:.1f}s! Impressive!"
            else:
                persona_msg = self._get_persona_response("games", "trivia_correct", time=int(elapsed_time))
                return persona_msg or f"Correct! You took {elapsed_time:.1f}s."
        else:
            persona_msg = self._get_persona_response("games", "trivia_wrong", answer=correct_answer)
            return persona_msg or f"Wrong! The answer was {correct_answer}."