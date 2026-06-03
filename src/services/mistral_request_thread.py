"""
Background thread for Mistral API calls.
Prevents UI freeze during network requests.
"""
from PySide6.QtCore import QThread, Signal
from services.mistral_service import MistralService


class MistralRequestThread(QThread):
    """
    Execute Mistral API call in background thread.

    Flow:
    1. MainWindow creates thread with message
    2. start() triggers run() in background
    3. run() calls MistralService (network call)
    4. Signal emitted back to main thread
    5. MainWindow updates UI
    """

    # ==================== SIGNALS ====================
    
    # Emitted with each text chunk as it arrives
    chunk_received = Signal(str)
    # Emitted when streaming is complete
    stream_finished = Signal()
    # Emitted with error message on failure
    error_occurred = Signal(str)

    # ==================== INITIALIZATION ====================

    def __init__(self, mistral_service: MistralService, user_message: str) -> None:
        super().__init__()
        self._mistral_service = mistral_service
        self._user_message = user_message

    # ==================== THREAD EXECUTION ====================

    def run(self) -> None:
        """
        Execute streaming API call in background.
        Emits chunks as they arrive for typewriter effect.
        """
        try:
            for chunk in self._mistral_service.send_message_stream(self._user_message):
                self.chunk_received.emit(chunk)
            self.stream_finished.emit()
        except Exception as e:
            self.error_occurred.emit(str(e))
