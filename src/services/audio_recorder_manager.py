from pathlib import Path

from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtMultimedia import (
    QAudioInput,
    QMediaCaptureSession,
    QMediaFormat,
    QMediaRecorder,
)


class AudioRecorderManager(QObject):
    """Manage the Qt multimedia objects used for microphone recording."""

    recorderStateChanged = Signal(QMediaRecorder.RecorderState)
    actualLocationChanged = Signal(QUrl)
    errorOccurred = Signal(object, str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._capture_session: QMediaCaptureSession | None = None
        self._audio_input: QAudioInput | None = None
        self._audio_recorder: QMediaRecorder | None = None

    def setup(self) -> None:
        """Configure an isolated microphone recorder for temporary WAV files."""
        if self._audio_recorder is not None:
            return

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
            self.recorderStateChanged.emit
        )
        self._audio_recorder.actualLocationChanged.connect(
            self.actualLocationChanged.emit
        )
        self._audio_recorder.errorOccurred.connect(self.errorOccurred.emit)

    def start(self, output_path: Path) -> None:
        """Start recording audio to the requested output path."""
        self.setup()
        self._audio_recorder.setOutputLocation(
            QUrl.fromLocalFile(str(output_path))
        )
        self._audio_recorder.record()

    def stop(self) -> None:
        """Stop the active recording."""
        if self._audio_recorder is not None:
            self._audio_recorder.stop()

    def is_recording(self) -> bool:
        """Return whether the recorder is currently recording."""
        return (
            self._audio_recorder is not None
            and self._audio_recorder.recorderState()
            == QMediaRecorder.RecorderState.RecordingState
        )

    def cleanup(self) -> None:
        """Release the recorder objects owned by this manager."""
        self.stop()
        if self._capture_session is not None:
            self._capture_session.setAudioInput(None)
            self._capture_session.setRecorder(None)

        for recorder_object in (
            self._audio_recorder,
            self._audio_input,
            self._capture_session,
        ):
            if recorder_object is not None:
                recorder_object.deleteLater()

        self._audio_recorder = None
        self._audio_input = None
        self._capture_session = None
