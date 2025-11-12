"""
Persona Manager - Centralized personality system using persona cards
"""
import json
import random

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
        """Fallback default persona"""
        return {
            "name": "AI Assistant",
            "personality": "helpful",
            "ai_system_prompt": "You are a helpful AI assistant."
        }
    
    def get_name(self):
        """Get persona name"""
        return self.persona.get("name", "AI Assistant")
    
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
        """Get a random response of the specified type"""
        responses = self.persona.get("response_templates", {}).get(response_type, [])
        if not responses:
            return f"*{response_type} response not configured*"
        
        response = random.choice(responses)
        
        # Format response with any provided kwargs
        try:
            return response.format(**kwargs)
        except KeyError:
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
                        timeout=15.0  # 15 second timeout for quick responses
                    )
                    return response.text.strip()
                except asyncio.TimeoutError:
                    # Fallback to template response if AI times out
                    return self.get_response("error")
        except Exception:
            # Fallback to template response if AI fails
            return self.get_response("error")
    
    def get_relationship_response(self, relationship_level, response_type, **kwargs):
        """Get relationship-specific response"""
        rel_responses = self.persona.get("relationship_responses", {})
        if relationship_level not in rel_responses:
            relationship_level = "stranger"
        
        response = rel_responses[relationship_level].get(response_type, "Hi there!")
        
        try:
            return response.format(**kwargs)
        except KeyError:
            return response
    
    def get_activity_response(self, activity, result_type, **kwargs):
        """Get activity-specific response (weather, calculation, etc.)"""
        activity_responses = self.persona.get("activity_responses", {})
        if activity not in activity_responses:
            return self.get_response("error")
        
        response = activity_responses[activity].get(result_type, "Something happened!")
        
        try:
            return response.format(**kwargs)
        except KeyError:
            return response
    
    def get_speech_pattern(self, pattern_type):
        """Get random speech pattern element"""
        patterns = self.persona.get("speech_patterns", {}).get(pattern_type, [])
        if not patterns:
            return ""
        return random.choice(patterns)
    
    def format_error_response(self, error):
        """Format error with persona flair"""
        base_response = self.get_response("error")
        return f"{base_response} Error: {str(error)}"
    
    def reload_persona(self):
        """Reload persona from file (useful for live updates)"""
        self.persona = self.load_persona()
        return f"Persona reloaded: {self.get_name()}"