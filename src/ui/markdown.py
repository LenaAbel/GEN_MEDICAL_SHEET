"""
Custom QLabel that renders markdown content as HTML.
Uses the 'markdown' library for robust conversion.
"""
import markdown
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt


MARKDOWN_EXTENSIONS = [
    'fenced_code',    # For code blocks with triple backticks
    'tables',         # For markdown tables
    'nl2br',          # Convert newlines to <br> tags
    'sane_lists',     # Better handling of lists
]


class Markdown(QLabel):
    """QLabel that converts markdown text to HTML for display."""

    def __init__(self, text: str = "") -> None:
        super().__init__()
        self._configure_label()
        if text:
            self.set_markdown(text)

    # ==================== SETUP ====================

    def _configure_label(self) -> None:
        """Configure label properties for rich text display."""
        self.setWordWrap(True)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
        self.setOpenExternalLinks(True)
        self.setTextFormat(Qt.RichText)

    # ==================== PUBLIC METHODS ====================

    def set_markdown(self, text: str) -> None:
        """Convert markdown to HTML and display."""
        html = markdown.markdown(text, extensions=MARKDOWN_EXTENSIONS)
        styled_html = self._wrap_with_styles(html)
        self.setText(styled_html)

    # ==================== STYLING ====================

    def _wrap_with_styles(self, html: str) -> str:
        """Add inline styles for code blocks and other elements."""
        # Style code blocks
        html = html.replace(
            '<code>',
            '<code style="background-color: #f4f4f4; padding: 2px 6px; border-radius: 4px; font-family: monospace;">'
        )
        html = html.replace(
            '<pre>',
            '<pre style="background-color: #f4f4f4; padding: 10px; border-radius: 6px; font-family: monospace; overflow-x: auto;">'
        )
        return html
