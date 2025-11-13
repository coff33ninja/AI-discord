"""Utility functions module - helpful tools with persona-driven responses"""
import random
import datetime
import requests
from .persona_manager import PersonaManager

# Constants for external APIs
OPENWEATHERMAP_API_URL = "http://api.openweathermap.org/data/2.5/weather"
RANDOM_FACTS_API_URL = "https://uselessfacts.jsph.pl/random.json"
JOKES_API_URL = "https://official-joke-api.appspot.com/random_joke"
CAT_FACTS_API_URL = "https://catfact.ninja/fact"

DEFAULT_TIMEOUT = 5
DEFAULT_API_KEY = "demo_key"  # Replace with real API key from .env
DEFAULT_DICE_SIDES = 6

class TsundereUtilities:
    def __init__(self, gemini_model, persona_file="persona_card.json"):
        self.model = gemini_model
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
    
    async def get_weather(self, location):
        """Get weather info using OpenWeatherMap API"""
        try:
            # Using OpenWeatherMap free API (you'd need to add API key to .env)
            api_key = "demo_key"  # Replace with real API key
            url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                temp = data['main']['temp']
                description = data['weather'][0]['description']
                feels_like = data['main']['feels_like']
                
                weather_info = f"{temp}°C with {description}. Feels like {feels_like}°C"
                return self.persona_manager.get_activity_response("weather", "success", 
                                                                location=location, 
                                                                weather_info=weather_info)
            else:
                return self.persona_manager.get_activity_response("weather", "error", location=location)
                
        except requests.exceptions.Timeout:
            return self.persona_manager.get_activity_response("weather", "error", location=location)
        except requests.exceptions.RequestException:
            return self.persona_manager.get_activity_response("weather", "error", location=location)
        except Exception:
            return self.persona_manager.get_activity_response("weather", "error", location=location)
    
    async def roll_dice(self, sides=6):
        """Roll dice with persona-driven attitude"""
        result = random.randint(1, sides)
        frustration = self.persona_manager.get_speech_pattern("frustrated")
        insult = self.persona_manager.get_speech_pattern("insults")
        return f"{frustration} " + self.persona_manager.get_activity_response("utilities", "dice", result=result, insult=insult)
    
    async def get_time(self):
        """Get current time with persona flair"""
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M %p")
        insult = self.persona_manager.get_speech_pattern("insults")
        return self.persona_manager.get_activity_response("utilities", "time", time=time_str, insult=insult)
    
    async def flip_coin(self):
        """Flip a coin with persona attitude"""
        result = random.choice(["Heads", "Tails"])
        reluctant = self.persona_manager.get_speech_pattern("reluctant_help")
        insult = self.persona_manager.get_speech_pattern("insults")
        return f"{reluctant} " + self.persona_manager.get_activity_response("utilities", "coin", result=result, insult=insult)
    
    async def calculate(self, expression):
        """Safe calculator with persona-driven responses"""
        try:
            # Simple safe evaluation for basic math
            allowed_chars = set('0123456789+-*/.() ')
            if not all(c in allowed_chars for c in expression):
                return self.persona_manager.get_activity_response("calculation", "error")
            
            result = eval(expression)
            return self.persona_manager.get_activity_response("calculation", "success", 
                                                            expression=expression, 
                                                            result=result)
        except:
            return self.persona_manager.get_activity_response("calculation", "error")   
    async def get_random_fact(self):
        """Get a random fact using an API"""
        try:
            url = "https://uselessfacts.jsph.pl/random.json?language=en"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                fact = data['text']
                
                success_responses = self.persona_manager.persona.get("activity_responses", {}).get("facts", {}).get("success", ["Here's a fact: {fact}"])
                return random.choice(success_responses).format(fact=fact)
            else:
                error_responses = self.persona_manager.persona.get("activity_responses", {}).get("facts", {}).get("error", ["Can't get facts right now!"])
                return random.choice(error_responses)
                
        except (requests.exceptions.Timeout, requests.exceptions.RequestException, Exception):
            error_responses = self.persona_manager.persona.get("activity_responses", {}).get("facts", {}).get("error", ["Can't get facts right now!"])
            return random.choice(error_responses)
    
    async def get_joke(self):
        """Get a random joke using an API"""
        try:
            url = "https://official-joke-api.appspot.com/random_joke"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                setup = data['setup']
                punchline = data['punchline']
                
                success_responses = self.persona_manager.persona.get("activity_responses", {}).get("jokes", {}).get("success", ["Here's a joke: {setup}\n{punchline}"])
                return random.choice(success_responses).format(setup=setup, punchline=punchline)
            else:
                error_responses = self.persona_manager.persona.get("activity_responses", {}).get("jokes", {}).get("error", ["Can't get jokes right now!"])
                return random.choice(error_responses)
                
        except (requests.exceptions.Timeout, requests.exceptions.RequestException, Exception):
            error_responses = self.persona_manager.persona.get("activity_responses", {}).get("jokes", {}).get("error", ["Can't get jokes right now!"])
            return random.choice(error_responses)
    
    async def get_cat_fact(self):
        """Get a random cat fact"""
        try:
            url = "https://catfact.ninja/fact"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                fact = data['fact']
                
                success_responses = self.persona_manager.persona.get("activity_responses", {}).get("cat_facts", {}).get("success", ["Here's a cat fact: {fact}"])
                return random.choice(success_responses).format(fact=fact)
            else:
                error_responses = self.persona_manager.persona.get("activity_responses", {}).get("cat_facts", {}).get("error", ["Can't get cat facts right now!"])
                return random.choice(error_responses)
                
        except (requests.exceptions.Timeout, requests.exceptions.RequestException, Exception):
            error_responses = self.persona_manager.persona.get("activity_responses", {}).get("cat_facts", {}).get("error", ["Can't get cat facts right now!"])
            return random.choice(error_responses)