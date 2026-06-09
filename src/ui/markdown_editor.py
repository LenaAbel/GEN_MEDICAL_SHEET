"""Markdown editor widget with live preview and formatting helpers."""
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QPlainTextEdit,
    QTextBrowser,
    QToolButton,
    QSizePolicy,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor

from ui.markdown import markdown_to_html


class MarkdownEditorWidget(QWidget):
    """Simple markdown editor with a live rendered preview."""

    def __init__(self, initial_text: str = "", parent=None) -> None:
        super().__init__(parent)
        self._setup_ui(initial_text)

    def _setup_ui(self, initial_text: str) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self._toolbar = QWidget(self)
        self._toolbar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._toolbar.setMaximumHeight(44)
        toolbar_layout = QHBoxLayout(self._toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(6)

        self._add_toolbar_button(toolbar_layout, "Gras", lambda: self._wrap_selection("**", "**", "texte en gras"))
        self._add_toolbar_button(toolbar_layout, "Italique", lambda: self._wrap_selection("*", "*", "texte en italique"))
        self._add_toolbar_button(toolbar_layout, "Titre", lambda: self._prefix_block_lines("# ", "Titre"))
        self._add_toolbar_button(toolbar_layout, "Citation", lambda: self._prefix_block_lines("> ", "Citation"))
        self._add_toolbar_button(toolbar_layout, "Liste", lambda: self._prefix_block_lines("- ", "Élément"))
        self._add_toolbar_button(toolbar_layout, "Code", lambda: self._wrap_selection("`", "`", "code"))
        self._add_toolbar_button(toolbar_layout, "Lien", self._insert_link_placeholder)
        toolbar_layout.addStretch()

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
        splitter.setSizes([520, 620])

        layout.addWidget(self._toolbar, 0)
        layout.addWidget(splitter, 1)

        self._editor.textChanged.connect(self._update_preview)

    def _add_toolbar_button(self, layout: QHBoxLayout, label: str, callback) -> None:
        """Add a formatting button to the toolbar."""
        button = QToolButton()
        button.setText(label)
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(callback)
        layout.addWidget(button)

    def _update_preview(self) -> None:
        """Refresh the rendered markdown preview."""
        scrollbar = self._preview.verticalScrollBar()
        old_max = scrollbar.maximum()
        old_value = scrollbar.value()
        scroll_ratio = (old_value / old_max) if old_max > 0 else 0.0

        self._preview.setHtml(markdown_to_html(self._editor.toPlainText()))

        new_max = scrollbar.maximum()
        scrollbar.setValue(int(scroll_ratio * new_max))

    def _wrap_selection(self, prefix: str, suffix: str, placeholder: str) -> None:
        """Wrap the selected text or insert a formatted placeholder."""
        cursor = self._editor.textCursor()
        if cursor.hasSelection():
            selected = cursor.selectedText().replace("\u2029", "\n")
            replacement = f"{prefix}{selected}{suffix}"
        else:
            replacement = f"{prefix}{placeholder}{suffix}"
        cursor.insertText(replacement)
        self._editor.setTextCursor(cursor)

    def _prefix_block_lines(self, prefix: str, placeholder: str) -> None:
        """Prefix each selected line, or insert a single formatted line."""
        cursor = self._editor.textCursor()
        if cursor.hasSelection():
            selected = cursor.selectedText().replace("\u2029", "\n")
            lines = selected.split("\n")
            replacement = "\n".join(f"{prefix}{line}" if line.strip() else prefix.rstrip() for line in lines)
        else:
            replacement = f"{prefix}{placeholder}"
        cursor.insertText(replacement)
        self._editor.setTextCursor(cursor)

    def _insert_link_placeholder(self) -> None:
        """Insert a Markdown link placeholder at the cursor position."""
        cursor = self._editor.textCursor()
        replacement = "[texte du lien](https://example.com)"
        cursor.insertText(replacement)
        self._editor.setTextCursor(cursor)

    def text(self) -> str:
        """Return the current markdown source."""
        return self._editor.toPlainText()

    def set_text(self, text: str) -> None:
        """Replace the editor content and refresh the preview."""
        self._editor.blockSignals(True)
        self._editor.setPlainText(text)
        self._editor.blockSignals(False)
        self._update_preview()
