import tempfile
import uuid
from pathlib import Path

from PySide6.QtCore import QElapsedTimer, QTimer, Qt, QUrl
from PySide6.QtGui import QPixmap
from PySide6.QtMultimedia import (
    QMediaDevices,
    QMediaRecorder,
)
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QMessageBox
)

from config.constants import WINDOW_MIN_SIZE, WINDOW_TITLE
from ui.widgets.chat_area import ChatArea
from ui.widgets.header_widget import HeaderWidget, LOGO_PATH
from ui.widgets.input_widget import InputWidget
from ui.style.styles import (
    MAIN_WINDOW_STYLE, RECORDING_BUTTON_STYLE, RECORDING_TIMER_STYLE,
    TRANSCRIPTION_BUTTON_STYLE, TRANSCRIPTION_TIMER_STYLE
)
from application.controllers.chat_controller import ChatController
from application.controllers.transcription_controller import TranscriptionController
from infrastructure.audio.audio_recorder_manager import AudioRecorderManager
from domain.models.message import Role
from ui.style.responsive import main_window_metrics


class MainWindow(QMainWindow):
    """Main chat window for Medical Sheet Generator."""

    def __init__(self) -> None:
        super().__init__()
        self._configure_window()
        self._chat_controller = ChatController(self)
        self._chat_controller.chunk_received.connect(self._on_chunk_received)
        self._chat_controller.stream_finished.connect(self._on_stream_finished)
        self._chat_controller.error_occurred.connect(self._on_error)
        self._chat_controller.request_finished.connect(self._on_thread_finished)
        self._recorded_audio_path: Path | None = None
        self._recording_stop_requested = False
        self._transcription_controller = TranscriptionController(self)
        self._transcription_controller.transcription_finished.connect(
            self._on_transcription_finished
        )
        self._transcription_controller.transcription_error.connect(
            self._on_transcription_error
        )
        self._transcription_controller.transcription_thread_finished.connect(
            self._on_transcription_thread_finished
        )
        self._transcription_controller.extraction_finished.connect(
            self._on_extraction_finished
        )
        self._transcription_controller.extraction_error.connect(
            self._on_extraction_error
        )
        self._transcription_controller.extraction_thread_finished.connect(
            self._on_extraction_thread_finished
        )
        self._audio_manager = AudioRecorderManager(self)
        self._audio_manager.recorderStateChanged.connect(
            self._on_recorder_state_changed
        )
        self._audio_manager.actualLocationChanged.connect(
            self._on_recording_location_changed
        )
        self._audio_manager.errorOccurred.connect(self._on_recorder_error)
        self._transcription_timer = QTimer(self)
        self._transcription_timer.setInterval(100)
        self._transcription_timer.timeout.connect(self._update_transcription_timer)
        self._transcription_elapsed = QElapsedTimer()
        self._conversation_session_id = 0
        self._setup_ui()

    # ==================== WINDOW CONFIGURATION ====================
    
    def _configure_window(self) -> None:
        """Set window title, size and theme."""
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(*WINDOW_MIN_SIZE)
        self.setStyleSheet(MAIN_WINDOW_STYLE)

    # ==================== UI SETUP ====================

    def _setup_ui(self) -> None:
        """Build main UI layout."""
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # HEADER
        self._header = HeaderWidget()
        self._logo_label = self._header.logo_label
        self._audio_spinner = self._header.audio_spinner
        self._transcription_timer_label = self._header.transcription_timer_label
        self._transcription_button = self._header.transcription_button
        self._new_conversation_button = self._header.new_conversation_button
        self._header.transcription_toggled.connect(
            self._on_transcription_clicked
        )
        self._header.new_conversation_requested.connect(
            self._start_new_conversation
        )
        main_layout.addWidget(self._header)

        # CHAT AREA with scrollable conversation and message bubbles
        self._chat_area = ChatArea()
        self._chat_widget = self._chat_area.chat_widget
        main_layout.addWidget(self._chat_area, stretch=1)
        
        # INPUT with AI disclaimer, text field, send button, and loading spinner
        self._input_widget = InputWidget()
        self._input_container = self._input_widget._input_container
        self._input_field = self._input_widget._input_field
        self._send_button = self._input_widget._send_button
        self._spinner = self._input_widget._spinner
        self._disclaimer = self._input_widget._disclaimer
        self._input_widget._send_button.clicked.connect(self._on_send_clicked)
        main_layout.addWidget(self._input_widget)
        self._apply_responsive_layout(self.width())

    # ==================== EVENT HANDLERS ====================

    def _on_transcription_clicked(self) -> None:
        """Start or stop microphone recording."""
        if self._audio_manager.is_recording():
            self._stop_audio_recording()
            return

        if not QMediaDevices.audioInputs():
            QMessageBox.warning(
                self,
                "Enregistrement audio",
                "Aucun microphone n'est disponible sur cet appareil.",
            )
            return

        self._cleanup_recorded_audio()
        self._new_conversation_button.setEnabled(False)
        self._recorded_audio_path = (
            Path(tempfile.gettempdir()) / f"gen_medical_sheet_{uuid.uuid4().hex}.wav"
        )
        self._recording_stop_requested = False

        self._transcription_button.setAccessibleName("Arrêter l'enregistrement audio")
        self._transcription_button.setToolTip("Arrêter l'enregistrement audio")
        self._transcription_button.setStatusTip("Arrêter l'enregistrement audio")
        self._transcription_button.setStyleSheet(RECORDING_BUTTON_STYLE)
        self._transcription_timer_label.setText("Enregistrement 00:00")
        self._transcription_timer_label.setStyleSheet(RECORDING_TIMER_STYLE)
        self._transcription_timer_label.show()
        self._transcription_elapsed.start()
        self._transcription_timer.start()
        self._audio_manager.start(self._recorded_audio_path)

    def _stop_audio_recording(self) -> None:
        """Stop recording and wait for Qt to finish writing the audio file."""
        if not self._audio_manager.is_recording():
            return
        self._recording_stop_requested = True
        self._audio_manager.stop()
        self._stop_transcription_timer()
        self._set_audio_processing_status("Préparation audio...")

    def _on_recorder_state_changed(
        self,
        state: QMediaRecorder.RecorderState,
    ) -> None:
        """Start transcription only after the recorder has flushed the WAV file."""
        if state != QMediaRecorder.RecorderState.StoppedState:
            return
        if not self._recording_stop_requested:
            return
        self._recording_stop_requested = False
        QTimer.singleShot(0, self._start_transcription)

    def _on_recording_location_changed(self, location: QUrl) -> None:
        """Track the final path selected by the Qt multimedia backend."""
        if location.isLocalFile():
            self._recorded_audio_path = Path(location.toLocalFile())

    def _start_transcription(self) -> None:
        """Transcribe the completed recording outside the chat conversation."""
        if (
            self._recorded_audio_path is None
            or not self._recorded_audio_path.is_file()
        ):
            self._on_transcription_error(
                "Le fichier audio enregistré est introuvable ou n'a pas pu être finalisé."
            )
            return
        self._set_audio_processing_status("Transcription en cours...")
        self._transcription_controller.start_transcription(self._recorded_audio_path)

    def _update_transcription_timer(self) -> None:
        """Refresh the visible elapsed transcription time."""
        elapsed_seconds = self._transcription_elapsed.elapsed() // 1000
        minutes, seconds = divmod(elapsed_seconds, 60)
        self._transcription_timer_label.setText(
            f"Enregistrement {minutes:02d}:{seconds:02d}"
        )

    def _on_transcription_finished(self, transcript: str) -> None:
        """Automatically start extraction without displaying the raw transcript."""
        self._set_audio_processing_status("Extraction en cours...")
        self._start_extraction(transcript)

    def _on_transcription_error(self, error_message: str) -> None:
        """Display a clear audio transcription error."""
        self._stop_transcription_timer()
        self._audio_spinner.stop()
        self._transcription_timer_label.setText("Transcription échouée")
        self._reset_recording_button()
        self._cleanup_recorded_audio()
        self._new_conversation_button.setEnabled(
            not self._transcription_controller.is_transcribing
        )
        QMessageBox.warning(self, "Transcription audio", error_message)

    def _on_transcription_thread_finished(self) -> None:
        """Release the completed audio request thread."""
        self._cleanup_recorded_audio()
        if not self._transcription_controller.is_extracting:
            self._reset_recording_button()
            self._new_conversation_button.setEnabled(True)

    def _stop_transcription_timer(self) -> None:
        """Stop timer updates while keeping the final duration visible."""
        if self._transcription_timer.isActive():
            self._update_transcription_timer()
            self._transcription_timer.stop()

    def _reset_recording_button(self) -> None:
        """Restore the recording button after processing completes."""
        self._transcription_button.setAccessibleName("Enregistrer l'audio")
        self._transcription_button.setToolTip("Démarrer un enregistrement audio")
        self._transcription_button.setStatusTip("Démarrer un enregistrement audio")
        self._transcription_button.setStyleSheet(TRANSCRIPTION_BUTTON_STYLE)
        self._transcription_button.setEnabled(True)
        self._transcription_button.show()

    def _set_audio_processing_status(self, status: str) -> None:
        """Show one compact processing status instead of reusing the action button."""
        self._transcription_button.hide()
        self._transcription_timer_label.setText(status)
        self._transcription_timer_label.setStyleSheet(TRANSCRIPTION_TIMER_STYLE)
        self._transcription_timer_label.show()
        self._audio_spinner.start()

    def _on_recorder_error(
        self,
        _error: QMediaRecorder.Error,
        error_message: str,
    ) -> None:
        """Handle microphone and recording backend errors."""
        self._recording_stop_requested = False
        self._stop_transcription_timer()
        self._audio_spinner.stop()
        self._transcription_timer_label.setText("Enregistrement échoué")
        self._transcription_timer_label.setStyleSheet(TRANSCRIPTION_TIMER_STYLE)
        self._transcription_timer_label.show()
        self._reset_recording_button()
        self._cleanup_recorded_audio()
        self._new_conversation_button.setEnabled(True)
        QMessageBox.warning(
            self,
            "Enregistrement audio",
            error_message or "L'enregistrement audio a échoué.",
        )

    def _start_extraction(self, transcript: str) -> None:
        """Automatically extract compact data from the isolated raw transcript."""
        self._new_conversation_button.setEnabled(False)
        self._transcription_controller.start_extraction(transcript)

    def _on_extraction_finished(self, extracted_data: object) -> None:
        """Attach structured JSON to chat context without exposing it in the chatbot."""
        if isinstance(extracted_data, dict):
            self._chat_controller.set_audio_transcript_context(extracted_data)
            self._input_widget.show_audio_context_badge()
        self._audio_spinner.stop()

    def _on_extraction_error(self, error_message: str) -> None:
        """Display a clear structured extraction error."""
        self._audio_spinner.stop()
        self._transcription_timer_label.setText("Extraction échouée")
        QMessageBox.warning(self, "Extraction audio", error_message)

    def _on_extraction_thread_finished(self) -> None:
        """Release the automatic extraction thread."""
        self._reset_recording_button()
        self._new_conversation_button.setEnabled(True)

    def _cleanup_recorded_audio(self) -> None:
        """Delete temporary audio data as soon as it is no longer needed."""
        if self._recorded_audio_path and self._recorded_audio_path.exists():
            try:
                self._recorded_audio_path.unlink()
            except OSError:
                pass
        self._recorded_audio_path = None

    def _on_send_clicked(self) -> None:
        """Handle send button click."""
        user_message = self._input_field.toPlainText().strip()
        if not user_message:
            return

        conversation_id = self._conversation_session_id

        # Display user message and clear input
        self._chat_widget.add_message(user_message, Role.USER)
        self._input_field.clear()
        self._send_button.setEnabled(False)
        
        # Show loading spinner and prepare streaming bubble
        self._spinner.start()
        self._chat_widget.start_streaming_message()

        # Start background API request with streaming
        self._chat_controller.send_message(conversation_id, user_message)

    def _on_chunk_received(self, conversation_id: int, chunk: str) -> None:
        """Handle incoming text chunk (typewriter effect)."""
        if conversation_id != self._conversation_session_id:
            return
        # Hide spinner after first chunk arrives
        self._spinner.stop()
        # Streaming chunk for typewriter effect
        self._chat_widget.append_streaming_chunk(chunk)

    def _on_stream_finished(self, conversation_id: int) -> None:
        """Handle end of streaming."""
        if conversation_id != self._conversation_session_id:
            return
        self._chat_widget.finish_streaming()
        self._send_button.setEnabled(True)

    def _on_error(self, conversation_id: int, error_message: str) -> None:
        """Handle API error."""
        if conversation_id != self._conversation_session_id:
            return
        self._spinner.stop()
        self._chat_widget.finish_streaming()
        QMessageBox.warning(self, "API Error", error_message)
        self._send_button.setEnabled(True)

    def _on_thread_finished(self, conversation_id: int) -> None:
        """Clean up thread connections after completion."""
        if conversation_id != self._conversation_session_id:
            return

    def _start_new_conversation(self) -> None:
        """Reset the UI and AI history for a fresh conversation."""
        self._conversation_session_id += 1
        self._chat_controller.cancel(wait=False)
        self._transcription_controller.cancel()
        self._spinner.stop()
        self._send_button.setEnabled(True)
        self._input_field.clear()
        self._chat_widget.clear_conversation()
        self._chat_controller.clear_history()
        self._chat_controller.clear_audio_transcript_context()
        self._input_widget.hide_audio_context_badge()
        self._audio_spinner.stop()
        self._transcription_timer_label.hide()
        self._cleanup_recorded_audio()

    def closeEvent(self, event) -> None:
        """Stop recording and remove temporary audio before closing."""
        if self._audio_manager.is_recording():
            self._audio_manager.stop()
        self._chat_controller.cancel()
        self._transcription_controller.cancel()
        self._audio_manager.cleanup()
        self._audio_spinner.stop()
        self._cleanup_recorded_audio()
        super().closeEvent(event)

    def resizeEvent(self, event) -> None:
        """Keep the main view proportions comfortable as the window changes."""
        super().resizeEvent(event)
        self._apply_responsive_layout(event.size().width())

    def _apply_responsive_layout(self, width: int) -> None:
        """Update the main window spacing and control sizes for the current width."""
        metrics = main_window_metrics(width)

        if hasattr(self, "_header"):
            self._header.setMinimumHeight(metrics.header_height)
            header_layout = self._header.layout()
            if header_layout is not None:
                header_layout.setContentsMargins(*metrics.header_margins)

        if hasattr(self, "_logo_label") and LOGO_PATH.exists():
            pixmap = QPixmap(str(LOGO_PATH))
            self._logo_label.setPixmap(pixmap.scaledToHeight(metrics.logo_height, Qt.SmoothTransformation))

        if hasattr(self, "_input_container"):
            input_layout = self._input_container.layout()
            if input_layout is not None:
                input_layout.setContentsMargins(*metrics.input_margins)
                input_layout.setSpacing(metrics.input_spacing)

        if hasattr(self, "_disclaimer"):
            self._disclaimer.setWordWrap(True)

        if hasattr(self, "_input_field"):
            self._input_field.setMaximumHeight(metrics.input_max_height)

        if hasattr(self, "_send_button"):
            self._send_button.setFixedSize(metrics.send_button_size, metrics.send_button_size)

        if hasattr(self, "_spinner"):
            self._spinner.set_size(metrics.spinner_size)
