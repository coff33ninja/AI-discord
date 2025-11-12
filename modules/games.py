"""
Games module - fun interactive games with persona-driven responses
"""
import random
import asyncio
from .persona_manager import PersonaManager

class TsundereGames:
    def __init__(self, persona_file="persona_card.json"):
        self.active_games = {}
        self.persona_manager = PersonaManager(persona_file)
    
    async def start_number_guessing(self, user_id, max_number=100):
        """Start a number guessing game"""
        secret_number = random.randint(1, max_number)
        self.active_games[user_id] = {
            'type': 'number_guess',
            'secret': secret_number,
            'attempts': 0,
            'max': max_number
        }
        
        return self.persona_manager.get_activity_response("games", "start") + f" I picked a number between 1 and {max_number}. Try to guess it!"
    
    async def guess_number(self, user_id, guess):
        """Process a number guess"""
        if user_id not in self.active_games or self.active_games[user_id]['type'] != 'number_guess':
            return self.persona_manager.get_activity_response("games", "no_active_game")
        
        game = self.active_games[user_id]
        game['attempts'] += 1
        secret = game['secret']
        
        if guess == secret:
            attempts = game['attempts']
            del self.active_games[user_id]
            return self.persona_manager.get_activity_response("games", "win") + f" It was {secret} in {attempts} tries!"
        elif guess < secret:
            return self.persona_manager.get_activity_response("games", "hint_low", insult=self.persona_manager.get_speech_pattern('insults'))
        else:
            return self.persona_manager.get_activity_response("games", "hint_high", insult=self.persona_manager.get_speech_pattern('insults'))
    
    async def rock_paper_scissors(self, user_choice):
        """Play rock paper scissors"""
        choices = ['rock', 'paper', 'scissors']
        bot_choice = random.choice(choices)
        user_choice = user_choice.lower()
        
        if user_choice not in choices:
            return self.persona_manager.get_response("missing_args") + " Pick rock, paper, or scissors!"
        
        if user_choice == bot_choice:
            return self.persona_manager.get_activity_response("games", "tie", choice=bot_choice)
        elif (user_choice == 'rock' and bot_choice == 'scissors') or \
             (user_choice == 'paper' and bot_choice == 'rock') or \
             (user_choice == 'scissors' and bot_choice == 'paper'):
            return self.persona_manager.get_activity_response("games", "win") + f" You picked {user_choice}, I picked {bot_choice}..."
        else:
            return self.persona_manager.get_activity_response("games", "lose") + f" I picked {bot_choice}, you picked {user_choice}!"
    
    async def magic_8ball(self, question):
        """Magic 8-ball with persona responses"""
        # Add dramatic pause using asyncio
        await asyncio.sleep(2)  # Tsundere thinking time
        
        action = self.persona_manager.get_activity_response("magic_8ball", "action")
        answers = self.persona_manager.persona.get("activity_responses", {}).get("magic_8ball", {}).get("answers", ["Maybe?"])
        answer = random.choice(answers)
        
        return f"{action}\n\n{answer}"
    
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
        await asyncio.sleep(1)
        
        return self.persona_manager.get_activity_response("games", "trivia_start", question=question_data['q'])
    
    async def answer_trivia(self, user_id, answer):
        """Process trivia answer with timing"""
        if user_id not in self.active_games or self.active_games[user_id]['type'] != 'trivia':
            return self.persona_manager.get_activity_response("games", "no_active_game").replace("game", "trivia game with !trivia")
        
        game = self.active_games[user_id]
        elapsed_time = asyncio.get_event_loop().time() - game['start_time']
        correct_answer = game['answer']
        
        del self.active_games[user_id]
        
        if elapsed_time > 30:
            return self.persona_manager.get_activity_response("games", "trivia_timeout", answer=correct_answer)
        
        if answer.lower().strip() == correct_answer:
            if elapsed_time < 5:
                return self.persona_manager.get_activity_response("games", "trivia_fast_correct", time=elapsed_time)
            else:
                return self.persona_manager.get_activity_response("games", "trivia_correct", time=elapsed_time)
        else:
            return self.persona_manager.get_activity_response("games", "trivia_wrong", answer=correct_answer)