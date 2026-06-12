"""Isolated audio transcription service backed by Mistral."""

import os
from pathlib import Path
from typing import Any

from mistralai import Mistral


API_KEY_VAR = "MISTRAL_API_KEY"
DEFAULT_TRANSCRIPTION_MODEL = "voxtral-mini-latest"


class TranscriptionError(RuntimeError):
    """Raised when an audio file cannot be transcribed."""


class TranscriptionService:
    """Convert an audio file to raw text without clinical extraction."""

    def __init__(
        self,
        client: Any | None = None,
        model: str = DEFAULT_TRANSCRIPTION_MODEL,
    ) -> None:
        self._client = client if client is not None else self._create_client()
        self._model = model

    def _create_client(self) -> Mistral:
        api_key = os.getenv(API_KEY_VAR)
        if not api_key:
            raise RuntimeError(
                f"La variable d'environnement requise '{API_KEY_VAR}' n'est pas définie."
            )
        return Mistral(api_key=api_key)

    def transcribe_audio(self, audio_path: str | Path) -> str:
        """Return the raw transcription of a local audio file."""
        path = Path(audio_path)
        if not path.is_file():
            raise FileNotFoundError(f"Fichier audio introuvable : {path}")

        try:
            with path.open("rb") as audio_file:
                response = self._client.audio.transcriptions.complete(
                    model=self._model,
                    file={
                        "content": audio_file,
                        "file_name": path.name,
                    },
                )
        except Exception as exc:
            raise TranscriptionError(
                f"La transcription audio a échoué pour '{path.name}' : {exc}"
            ) from exc

        transcript = getattr(response, "text", None)
        if not isinstance(transcript, str) or not transcript.strip():
            raise TranscriptionError(
                f"La transcription audio de '{path.name}' est vide ou invalide."
            )
        return transcript.strip()
