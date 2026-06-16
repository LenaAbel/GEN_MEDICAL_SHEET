from PySide6.QtWidgets import QVBoxLayout, QWidget

from domain.models.message import Role
from ui.widgets.chat_widget import ChatWidget


class ChatArea(QWidget):
    """Visual container for the conversation chat widget."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._chat_widget = ChatWidget()
        self.chat_widget = self._chat_widget
        layout.addWidget(self._chat_widget)

    def add_message(self, text: str, role: Role) -> None:
        """Add a complete message to the conversation."""
        self._chat_widget.add_message(text, role)

    def start_streaming_message(self) -> None:
        """Start an assistant streaming message."""
        self._chat_widget.start_streaming_message()

    def append_streaming_chunk(self, chunk: str) -> None:
        """Append a chunk to the active streaming message."""
        self._chat_widget.append_streaming_chunk(chunk)

    def finish_streaming(self) -> None:
        """Finish the active streaming message."""
        self._chat_widget.finish_streaming()

    def clear_conversation(self) -> None:
        """Clear all messages from the conversation."""
        self._chat_widget.clear_conversation()
