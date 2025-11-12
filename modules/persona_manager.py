"""
Persona Manager - Centralized personality system using persona cards
"""
import json
import random
import os

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
        """Generate AI system prompt with persona and relationship context"""
        base_prompt = self.persona.get("ai_system_prompt", "You are a helpful AI assistant.")
        
        # Add relationship context
        relationship_context = ""
        if relationship_level in self.persona.get("relationship_responses", {}):
            relationship_context = f"\n\nRelationship context: The user is a {relationship_level}. Adjust your tsundere responses accordingly - be more caring (but still defensive) with closer relationships."
        
        return f"{base_prompt}{relationship_context}\n\nUser question: {user_question}\n\nRespond in character:"
    
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