"""
Persona Manager - Centralized personality system using persona cards
"""
import json
import random

# Constants for persona management
DEFAULT_PERSONA_FILE = "persona_card.json"
DEFAULT_PERSONA_NAME = "AI Assistant"
DEFAULT_PERSONA_PERSONALITY = "helpful"
DEFAULT_AI_PROMPT = "You are a helpful AI assistant."
AI_GENERATION_TIMEOUT = 15.0  # seconds

class PersonaManager:
    def __init__(self, persona_file="persona_card.json"):
        self.persona_file = persona_file
        self.persona = self.load_persona()
    
    def load_persona(self):
        """Load persona card from JSON file"""
        try:
            with open(self.persona_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {self.persona_file} not found. Using default persona.")
            return self.get_default_persona()
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in {self.persona_file}. Using default persona.")
            return self.get_default_persona()
    
    def get_default_persona(self):
        """Fallback default persona with all necessary response templates"""
        return {
            "name": DEFAULT_PERSONA_NAME,
            "personality": DEFAULT_PERSONA_PERSONALITY,
            "description": "A helpful AI assistant that provides assistance with various tasks",
            "core_traits": [
                "Helpful and informative",
                "Polite and professional",
                "Clear and concise communication",
                "Eager to assist users"
            ],
            "speech_patterns": {
                "greeting": ["Hello!", "Hi there!", "Good day!"],
                "acknowledgment": ["I understand", "Got it", "Certainly"],
                "thinking": ["Let me think about that", "One moment", "Processing..."],
                "completion": ["Done!", "Complete", "Finished"]
            },
            "response_templates": {
                "error": [
                    "I apologize, but something went wrong. Let me try to help you anyway.",
                    "There seems to be an issue, but I'm here to assist you.",
                    "Oops! Something didn't work as expected. How can I help you resolve this?"
                ],
                "mention": [
                    "Hello! You mentioned me. How can I assist you today?",
                    "Hi there! I'm here to help. What do you need?",
                    "You called? I'm ready to assist you with whatever you need."
                ],
                "compliment_received": [
                    "Thank you for the kind words! I'm happy to help.",
                    "I appreciate that! It's my pleasure to assist you.",
                    "That's very nice of you to say. How else can I help?"
                ],
                "missing_args": [
                    "I need a bit more information to help you with that.",
                    "Could you provide more details so I can assist you better?",
                    "I'm missing some information. Could you be more specific?"
                ]
            },
            "relationship_responses": {
                "stranger": {
                    "greeting": "Hello! I'm here to help you with whatever you need.",
                    "compliment": "Thank you! I'm glad I could be of assistance.",
                    "mood": "I'm doing well and ready to help you today!"
                },
                "acquaintance": {
                    "greeting": "Nice to see you again! How can I help you today?",
                    "compliment": "I appreciate your kind words! Happy to help as always.",
                    "mood": "I'm doing great! Thanks for asking. What can I do for you?"
                },
                "friend": {
                    "greeting": "Hey there! Good to see you again. What's on your mind?",
                    "compliment": "You're too kind! I really enjoy helping you out.",
                    "mood": "I'm feeling great today! Ready to tackle whatever you need help with."
                },
                "close_friend": {
                    "greeting": "Hello, my friend! Always a pleasure. What can I help you with?",
                    "compliment": "You always know how to make me feel appreciated! Thank you.",
                    "mood": "I'm wonderful, especially when I get to help good friends like you!"
                }
            },
            "activity_responses": {
                "weather": {
                    "success": "Here's the weather information for {location}: {weather_info}",
                    "error": "I'm sorry, I couldn't retrieve weather information for '{location}' right now."
                },
                "calculation": {
                    "success": "The result of {expression} is {result}.",
                    "error": "I couldn't calculate that expression. Please check the format and try again."
                },
                "games": {
                    "start": "Great! Let's play a game. I'm ready when you are!",
                    "win": "Congratulations! You won! Well played!",
                    "lose": "Better luck next time! Want to play again?",
                    "tie": "It's a tie! We both chose {choice}. Great minds think alike!",
                    "hint_low": "Too low! Try a higher number.",
                    "hint_high": "Too high! Try a lower number.",
                    "trivia_start": "Here's your trivia question:\n\n**{question}**\n\nTake your time!",
                    "trivia_timeout": "Time's up! The correct answer was '{answer}'. Better luck next time!",
                    "trivia_fast_correct": "Wow! Correct answer in {time:.1f} seconds! Impressive!",
                    "trivia_correct": "Correct! You got it right in {time:.1f} seconds. Well done!",
                    "trivia_wrong": "Sorry, that's not correct. The answer was '{answer}'. Try again next time!",
                    "no_active_game": "No active game found. Start a new game first!"
                },
                "magic_8ball": {
                    "answers": [
                        "Yes, definitely!",
                        "No, I don't think so.",
                        "Maybe, it's possible.",
                        "Absolutely!",
                        "Probably not.",
                        "Ask again later.",
                        "I think so.",
                        "Unlikely.",
                        "Most likely.",
                        "Yes, go for it!"
                    ],
                    "action": "*shakes magic 8-ball*"
                },
                "utilities": {
                    "dice": "You rolled: {result}",
                    "time": "The current time is {time}",
                    "coin": "The coin landed on: {result}",
                    "weather": "Here's the weather information for {location}: {weather_info}",
                    "calculate": "The result of {expression} is {result}",
                    "fact": "Here's an interesting fact: {fact}",
                    "joke": "Here's a joke for you:\n\n{setup}\n{punchline}",
                    "cat_fact": "Here's a cat fact: {fact}"
                },
                "facts": {
                    "success": [
                        "Here's an interesting fact: {fact}",
                        "Did you know? {fact}",
                        "Fun fact: {fact}"
                    ],
                    "error": [
                        "I couldn't retrieve a fact right now. Please try again later.",
                        "The fact service is currently unavailable.",
                        "Sorry, I can't get facts at the moment."
                    ]
                },
                "jokes": {
                    "success": [
                        "Here's a joke for you:\n\n{setup}\n{punchline}",
                        "Hope this makes you smile:\n\n{setup}\n{punchline}",
                        "Time for a joke:\n\n{setup}\n{punchline}"
                    ],
                    "error": [
                        "I couldn't get a joke right now. Maybe I can tell you one later!",
                        "The joke service is currently down. Sorry about that!",
                        "No jokes available at the moment, but I'm still here to help!"
                    ]
                },
                "cat_facts": {
                    "success": [
                        "Here's a cat fact: {fact}",
                        "Cat fact: {fact}",
                        "Did you know this about cats? {fact}"
                    ],
                    "error": [
                        "I couldn't get cat facts right now. Try again later!",
                        "The cat fact service is unavailable at the moment.",
                        "No cat facts available right now, but cats are still amazing!"
                    ]
                },
                "help_command": {
                    "title": "Available Commands",
                    "description": "Here are the commands I can help you with:",
                    "footer": "Use these commands to interact with me!"
                },
                "admin": {
                    "reload_success": "Configuration reloaded successfully: {result}",
                    "no_permission": "You don't have permission to use that command.",
                    "shutdown": [
                        "Shutting down now. Goodbye!",
                        "System shutdown initiated. See you later!",
                        "Goodbye! Shutting down the system.",
                        "Farewell! The system is shutting down."
                    ],
                    "restart": [
                        "Restarting the system now. I'll be back shortly!",
                        "System restart initiated. Please wait a moment.",
                        "Restarting now. See you in a moment!",
                        "System reboot in progress. Back soon!"
                    ]
                },
                "permissions": {
                    "no_send_permission": "I don't have permission to send messages in that channel.",
                    "general_permission_error": "I don't have the necessary permissions for that action."
                },
                "bot_status": "Ready to help! | Use !help_ai for commands",
                "server_actions": {
                    "no_permission": "You don't have permission to use that command.",
                    "user_not_found": "I couldn't find that user. Are they in this server?",
                    "role_not_found": "I couldn't find a role with that name.",
                    "channel_not_found": "I couldn't find that channel.",
                    "already_has_role": "{user} already has that role.",
                    "doesnt_have_role": "{user} doesn't have that role.",
                    "cant_kick_self": "I can't kick myself from the server.",
                    "hierarchy_error": "I can't perform that action on someone with a higher role.",
                    "success_mention": "Hey {user}! Someone wanted to get your attention.",
                    "success_role_give": "Successfully gave {user} the {role} role.",
                    "success_role_remove": "Successfully removed the {role} role from {user}.",
                    "success_kick": "{user} has been kicked from the server.",
                    "success_role_create": "Successfully created the '{role_name}' role.",
                    "success_channel": "Successfully created the {type} channel {channel}.",
                    "success_message": "Message delivered to {channel}."
                },
                "search": {
                    "instant_answer": [
                        "Here's your answer: **{answer}**",
                        "I found this: **{answer}**",
                        "The answer is: **{answer}**"
                    ],
                    "abstract": [
                        "I found this information about **{query}**:\n\n{abstract}\n\n*Source: {source}*",
                        "Here's what I found on **{query}**:\n\n{abstract}\n\n*From: {source}*",
                        "Information about **{query}**:\n\n{abstract}\n\n*Source: {source}*"
                    ],
                    "related_topics": [
                        "Here are the search results for **{query}**:\n\n{results}",
                        "I found these results for **{query}**:\n\n{results}",
                        "Search results for **{query}**:\n\n{results}"
                    ],
                    "definition": [
                        "Here's the definition of **{query}**:\n\n{definition}\n\n*Source: {source}*",
                        "**{query}** means:\n\n{definition}\n\n*From: {source}*"
                    ],
                    "web_results": [
                        "Here are the web search results for **{query}**:\n\n{results}",
                        "Web search results for **{query}**:\n\n{results}",
                        "I found these web results for **{query}**:\n\n{results}"
                    ],
                    "no_results": [
                        "I couldn't find any results for **{query}**. Try a different search term.",
                        "No results found for **{query}**. Please try rephrasing your search.",
                        "Sorry, no results for **{query}**. Try searching for something else."
                    ],
                    "error": [
                        "Search is currently unavailable. Please try again later.",
                        "I'm having trouble with the search function right now.",
                        "Search service is temporarily down. Try again in a moment."
                    ],
                    "timeout": [
                        "The search is taking too long. Please try a simpler query.",
                        "Search timed out. Try searching for something more specific.",
                        "The search took too long to complete. Please try again."
                    ]
                },
                "reminders": {
                    "reminder_ping": [
                        "Hey {user_mention}! Here's your reminder:",
                        "{user_mention}, you asked me to remind you about this:",
                        "Reminder for {user_mention}:"
                    ]
                }
            },
            "ai_system_prompt": "You are a helpful AI assistant. You are polite, informative, and eager to help users with their questions and tasks. Provide clear, accurate, and helpful responses while maintaining a friendly and professional tone."
        }
    
    def get_name(self):
        """Get persona name"""
        return self.persona.get("name", DEFAULT_PERSONA_NAME)
    
    def get_ai_prompt(self, user_question, relationship_level="stranger"):
        """Generate AI system prompt with full persona card context"""
        # Pass the entire persona card to the AI
        persona_json = json.dumps(self.persona, indent=2)
        
        prompt = f"""You are an AI that must understand and embody the personality described in this persona card:

PERSONA CARD:
{persona_json}

INSTRUCTIONS:
1. Read and understand your complete personality from the persona card above
2. You ARE the character described - embody them completely in your responses
3. Your relationship with this user is: {relationship_level}
4. Respond naturally as this character would, using their speech patterns and personality traits

USER QUESTION: {user_question}

Generate an authentic response as the character described in the persona card."""
        
        return prompt
    
    def get_ai_response_prompt(self, user_action, user_name, relationship_level="stranger"):
        """Generate AI prompt based on persona card and user action"""
        # Pass the persona card to AI so it can embody the personality
        persona_json = json.dumps(self.persona, indent=2)
        
        prompt = f"""PERSONA CARD:
{persona_json}

You ARE the character described above. Embody this personality completely.

USER ACTION: {user_name} just used: {user_action}
RELATIONSHIP LEVEL: {relationship_level}

Based on your personality and what the user did, generate ONE authentic response. Stay in character."""
        
        return prompt
    
    def create_ai_prompt(self, user_action, user_name=None, relationship_level="stranger"):
        """Create AI prompt for use with API manager"""
        if user_name:
            return self.get_ai_response_prompt(user_action, user_name, relationship_level)
        else:
            # For general AI questions without specific user context
            persona_json = json.dumps(self.persona, indent=2)
            
            prompt = f"""PERSONA CARD:
{persona_json}

You ARE the character described above. Embody this personality completely.

USER QUESTION: {user_action}

Generate an authentic response as the character described in the persona card."""
            
            return prompt
    
    def get_response(self, response_type, **kwargs):
        """Get a random response of the specified type with comprehensive fallbacks"""
        responses = self.persona.get("response_templates", {}).get(response_type, [])
        
        # If no responses found, provide generic fallbacks
        if not responses:
            fallback_responses = {
                "error": ["I apologize, but something went wrong. How can I help you?"],
                "mention": ["Hello! How can I assist you today?"],
                "compliment_received": ["Thank you! I'm happy to help."],
                "missing_args": ["I need more information to help you with that."],
                "greeting": ["Hello! How can I help you today?"],
                "goodbye": ["Goodbye! Have a great day!"],
                "thanks": ["You're welcome! Happy to help."],
                "unknown": ["I'm not sure about that, but I'm here to help however I can."]
            }
            responses = fallback_responses.get(response_type, [f"I'm here to help with {response_type}."])
        
        response = random.choice(responses)
        
        # Format response with any provided kwargs
        try:
            return response.format(**kwargs)
        except (KeyError, ValueError):
            # If formatting fails, return the unformatted response
            return response
    
    async def get_ai_generated_response(self, model, user_action, user_name, relationship_level="stranger"):
        """Generate a response using AI based on persona and user action"""
        import asyncio
        import concurrent.futures
        
        try:
            prompt = self.get_ai_response_prompt(user_action, user_name, relationship_level)
            
            # Generate response using Gemini with timeout protection
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                try:
                    response = await asyncio.wait_for(
                        loop.run_in_executor(executor, model.generate_content, prompt),
                        timeout=AI_GENERATION_TIMEOUT
                    )
                    return response.text.strip()
                except asyncio.TimeoutError:
                    # Fallback to template response if AI times out
                    return self.get_response("error")
        except Exception:
            # Fallback to template response if AI fails
            return self.get_response("error")
    
    def get_relationship_response(self, relationship_level, response_type, **kwargs):
        """Get relationship-specific response with comprehensive fallbacks"""
        rel_responses = self.persona.get("relationship_responses", {})
        
        # Try the specific relationship level first
        if relationship_level in rel_responses:
            response = rel_responses[relationship_level].get(response_type)
            if response:
                try:
                    return response.format(**kwargs)
                except (KeyError, ValueError):
                    return response
        
        # Fall back to stranger level
        if "stranger" in rel_responses:
            response = rel_responses["stranger"].get(response_type)
            if response:
                try:
                    return response.format(**kwargs)
                except (KeyError, ValueError):
                    return response
        
        # Ultimate fallbacks if nothing is configured
        fallback_responses = {
            "greeting": "Hello! How can I help you today?",
            "compliment": "Thank you! I appreciate that.",
            "mood": "I'm doing well, thank you for asking!",
            "goodbye": "Goodbye! Have a great day!",
            "thanks": "You're welcome!",
            "help": "I'm here to help you with whatever you need."
        }
        
        response = fallback_responses.get(response_type, "Hi there!")
        
        try:
            return response.format(**kwargs)
        except (KeyError, ValueError):
            return response
    
    def get_activity_response(self, activity, result_type, **kwargs):
        """Get activity-specific response with comprehensive fallbacks"""
        activity_responses = self.persona.get("activity_responses", {})
        
        # If activity not found, provide generic fallbacks
        if activity not in activity_responses:
            generic_fallbacks = {
                "success": "Operation completed successfully!",
                "error": "I'm sorry, something went wrong with that request.",
                "timeout": "That operation took too long to complete.",
                "no_permission": "You don't have permission for that action.",
                "not_found": "I couldn't find what you're looking for.",
                "invalid_input": "Please check your input and try again."
            }
            response = generic_fallbacks.get(result_type, "Something happened!")
        else:
            response = activity_responses[activity].get(result_type)
            
            # If specific response not found, try generic fallbacks
            if response is None:
                generic_fallbacks = {
                    "success": "Operation completed successfully!",
                    "error": "I'm sorry, something went wrong.",
                    "timeout": "That took too long to complete.",
                    "no_permission": "You don't have permission for that.",
                    "not_found": "I couldn't find that.",
                    "invalid_input": "Please check your input."
                }
                response = generic_fallbacks.get(result_type, "Something happened!")
        
        # Handle list responses (like shutdown/restart messages)
        if isinstance(response, list):
            response = random.choice(response)
        
        try:
            return response.format(**kwargs)
        except (KeyError, ValueError, AttributeError):
            # If formatting fails, return the unformatted response or a generic message
            if isinstance(response, str):
                return response
            else:
                return f"Completed {activity} operation."
    
    def get_speech_pattern(self, pattern_type):
        """Get random speech pattern element"""
        patterns = self.persona.get("speech_patterns", {}).get(pattern_type, [])
        if not patterns:
            return ""
        return random.choice(patterns)
    
    def format_error_response(self, error):
        """Format error with persona flair and robust fallbacks"""
        try:
            base_response = self.get_response("error")
            # Don't include the actual error details in user-facing messages for security
            return base_response
        except Exception:
            # Ultimate fallback if everything fails
            return "I apologize, but something went wrong. Please try again or contact support if the issue persists."
    
    def reload_persona(self):
        """Reload persona from file (useful for live updates)"""
        self.persona = self.load_persona()
        return f"Persona reloaded: {self.get_name()}"