"""Background thread for structured transcript extraction requests."""

from PySide6.QtCore import QThread, Signal

from services.transcript_extraction_service import TranscriptExtractionService


class TranscriptExtractionRequestThread(QThread):
    """Run transcript extraction without blocking the UI."""

    extraction_finished = Signal(object)
    error_occurred = Signal(str)

    def __init__(
        self,
        extraction_service: TranscriptExtractionService,
        transcript_text: str,
    ) -> None:
        super().__init__()
        self._extraction_service = extraction_service
        self._transcript_text = transcript_text

    def run(self) -> None:
        try:
            extracted_data = self._extraction_service.extract_structured_data(
                self._transcript_text
            )
            self.extraction_finished.emit(extracted_data)
        except Exception as exc:
            self.error_occurred.emit(str(exc))
