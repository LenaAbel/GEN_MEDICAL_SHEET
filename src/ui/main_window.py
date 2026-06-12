import json
import tempfile
import uuid
from pathlib import Path

from PySide6.QtCore import QElapsedTimer, QTimer, Qt, QUrl
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtMultimedia import (
    QAudioInput,
    QMediaCaptureSession,
    QMediaDevices,
    QMediaFormat,
    QMediaRecorder,
)
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QMessageBox, QLabel
)

from ui.chat_widget import ChatWidget
from ui.spinner import LoadingSpinner
from ui.styles import (
    MAIN_WINDOW_STYLE, INPUT_FIELD_STYLE, SEND_BUTTON_STYLE,
    HEADER_STYLE, LOGO_STYLE, DISCLAIMER_STYLE, NEW_CONVERSATION_BUTTON_STYLE,
    RECORDING_BUTTON_STYLE, RECORDING_TIMER_STYLE, TRANSCRIPTION_BUTTON_STYLE,
    TRANSCRIPTION_TIMER_STYLE
)
from services.mistral_service import MistralService
from services.mistral_request_thread import MistralRequestThread
from services.transcript_extraction_request_thread import (
    TranscriptExtractionRequestThread,
)
from services.transcript_extraction_service import TranscriptExtractionService
from services.transcription_request_thread import TranscriptionRequestThread
from services.transcription_service import TranscriptionService
from models.message import Role
from ui.responsive import main_window_metrics


# ==== CONSTANTS ====
WINDOW_TITLE = "Générateur de Fiche Médicale - CHU Besançon"
WINDOW_MIN_SIZE = (760, 560)
INPUT_MAX_HEIGHT = 100
LOGO_HEIGHT = 40
SEND_BUTTON_SIZE = 36

ASSETS_DIR = Path(__file__).parent / "img"
LOGO_PATH = ASSETS_DIR / "chu_logo.svg"
SEND_ICON_PATH = ASSETS_DIR / "send_icon.svg"


