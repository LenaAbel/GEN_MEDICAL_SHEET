import os
from mistralai import Mistral
from models.message import Message, Role

class MistralService:
    def __init__(self):
        # Read API key from environment and initialize client
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise RuntimeError("Require MISTRAL_API_KEY in environment")
        self.client = Mistral(api_key=api_key)
        self.model = "mistral-large-latest"
        # Keep conversation history for context
        self.history = []

    def send_message(self, user_text: str) -> str:
        # Append user message to history
        self.history.append({"role": "user", "content": user_text})
        
        # Call Mistral chat API with full history
        response = self.client.chat.complete(model=self.model, messages=self.history)
        
        # Extract assistant content and store in history
        assistant_text = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": assistant_text})
        
        # Return assistant reply text
        return assistant_text

    def clear_history(self):
        # Reset conversation history
        self.history = []
