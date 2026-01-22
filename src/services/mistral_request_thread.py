"""
Background thread for Mistral API calls.
Prevents UI freeze during network requests.
"""
from PySide6.QtCore import QThread, Signal
from services.mistral_service import MistralService


class MistralRequestThread(QThread):
    """
    Execute Mistral API call in background thread.
    
    Why a thread?
    - Network calls to Mistral takes time (1-10 seconds)
    - Running on main thread would freeze the UI
    - This thread runs separately, UI stays responsive

    Flow:
    1. MainWindow creates thread with message
    2. start() triggers run() in background
    3. run() calls MistralService (network call)
    4. Signal emitted back to main thread
    5. MainWindow updates UI
    """

    # ==================== SIGNALS ====================
    
    # Emitted with assistant response on success
    response_ready = Signal(str)
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
        Execute API call in background.
        
        Runs OFF the main UI thread.
        Never update UI directly — use signals instead.
        """
        try:
            assistant_text = self._mistral_service.send_message(self._user_message)
            self.response_ready.emit(assistant_text)
        except Exception as e:
            self.error_occurred.emit(str(e))
