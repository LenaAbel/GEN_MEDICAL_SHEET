from PySide6.QtCore import QEvent, QObject, QThread, Signal

from services.mistral_request_thread import MistralRequestThread
from services.mistral_service import MistralService


class ChatController(QObject):
    """Orchestrate streaming chat request threads."""

    chunk_received = Signal(int, str)
    stream_finished = Signal(int)
    error_occurred = Signal(int, str)
    request_finished = Signal(int)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._mistral_service = MistralService()
        self._request_thread: MistralRequestThread | None = None
        self._threads: set[MistralRequestThread] = set()

    def event(self, event: QEvent) -> bool:
        """Join active workers before Qt destroys the controller."""
        if event.type() == QEvent.Type.DeferredDelete:
            self.cancel()
        return super().event(event)

    def send_message(self, conversation_id: int, user_message: str) -> None:
        """Start a streaming chat request for the current conversation."""
        thread = MistralRequestThread(self._mistral_service, user_message)
        self._request_thread = thread
        self._threads.add(thread)
        thread.chunk_received.connect(
            lambda chunk, cid=conversation_id: self.chunk_received.emit(cid, chunk)
        )
        thread.stream_finished.connect(
            lambda cid=conversation_id: self.stream_finished.emit(cid)
        )
        thread.error_occurred.connect(
            lambda error_message, cid=conversation_id: self.error_occurred.emit(
                cid,
                error_message,
            )
        )
        thread.finished.connect(
            lambda cid=conversation_id, active_thread=thread: self._finish_thread(
                active_thread,
                cid,
            )
        )
        thread.start()

    def clear_history(self) -> None:
        """Reset the chat service conversation history."""
        self._mistral_service.clear_history()

    def cancel(self, wait: bool = True) -> None:
        """Cancel tracked chat workers and optionally wait for completion."""
        self._request_thread = None
        if not wait:
            return

        for thread in tuple(self._threads):
            self._stop_thread(thread)
        self._threads.clear()

    def _finish_thread(
        self,
        thread: MistralRequestThread,
        conversation_id: int,
    ) -> None:
        if thread is self._request_thread:
            self._request_thread = None
        self._threads.discard(thread)
        thread.deleteLater()
        self.request_finished.emit(conversation_id)

    @staticmethod
    def _stop_thread(thread: QThread) -> None:
        thread.requestInterruption()
        thread.quit()
        thread.wait()
        thread.deleteLater()
