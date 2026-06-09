"""Markdown editor widget with live preview."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSplitter, QPlainTextEdit, QTextBrowser
from PySide6.QtCore import Qt

from ui.markdown import markdown_to_html


class MarkdownEditorWidget(QWidget):
    """Simple markdown editor with a live rendered preview."""

    def __init__(self, initial_text: str = "", parent=None) -> None:
        super().__init__(parent)
        self._setup_ui(initial_text)

    def _setup_ui(self, initial_text: str) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        splitter = QSplitter(Qt.Horizontal, self)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(14)

        self._editor = QPlainTextEdit()
        self._editor.setPlainText(initial_text)

        self._preview = QTextBrowser()
        self._preview.setOpenExternalLinks(True)
        self._preview.setPlainText("")
        self._preview.setHtml(markdown_to_html(initial_text))

        splitter.addWidget(self._editor)
        splitter.addWidget(self._preview)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([1, 1])

        layout.addWidget(splitter)

        self._editor.textChanged.connect(self._update_preview)

    def _update_preview(self) -> None:
        """Refresh the rendered markdown preview."""
        self._preview.setHtml(markdown_to_html(self._editor.toPlainText()))

    def text(self) -> str:
        """Return the current markdown source."""
        return self._editor.toPlainText()

    def set_text(self, text: str) -> None:
        """Replace the editor content and refresh the preview."""
        self._editor.blockSignals(True)
        self._editor.setPlainText(text)
        self._editor.blockSignals(False)
        self._update_preview()
