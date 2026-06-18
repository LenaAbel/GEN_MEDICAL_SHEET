'''
Logic for interacting with the Mistral AI API
-> Maintains conversation history for context
'''
import json
import os
from typing import Any, List, Dict, Generator
from mistralai import Mistral
from domain.models.prompts.prompts import SYSTEM_PROMPT


# ==== CONSTANTS ====
API_KEY_VAR = "MISTRAL_API_KEY"
DEFAULT_MODEL = "mistral-medium-latest"
AUDIO_CONTEXT_PREFIX = "CONTEXTE AUDIO PRÉ-OPÉRATOIRE STRUCTURÉ:"


class MistralService:
    """
    Service for communicating with the Mistral AI API.
    Maintains conversation history to provide context.
    """

    def __init__(self) -> None:
        self._client = self._create_client()
        self._model = DEFAULT_MODEL
        self._conversation_history: List[Dict[str, str]] = []
        self._audio_transcript_context: dict[str, Any] | None = None
        self._audio_context_added_to_history = False
        self._initialize_system_prompt()

    # ==================== CLIENT SETUP FOR MISTRAL ====================

    def _create_client(self) -> Mistral:
        """Create Mistral API client from environment variable."""
        api_key = os.getenv(API_KEY_VAR)
        if not api_key:
            raise RuntimeError(f"Required environment variable '{API_KEY_VAR}' is not set !")
        return Mistral(api_key=api_key)

    def _initialize_system_prompt(self) -> None:
        """Add system prompt to start of conversation."""
        self._conversation_history.append({
            "role": "system",
            "content": SYSTEM_PROMPT
        })

    # ==================== PUBLIC METHODS ====================

    def send_message(self, user_message: str) -> str:
        """Send message to Mistral API and return full response."""
        self._add_pending_audio_context_to_history()
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
        self._add_pending_audio_context_to_history()
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
        """Reset the conversation history and re-add system prompt."""
        self._conversation_history = []
        self._audio_transcript_context = None
        self._audio_context_added_to_history = False
        self._initialize_system_prompt()

    def set_audio_transcript_context(self, extracted_data: dict[str, Any]) -> None:
        """Attach structured audio extraction data to future chat requests."""
        self._remove_audio_context_from_history()
        self._audio_transcript_context = extracted_data
        self._audio_context_added_to_history = False

    def clear_audio_transcript_context(self) -> None:
        """Remove the structured audio extraction context."""
        self._audio_transcript_context = None
        self._audio_context_added_to_history = False
        self._remove_audio_context_from_history()

    # ==================== HISTORY MANAGEMENT ====================

    def _add_to_history(self, role: str, content: str) -> None:
        """Append message to conversation history."""
        self._conversation_history.append({"role": role, "content": content})

    def _add_pending_audio_context_to_history(self) -> None:
        """Inject compact audio JSON once into the chat history."""
        if (
            self._audio_transcript_context is None
            or self._audio_context_added_to_history
        ):
            return

        audio_json = json.dumps(
            self._audio_transcript_context,
            ensure_ascii=False,
            indent=2,
        )
        self._add_to_history(
            role="system",
            content=(
                f"{AUDIO_CONTEXT_PREFIX}\n"
                "Le JSON ci-dessous provient d'une transcription audio déjà résumée et "
                "validée. Il sert à récupérer les détails dits oralement pendant la "
                "consultation mais absents ou oubliés dans la fiche SFAR. Utilise-le "
                "uniquement comme complément aux données SFAR. N'invente rien. Si une "
                "information audio contredit la SFAR ou semble incertaine, reste prudent "
                "et indique qu'elle est à confirmer avec l'équipe d'anesthésie.\n"
                f"```json\n{audio_json}\n```\n\n"
                "N'utilise jamais la transcription brute: elle n'est pas fournie. "
                "Ne mentionne pas au patient que l'information vient d'un enregistrement."
            ),
        )
        self._audio_context_added_to_history = True

    def _remove_audio_context_from_history(self) -> None:
        """Remove any previous structured audio context message from history."""
        self._conversation_history = [
            message
            for message in self._conversation_history
            if not (
                message.get("role") == "system"
                and message.get("content", "").startswith(AUDIO_CONTEXT_PREFIX)
            )
        ]