class MainWindow(QMainWindow):
    """Main chat window for Medical Sheet Generator."""

    def __init__(self) -> None:
        super().__init__()
        self._configure_window()
        self._mistral_service = MistralService()
        self._request_thread: MistralRequestThread | None = None
        self._transcription_thread: TranscriptionRequestThread | None = None
        self._extraction_thread: TranscriptExtractionRequestThread | None = None
        self._recorded_audio_path: Path | None = None
        self._recording_stop_requested = False
        self._capture_session: QMediaCaptureSession | None = None
        self._audio_input: QAudioInput | None = None
        self._audio_recorder: QMediaRecorder | None = None
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

    def _setup_audio_recorder(self) -> None:
        """Configure an isolated microphone recorder for temporary WAV files."""
        self._capture_session = QMediaCaptureSession(self)
        self._audio_input = QAudioInput(self)
        self._audio_recorder = QMediaRecorder(self)

        media_format = QMediaFormat()
        media_format.setFileFormat(QMediaFormat.FileFormat.Wave)
        media_format.setAudioCodec(QMediaFormat.AudioCodec.Wave)
        self._audio_recorder.setMediaFormat(media_format)

        self._capture_session.setAudioInput(self._audio_input)
        self._capture_session.setRecorder(self._audio_recorder)
        self._audio_recorder.recorderStateChanged.connect(
            self._on_recorder_state_changed
        )
        self._audio_recorder.actualLocationChanged.connect(
            self._on_recording_location_changed
        )
        self._audio_recorder.errorOccurred.connect(self._on_recorder_error)

    # ==================== UI SETUP ====================

    def _setup_ui(self) -> None:
        """Build main UI layout."""
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # UI sections
        main_layout.addWidget(self._create_header())
        main_layout.addWidget(self._create_chat_area(), stretch=1)
        main_layout.addWidget(self._create_input_area())
        self._apply_responsive_layout(self.width())

    # ==================== HEADER SECTION ====================

    def _create_header(self) -> QWidget:
        """Create header with CHU logo."""
        self._header = QWidget()
        self._header.setStyleSheet(HEADER_STYLE)
        
        layout = QHBoxLayout(self._header)
        layout.setContentsMargins(15, 5, 15, 5)
        
        # Logo on left
        self._logo_label = QLabel()
        self._logo_label.setStyleSheet(LOGO_STYLE)
        if LOGO_PATH.exists():
            pixmap = QPixmap(str(LOGO_PATH))
            scaled = pixmap.scaledToHeight(LOGO_HEIGHT, Qt.SmoothTransformation)
            self._logo_label.setPixmap(scaled)
        else:
            self._logo_label.setText("CHU")
        
        layout.addWidget(self._logo_label)
        layout.addStretch()

        self._audio_spinner = LoadingSpinner(self._header, size=20)
        layout.addWidget(self._audio_spinner)

        self._transcription_timer_label = QLabel("Enregistrement 00:00")
        self._transcription_timer_label.setStyleSheet(TRANSCRIPTION_TIMER_STYLE)
        self._transcription_timer_label.hide()
        layout.addWidget(self._transcription_timer_label)

        self._transcription_button = QPushButton("Enregistrer")
        self._transcription_button.setToolTip("Démarrer un enregistrement audio")
        self._transcription_button.setCursor(Qt.PointingHandCursor)
        self._transcription_button.setStyleSheet(TRANSCRIPTION_BUTTON_STYLE)
        self._transcription_button.clicked.connect(self._on_transcription_clicked)
        layout.addWidget(self._transcription_button)

        self._new_conversation_button = QPushButton("+")
        self._new_conversation_button.setToolTip("Nouvelle conversation")
        self._new_conversation_button.setCursor(Qt.PointingHandCursor)
        self._new_conversation_button.setStyleSheet(NEW_CONVERSATION_BUTTON_STYLE)
        self._new_conversation_button.clicked.connect(self._start_new_conversation)
        layout.addWidget(self._new_conversation_button)
        
        return self._header

    # ==================== CHAT SECTION ====================

    def _create_chat_area(self) -> QWidget:
        """Create scrollable chat display area."""
        self._chat_widget = ChatWidget()
        return self._chat_widget

    # ==================== INPUT SECTION ====================

    def _create_input_area(self) -> QWidget:
        """Create message input area with spinner, text field and send button."""
        self._input_container = QWidget()
        
        main_layout = QVBoxLayout(self._input_container)
        main_layout.setContentsMargins(60, 15, 60, 20)
        main_layout.setSpacing(8)
        
        # Disclaimer text
        self._disclaimer = QLabel("⚠ L'IA peut halluciner. Vérifiez toujours les informations importantes.")
        self._disclaimer.setWordWrap(True)
        self._disclaimer.setStyleSheet(DISCLAIMER_STYLE)
        main_layout.addWidget(self._disclaimer)
        
        # Input controls layout
        layout = QHBoxLayout()
        layout.setSpacing(12)
        
        # Loading spinner
        self._spinner = LoadingSpinner(self._input_container)
        layout.addWidget(self._spinner)
        
        # Input text area for user messages
        self._input_field = QTextEdit()
        self._input_field.setMaximumHeight(INPUT_MAX_HEIGHT)
        self._input_field.setPlaceholderText("Envoyer votre message...")
        self._input_field.setStyleSheet(INPUT_FIELD_STYLE)
        
        # Send button with icon
        self._send_button = QPushButton()
        self._send_button.setStyleSheet(SEND_BUTTON_STYLE)
        self._send_button.setCursor(Qt.PointingHandCursor)
        self._send_button.setFixedSize(SEND_BUTTON_SIZE, SEND_BUTTON_SIZE)

        if SEND_ICON_PATH.exists():
            self._send_button.setIcon(QIcon(str(SEND_ICON_PATH)))
        else:
            self._send_button.setText("→")
        self._send_button.clicked.connect(self._on_send_clicked)
        
        layout.addWidget(self._input_field)
        layout.addWidget(self._send_button)
        
        main_layout.addLayout(layout)
        self._apply_responsive_layout(self.width())
        
        return self._input_container

    # ==================== EVENT HANDLERS ====================

    def _on_transcription_clicked(self) -> None:
        """Start or stop microphone recording."""
        if (
            self._audio_recorder is not None
            and self._audio_recorder.recorderState()
            == QMediaRecorder.RecorderState.RecordingState
        ):
            self._stop_audio_recording()
            return

        if not QMediaDevices.audioInputs():
            QMessageBox.warning(
                self,
                "Enregistrement audio",
                "Aucun microphone n'est disponible sur cet appareil.",
            )
            return

        if self._audio_recorder is None:
            self._setup_audio_recorder()

        self._cleanup_recorded_audio()
        self._new_conversation_button.setEnabled(False)
        self._recorded_audio_path = (
            Path(tempfile.gettempdir()) / f"gen_medical_sheet_{uuid.uuid4().hex}.wav"
        )
        self._recording_stop_requested = False
        self._audio_recorder.setOutputLocation(
            QUrl.fromLocalFile(str(self._recorded_audio_path))
        )

        self._transcription_button.setText("Arrêter")
        self._transcription_button.setToolTip("Arrêter l'enregistrement audio")
        self._transcription_button.setStyleSheet(RECORDING_BUTTON_STYLE)
        self._transcription_timer_label.setText("Enregistrement 00:00")
        self._transcription_timer_label.setStyleSheet(RECORDING_TIMER_STYLE)
        self._transcription_timer_label.show()
        self._transcription_elapsed.start()
        self._transcription_timer.start()
        self._audio_recorder.record()

    def _stop_audio_recording(self) -> None:
        """Stop recording and wait for Qt to finish writing the audio file."""
        if self._audio_recorder is None:
            return
        self._recording_stop_requested = True
        self._audio_recorder.stop()
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
        try:
            transcription_service = TranscriptionService()
        except Exception as exc:
            self._on_transcription_error(str(exc))
            return

        self._set_audio_processing_status("Transcription en cours...")

        self._transcription_thread = TranscriptionRequestThread(
            transcription_service,
            self._recorded_audio_path,
        )
        self._transcription_thread.transcription_finished.connect(
            self._on_transcription_finished
        )
        self._transcription_thread.error_occurred.connect(self._on_transcription_error)
        self._transcription_thread.finished.connect(self._on_transcription_thread_finished)
        self._transcription_thread.start()

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
        self._new_conversation_button.setEnabled(self._transcription_thread is None)
        QMessageBox.warning(self, "Transcription audio", error_message)

    def _on_transcription_thread_finished(self) -> None:
        """Release the completed audio request thread."""
        self._cleanup_recorded_audio()
        self._transcription_thread = None
        if self._extraction_thread is None:
            self._reset_recording_button()
            self._new_conversation_button.setEnabled(True)

    def _stop_transcription_timer(self) -> None:
        """Stop timer updates while keeping the final duration visible."""
        if self._transcription_timer.isActive():
            self._update_transcription_timer()
            self._transcription_timer.stop()

    def _reset_recording_button(self) -> None:
        """Restore the recording button after processing completes."""
        self._transcription_button.setText("Enregistrer")
        self._transcription_button.setToolTip("Démarrer un enregistrement audio")
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
        try:
            extraction_service = TranscriptExtractionService()
        except Exception as exc:
            self._on_extraction_error(str(exc))
            self._reset_recording_button()
            self._new_conversation_button.setEnabled(True)
            return

        self._new_conversation_button.setEnabled(False)
        self._extraction_thread = TranscriptExtractionRequestThread(
            extraction_service,
            transcript,
        )
        self._extraction_thread.extraction_finished.connect(
            self._on_extraction_finished
        )
        self._extraction_thread.error_occurred.connect(self._on_extraction_error)
        self._extraction_thread.finished.connect(self._on_extraction_thread_finished)
        self._extraction_thread.start()

    def _on_extraction_finished(self, extracted_data: object) -> None:
        """Print structured JSON for testing without exposing it in the chatbot."""
        formatted_json = json.dumps(extracted_data, ensure_ascii=False, indent=2)
        print(f"[Extraction audio JSON]\n{formatted_json}", flush=True)
        self._audio_spinner.stop()
        self._transcription_timer_label.setText("Extraction terminée")

    def _on_extraction_error(self, error_message: str) -> None:
        """Display a clear structured extraction error."""
        self._audio_spinner.stop()
        self._transcription_timer_label.setText("Extraction échouée")
        QMessageBox.warning(self, "Extraction audio", error_message)

    def _on_extraction_thread_finished(self) -> None:
        """Release the automatic extraction thread."""
        self._extraction_thread = None
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
        self._request_thread = MistralRequestThread(self._mistral_service, user_message)
        self._request_thread.chunk_received.connect(
            lambda chunk, cid=conversation_id: self._on_chunk_received(cid, chunk)
        )
        self._request_thread.stream_finished.connect(
            lambda cid=conversation_id: self._on_stream_finished(cid)
        )
        self._request_thread.error_occurred.connect(
            lambda error_message, cid=conversation_id: self._on_error(cid, error_message)
        )
        self._request_thread.finished.connect(
            lambda cid=conversation_id: self._on_thread_finished(cid)
        )
        self._request_thread.start()

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
        self._request_thread = None

    def _start_new_conversation(self) -> None:
        """Reset the UI and AI history for a fresh conversation."""
        self._conversation_session_id += 1
        self._request_thread = None
        self._spinner.stop()
        self._send_button.setEnabled(True)
        self._input_field.clear()
        self._chat_widget.clear_conversation()
        self._mistral_service.clear_history()
        self._audio_spinner.stop()
        self._transcription_timer_label.hide()
        self._cleanup_recorded_audio()

    def closeEvent(self, event) -> None:
        """Stop recording and remove temporary audio before closing."""
        if (
            self._audio_recorder is not None
            and self._audio_recorder.recorderState()
            == QMediaRecorder.RecorderState.RecordingState
        ):
            self._audio_recorder.stop()
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
