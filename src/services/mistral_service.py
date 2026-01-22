'''
Logic for interacting with the Mistral AI API
-> Maintains conversation history for context
'''
import os
from typing import List, Dict, Generator
from mistralai import Mistral


# ==== CONSTANTS ====
API_KEY_VAR = "MISTRAL_API_KEY"
DEFAULT_MODEL = "mistral-large-latest"


class MistralService:
    """
    Service for communicating with the Mistral AI API.
    Maintains conversation history to provide context.
    """

    def __init__(self) -> None:
        self._client = self._create_client()
        self._model = DEFAULT_MODEL
        self._conversation_history: List[Dict[str, str]] = []

    # ==================== CLIENT SETUP ====================

    def _create_client(self) -> Mistral:
        """Create Mistral API client from environment variable."""
        api_key = os.getenv(API_KEY_VAR)
        if not api_key:
            raise RuntimeError(f"Required environment variable '{API_KEY_VAR}' is not set")
        return Mistral(api_key=api_key)

    # ==================== PUBLIC METHODS ====================

    def send_message(self, user_message: str) -> str:
        """Send message to Mistral API and return full response."""
        self._add_to_history(role="user", content=user_message)
        
        response = self._client.chat.complete(
            model=self._model,
            messages=self._conversation_history
        )
        
        assistant_response = response.choices[0].message.content
        self._add_to_history(role="assistant", content=assistant_response)
        
        return assistant_response

    def send_message_stream(self, user_message: str) -> Generator[str, None, None]:
        """Send message and yield response chunks for typewriter effect."""
        self._add_to_history(role="user", content=user_message)
        
        full_response = ""
        
        # Use streaming API
        stream = self._client.chat.stream(
            model=self._model,
            messages=self._conversation_history
        )
        
        for chunk in stream:
            if chunk.data.choices[0].delta.content:
                text = chunk.data.choices[0].delta.content
                full_response += text
                yield text
        
        # Save complete response to history
        self._add_to_history(role="assistant", content=full_response)

    def clear_history(self) -> None:
        """Reset the conversation history."""
        self._conversation_history = []

    # ==================== HISTORY MANAGEMENT ====================

    def _add_to_history(self, role: str, content: str) -> None:
        """Append message to conversation history."""
        self._conversation_history.append({"role": role, "content": content})
