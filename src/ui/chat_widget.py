from PySide6.QtWidgets import (
    QScrollArea, QVBoxLayout, QHBoxLayout, QWidget, QFrame, QPushButton, QFileDialog, QDialog
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QTextDocument
from PySide6.QtPrintSupport import QPrinter
import markdown
from models.message import Role
from ui.styles import CHAT_WIDGET_STYLE, USER_BUBBLE_STYLE, ASSISTANT_BUBBLE_STYLE, EDIT_BUTTON_STYLE
from ui.edit_message_dialog import EditMessageDialog
from ui.responsive import apply_chat_responsive_layout, insert_chat_bubble, register_chat_bubble
from ui.markdown import Markdown


class ChatWidget(QScrollArea):
    """Scrollable chat widget displaying conversation as message bubbles."""

    def __init__(self) -> None:
        super().__init__()
        self._bubbles: list[tuple[QFrame, Role]] = []
        self._setup_scroll_area()
        self._setup_message_container()
        self._streaming_label: Markdown | None = None
        self._edited_messages: dict[int, str] = {}
        self._message_counter = 0
        self._last_assistant_message_id: int | None = None

    # ==================== SETUP ====================

    def _setup_scroll_area(self) -> None:
        """Configure scroll area properties."""
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet(CHAT_WIDGET_STYLE)

    def _setup_message_container(self) -> None:
        """Create container for message bubbles."""
        self._container = QWidget()
        self._layout = QVBoxLayout(self._container)
        self._layout.addStretch()
        self._layout.setSpacing(4)
        self.setWidget(self._container)
        apply_chat_responsive_layout(self, self._layout, self._bubbles)

    def clear_conversation(self) -> None:
        """Remove all messages and reset chat-local state."""
        for bubble, _role in self._bubbles:
            self._layout.removeWidget(bubble)
            bubble.setParent(None)
            bubble.deleteLater()

        self._bubbles.clear()
        self._edited_messages.clear()
        self._message_counter = 0
        self._last_assistant_message_id = None
        self._streaming_label = None
        self._streaming_bubble = None
        self._streaming_text = ""

        apply_chat_responsive_layout(self, self._layout, self._bubbles)

    # ==================== PUBLIC METHODS ====================

    def add_message(self, text: str, role: Role) -> None:
        """Add a complete message bubble to the chat."""
        bubble = self._create_bubble(text, role)
        self._register_bubble(bubble, role)
        self._insert_bubble(bubble, role)
        QTimer.singleShot(10, self._scroll_to_bottom)

    def start_streaming_message(self) -> None:
        """Create empty assistant bubble for streaming content."""
        bubble = QFrame()
        layout = QVBoxLayout(bubble)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self._streaming_label = Markdown("")
        layout.addWidget(self._streaming_label)
        
        bubble.setStyleSheet(ASSISTANT_BUBBLE_STYLE)
        self._streaming_label.setAlignment(Qt.AlignLeft)
        
        self._streaming_bubble = bubble
        self._streaming_text = ""
        self._message_counter += 1
        self._last_assistant_message_id = self._message_counter
        self._register_bubble(bubble, Role.ASSISTANT)
        self._insert_bubble(bubble, Role.ASSISTANT)

    def append_streaming_chunk(self, chunk: str) -> None:
        """Append text chunk to streaming bubble (typewriter effect)."""
        if self._streaming_label:
            self._streaming_text += chunk
            self._streaming_label.set_markdown(self._streaming_text)
            QTimer.singleShot(10, self._scroll_to_bottom)

    def finish_streaming(self) -> None:
        """Mark streaming as complete and add edit button."""
        if self._streaming_bubble and self._last_assistant_message_id:
            self._add_edit_button(self._streaming_bubble, self._last_assistant_message_id, self._streaming_text)
        
        self._streaming_label = None
        self._streaming_bubble = None
        self._streaming_text = ""

    # ==================== EDIT ====================

    def _add_edit_button(self, bubble: QFrame, message_id: int, original_text: str) -> None:
        """Add edit button under an AI message bubble."""
        layout = bubble.layout()
        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 8, 0, 0)
        
        edit_button = QPushButton("✏ Éditer")
        edit_button.setStyleSheet(EDIT_BUTTON_STYLE)
        edit_button.setCursor(Qt.PointingHandCursor)
        edit_button.setMaximumWidth(100)

        pdf_button = QPushButton("PDF")
        pdf_button.setStyleSheet(EDIT_BUTTON_STYLE)
        pdf_button.setCursor(Qt.PointingHandCursor)
        pdf_button.setMaximumWidth(60)
        
        def on_edit_clicked() -> None:
            self._open_edit_dialog(message_id, original_text, bubble)

        def on_pdf_clicked() -> None:
            self._export_message_as_pdf(message_id, original_text)
        
        edit_button.clicked.connect(on_edit_clicked)
        pdf_button.clicked.connect(on_pdf_clicked)
        button_row.addWidget(edit_button)
        button_row.addWidget(pdf_button)
        button_row.addStretch()
        layout.addLayout(button_row)

    def _open_edit_dialog(self, message_id: int, original_text: str, bubble: QFrame) -> None:
        """Open dialog to edit AI message."""
        current_text = self._edited_messages.get(message_id, original_text)
        dialog = EditMessageDialog(self, current_text)

        if dialog.exec() == QDialog.Accepted:
            edited_text = dialog.edited_text()
            self._edited_messages[message_id] = edited_text
            self._update_message_in_bubble(bubble, edited_text)

    def _export_message_as_pdf(self, message_id: int, original_text: str) -> None:
        """Export the latest version of an AI message to a PDF file."""
        text = self._edited_messages.get(message_id, original_text)
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter le message en PDF",
            "fiche_medicale.pdf",
            "PDF Files (*.pdf)"
        )
        if not file_path:
            return

        if not file_path.lower().endswith(".pdf"):
            file_path += ".pdf"

        html = markdown.markdown(text, extensions=[
            'fenced_code',
            'tables',
            'nl2br',
            'sane_lists',
        ])
        document = QTextDocument()
        document.setHtml(html)

        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(file_path)
        document.print_(printer)

    def _update_message_in_bubble(self, bubble: QFrame, new_text: str) -> None:
        """Update the text content of a message bubble."""
        layout = bubble.layout()
        if layout and layout.count() > 0:
            widget = layout.itemAt(0).widget()
            if isinstance(widget, Markdown):
                widget.set_markdown(new_text)

    # ==================== BUBBLE ====================

    def _create_bubble(self, text: str, role: Role) -> QFrame:
        """Create styled message bubble with markdown support."""
        bubble = QFrame()
        layout = QVBoxLayout(bubble)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label = Markdown(text)
        layout.addWidget(label)

        self._apply_bubble_style(bubble, label, role)
        return bubble

    def _apply_bubble_style(self, bubble: QFrame, label: Markdown, role: Role) -> None:
        """Apply style based on message role."""
        if role == Role.USER:
            bubble.setStyleSheet(USER_BUBBLE_STYLE)
            label.setAlignment(Qt.AlignRight)
        else:
            bubble.setStyleSheet(ASSISTANT_BUBBLE_STYLE)
            label.setAlignment(Qt.AlignLeft)

    def _register_bubble(self, bubble: QFrame, role: Role) -> None:
        """Track bubbles so their margins can adapt to the current width."""
        register_chat_bubble(self, self._layout, self._bubbles, bubble, role)

    # ==================== LAYOUT MANAGEMENT ====================

    def _insert_bubble(self, bubble: QFrame, role: Role) -> None:
        """Insert bubble above the stretch spacer."""
        insert_chat_bubble(self._layout, bubble, role)

    def _scroll_to_bottom(self) -> None:
        """Scroll to show latest message."""
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def resizeEvent(self, event) -> None:
        """Adjust bubble margins when the viewport width changes."""
        super().resizeEvent(event)
        apply_chat_responsive_layout(self, self._layout, self._bubbles)
