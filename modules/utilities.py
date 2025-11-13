"""Utility functions module - helpful tools with persona-driven responses"""
import random
import datetime
import requests
from .persona_manager import PersonaManager
from .logger import BotLogger

# Initialize logger
logger = BotLogger.get_logger(__name__)

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
            if not isinstance(location, str) or not location.strip():
                logger.warning(f"Invalid weather location: {location}")
                return "Please provide a valid location."
            
            logger.info(f"Fetching weather for location: {location}")
            params = {
                "q": location,
                "appid": DEFAULT_API_KEY,
                "units": "metric"
            }
            response = requests.get(OPENWEATHERMAP_API_URL, params=params, timeout=DEFAULT_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                temp = data['main']['temp']
                description = data['weather'][0]['description']
                feels_like = data['main']['feels_like']
                
                weather_info = f"{temp}°C with {description}. Feels like {feels_like}°C"
                logger.info(f"Weather retrieved for {location}: {weather_info}")
                persona_msg = self._get_persona_response("utilities", "weather", location=location, weather_info=weather_info)
                return persona_msg or f"Weather in {location}: {weather_info}"
            else:
                logger.warning(f"Weather API error for {location}: {response.status_code}")
                return f"Could not find weather for {location}."
                
        except requests.exceptions.Timeout:
            logger.error(f"Weather API timeout for location: {location}")
            return "Weather API request timed out."
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather API error: {e}")
            print(f"⚠️ Weather API error: {e}")
            return "I couldn't get the weather info right now..."
    
    async def roll_dice(self, sides=DEFAULT_DICE_SIDES):
        """Roll dice with persona-driven attitude"""
        try:
            # Validate sides parameter (2-1000 range)
            if not isinstance(sides, int) or sides < 2 or sides > 1000:
                logger.warning(f"Invalid dice sides: {sides}")
                return f"Please specify a valid number of sides (2-1000)."
            
            result = random.randint(1, sides)
            logger.info(f"Dice rolled: {result} out of {sides}")
            persona_msg = self._get_persona_response("utilities", "dice", result=result, sides=sides)
            return persona_msg or f"You rolled a {result}!"
        except (TypeError, ValueError) as e:
            logger.error(f"Dice roll error: {e}")
            return "Invalid dice parameters."
    
    async def get_time(self):
        """Get current time with persona flair"""
        try:
            now = datetime.datetime.now()
            time_str = now.strftime("%I:%M %p")
            logger.debug(f"Current time retrieved: {time_str}")
            persona_msg = self._get_persona_response("utilities", "time", time=time_str)
            return persona_msg or f"The current time is {time_str}."
        except Exception as e:
            logger.error(f"Error getting time: {e}")
            print(f"⚠️ Error getting time: {e}")
            return "I couldn't get the time right now..."
    
    async def flip_coin(self):
        """Flip a coin with persona attitude"""
        try:
            result = random.choice(["Heads", "Tails"])
            logger.info(f"Coin flipped: {result}")
            persona_msg = self._get_persona_response("utilities", "coin", result=result)
            return persona_msg or f"The coin landed on {result}!"
        except Exception as e:
            logger.error(f"Error flipping coin: {e}")
            print(f"⚠️ Error flipping coin: {e}")
            return "I couldn't flip the coin right now..."
    
    async def calculate(self, expression):
        """Safe calculator with persona-driven responses"""
        try:
            if not isinstance(expression, str):
                logger.warning("Non-string calculation expression received")
                return "Please provide a valid math expression."
            
            if len(expression) > 200:
                logger.warning(f"Expression too long: {len(expression)} characters")
                return "Expression is too long. Keep it under 200 characters."
            
            # Simple safe evaluation for basic math
            allowed_chars = set('0123456789+-*/.() ')
            if not all(c in allowed_chars for c in expression):
                logger.warning(f"Invalid characters in expression: {expression}")
                return "Invalid characters in expression. Only math operators allowed."
            
            result = eval(expression)
            logger.info(f"Calculation successful: {expression} = {result}")
            persona_msg = self._get_persona_response("utilities", "calculate", expression=expression, result=result)
            return persona_msg or f"{expression} = {result}"
        except ZeroDivisionError:
            logger.warning("Division by zero attempted")
            return "Cannot divide by zero!"
        except (SyntaxError, ValueError) as e:
            logger.warning(f"Invalid expression: {e}")
            return f"Invalid expression: {str(e)}"
        except Exception as e:
            logger.error(f"Calculation error: {e}")
            print(f"⚠️ Calculation error: {e}")
            return "I couldn't calculate that..."
    
    async def get_random_fact(self):
        """Get a random fact using an API"""
        try:
            logger.info("Fetching random fact from API")
            response = requests.get(RANDOM_FACTS_API_URL, timeout=DEFAULT_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                fact = data['text']
                logger.info(f"Random fact retrieved: {fact[:50]}...")
                persona_msg = self._get_persona_response("utilities", "fact", fact=fact)
                return persona_msg or f"Here's a fact: {fact}"
            else:
                logger.warning(f"Fact API error: {response.status_code}")
                return "Couldn't fetch a fact right now."
                
        except requests.exceptions.Timeout:
            logger.warning("Fact API request timed out")
            return "Fact API request timed out."
        except requests.exceptions.RequestException as e:
            logger.error(f"Fact API error: {e}")
            print(f"⚠️ Fact API error: {e}")
            return "Can't get facts right now!"
    
    async def get_joke(self):
        """Get a random joke using an API"""
        try:
            logger.info("Fetching random joke from API")
            response = requests.get(JOKES_API_URL, timeout=DEFAULT_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                setup = data['setup']
                punchline = data['punchline']
                logger.info(f"Joke retrieved")
                persona_msg = self._get_persona_response("utilities", "joke", setup=setup, punchline=punchline)
                return persona_msg or f"Here's a joke:\n{setup}\n{punchline}"
            else:
                logger.warning(f"Joke API error: {response.status_code}")
                return "Couldn't fetch a joke right now."
                
        except requests.exceptions.Timeout:
            logger.warning("Joke API request timed out")
            return "Joke API request timed out."
        except requests.exceptions.RequestException as e:
            logger.error(f"Joke API error: {e}")
            print(f"⚠️ Joke API error: {e}")
            return "Can't get jokes right now!"
    
    async def get_cat_fact(self):
        """Get a random cat fact"""
        try:
            logger.info("Fetching random cat fact from API")
            response = requests.get(CAT_FACTS_API_URL, timeout=DEFAULT_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                fact = data['fact']
                logger.info(f"Cat fact retrieved: {fact[:50]}...")
                persona_msg = self._get_persona_response("utilities", "cat_fact", fact=fact)
                return persona_msg or f"Here's a cat fact: {fact}"
            else:
                logger.warning(f"Cat fact API error: {response.status_code}")
                return "Couldn't fetch a cat fact right now."
                
        except requests.exceptions.Timeout:
            logger.warning("Cat fact API request timed out")
            return "Cat fact API request timed out."
        except requests.exceptions.RequestException as e:
            logger.error(f"Cat fact API error: {e}")
            print(f"⚠️ Cat fact API error: {e}")
            return "Can't get cat facts right now!"