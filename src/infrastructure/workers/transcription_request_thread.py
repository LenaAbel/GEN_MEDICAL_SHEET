"""Background thread for audio transcription requests."""

from pathlib import Path

from PySide6.QtCore import QThread, Signal

from infrastructure.ai.transcription_service import TranscriptionService


class TranscriptionRequestThread(QThread):
    """Run audio transcription without blocking the UI."""

    transcription_finished = Signal(str)
    error_occurred = Signal(str)

    def __init__(
        self,
        transcription_service: TranscriptionService,
        audio_path: str | Path,
    ) -> None:
        super().__init__()
        self._transcription_service = transcription_service
        self._audio_path = audio_path

    def run(self) -> None:
        try:
            transcript = self._transcription_service.transcribe_audio(self._audio_path)
            self.transcription_finished.emit(transcript)
        except Exception as exc:
            self.error_occurred.emit(str(exc))
