from pathlib import Path

from PySide6.QtCore import QEvent, QObject, QThread, Signal

from services.transcript_extraction_request_thread import (
    TranscriptExtractionRequestThread,
)
from services.transcript_extraction_service import TranscriptExtractionService
from services.transcription_request_thread import TranscriptionRequestThread
from services.transcription_service import TranscriptionService


class TranscriptionController(QObject):
    """Orchestrate transcription and extraction request threads."""

    transcription_finished = Signal(str)
    transcription_error = Signal(str)
    transcription_thread_finished = Signal()
    extraction_finished = Signal(object)
    extraction_error = Signal(str)
    extraction_thread_finished = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._transcription_thread: TranscriptionRequestThread | None = None
        self._extraction_thread: TranscriptExtractionRequestThread | None = None

    def event(self, event: QEvent) -> bool:
        """Join active workers before Qt destroys the controller."""
        if event.type() == QEvent.Type.DeferredDelete:
            self.cancel()
        return super().event(event)

    @property
    def is_transcribing(self) -> bool:
        """Return whether a transcription request is active."""
        return self._transcription_thread is not None

    @property
    def is_extracting(self) -> bool:
        """Return whether an extraction request is active."""
        return self._extraction_thread is not None

    def start_transcription(self, audio_path: Path) -> None:
        """Create and start a transcription request thread."""
        try:
            transcription_service = TranscriptionService()
        except Exception as exc:
            self.transcription_error.emit(str(exc))
            return

        thread = TranscriptionRequestThread(transcription_service, audio_path)
        self._transcription_thread = thread
        thread.transcription_finished.connect(
            lambda transcript, active_thread=thread: self._emit_transcription_finished(
                active_thread,
                transcript,
            )
        )
        thread.error_occurred.connect(
            lambda error_message, active_thread=thread: self._emit_transcription_error(
                active_thread,
                error_message,
            )
        )
        thread.finished.connect(
            lambda active_thread=thread: self._finish_transcription_thread(
                active_thread
            )
        )
        thread.start()

    def start_extraction(self, transcript: str) -> None:
        """Create and start a structured extraction request thread."""
        try:
            extraction_service = TranscriptExtractionService()
        except Exception as exc:
            self.extraction_error.emit(str(exc))
            self.extraction_thread_finished.emit()
            return

        thread = TranscriptExtractionRequestThread(extraction_service, transcript)
        self._extraction_thread = thread
        thread.extraction_finished.connect(
            lambda extracted_data, active_thread=thread: self._emit_extraction_finished(
                active_thread,
                extracted_data,
            )
        )
        thread.error_occurred.connect(
            lambda error_message, active_thread=thread: self._emit_extraction_error(
                active_thread,
                error_message,
            )
        )
        thread.finished.connect(
            lambda active_thread=thread: self._finish_extraction_thread(active_thread)
        )
        thread.start()

    def cancel(self) -> None:
        """Cancel and join any active transcription or extraction flow."""
        transcription_thread = self._transcription_thread
        extraction_thread = self._extraction_thread
        self._transcription_thread = None
        self._extraction_thread = None

        if transcription_thread is not None:
            self._stop_thread(transcription_thread)
            self.transcription_thread_finished.emit()

        if extraction_thread is not None:
            self._stop_thread(extraction_thread)
            self.extraction_thread_finished.emit()

    def _emit_transcription_finished(
        self,
        thread: TranscriptionRequestThread,
        transcript: str,
    ) -> None:
        if thread is self._transcription_thread:
            self.transcription_finished.emit(transcript)

    def _emit_transcription_error(
        self,
        thread: TranscriptionRequestThread,
        error_message: str,
    ) -> None:
        if thread is self._transcription_thread:
            self.transcription_error.emit(error_message)

    def _finish_transcription_thread(
        self,
        thread: TranscriptionRequestThread,
    ) -> None:
        if thread is not self._transcription_thread:
            return
        self._transcription_thread = None
        thread.deleteLater()
        self.transcription_thread_finished.emit()

    def _emit_extraction_finished(
        self,
        thread: TranscriptExtractionRequestThread,
        extracted_data: object,
    ) -> None:
        if thread is self._extraction_thread:
            self.extraction_finished.emit(extracted_data)

    def _emit_extraction_error(
        self,
        thread: TranscriptExtractionRequestThread,
        error_message: str,
    ) -> None:
        if thread is self._extraction_thread:
            self.extraction_error.emit(error_message)

    def _finish_extraction_thread(
        self,
        thread: TranscriptExtractionRequestThread,
    ) -> None:
        if thread is not self._extraction_thread:
            return
        self._extraction_thread = None
        thread.deleteLater()
        self.extraction_thread_finished.emit()

    @staticmethod
    def _stop_thread(thread: QThread) -> None:
        thread.requestInterruption()
        thread.quit()
        thread.wait()
        thread.deleteLater()
