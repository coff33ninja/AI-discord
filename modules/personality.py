"""
Personality module - now uses centralized persona manager
"""
from .persona_manager import PersonaManager

class TsunderePersonality:
    def __init__(self, persona_file="persona_card.json"):
        self.persona_manager = PersonaManager(persona_file)

    def get_mention_response(self):
        return self.persona_manager.get_response("mention")
    
    def get_compliment_response(self):
        return self.persona_manager.get_response("compliment_received")
    
    def get_error_response(self, error):
        return self.persona_manager.format_error_response(error)
    
    def get_missing_args_response(self):
        return self.persona_manager.get_response("missing_args")
    
    def create_ai_prompt(self, question, relationship_level="stranger"):
        return self.persona_manager.get_ai_prompt(question, relationship_level)
    
    def get_name(self):
        return self.persona_manager.get_name()
    
    def reload_persona(self):
        return self.persona_manager.reload_persona()