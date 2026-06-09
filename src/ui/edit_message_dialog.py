"""Reusable dialog for editing assistant messages."""
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
)

from ui.responsive import dialog_size_for_parent
from ui.styles import EDIT_BUTTON_STYLE, EDIT_DIALOG_STYLE
from ui.markdown_editor import MarkdownEditorWidget


class EditMessageDialog(QDialog):
    """Responsive dialog that lets the user edit a generated message."""

    def __init__(self, parent=None, initial_text: str = "") -> None:
        super().__init__(parent)
        self._initial_text = initial_text
        self._setup_window()
        self._setup_ui()
        self._apply_responsive_layout()

    # ==================== SETUP ====================

    def _setup_window(self) -> None:
        """Configure window flags and the initial size."""
        self.setWindowTitle("Éditer le message")
        self.setModal(True)
        self.setSizeGripEnabled(True)
        self.setStyleSheet(EDIT_DIALOG_STYLE)

        parent = self.parentWidget()
        parent_width = parent.width() if parent else None
        parent_height = parent.height() if parent else None
        dialog_width, dialog_height = dialog_size_for_parent(parent_width, parent_height)
        self.resize(dialog_width, dialog_height)
        self.setMinimumSize(480, 320)

    def _setup_ui(self) -> None:
        """Build dialog contents."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        self._markdown_editor = MarkdownEditorWidget(self._initial_text, self)
        layout.addWidget(self._markdown_editor)

        self._button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self._button_box.button(QDialogButtonBox.Save).setText("Enregistrer")
        self._button_box.button(QDialogButtonBox.Cancel).setText("Annuler")
        self._button_box.button(QDialogButtonBox.Save).setStyleSheet(EDIT_BUTTON_STYLE)
        self._button_box.button(QDialogButtonBox.Cancel).setStyleSheet(EDIT_BUTTON_STYLE)
        self._button_box.accepted.connect(self.accept)
        self._button_box.rejected.connect(self.reject)
        layout.addWidget(self._button_box)

    # ==================== RESPONSIVENESS ====================

    def _apply_responsive_layout(self) -> None:
        width = self.width()
        if width < 620:
            margins = (14, 14, 14, 14)
            spacing = 10
        elif width < 820:
            margins = (16, 16, 16, 16)
            spacing = 12
        else:
            margins = (20, 20, 20, 20)
            spacing = 14

        layout = self.layout()
        if layout is not None:
            layout.setContentsMargins(*margins)
            layout.setSpacing(spacing)

    def resizeEvent(self, event) -> None:
        """Update spacing when the dialog is resized."""
        super().resizeEvent(event)
        self._apply_responsive_layout()

    # ==================== PUBLIC API ====================

    def edited_text(self) -> str:
        """Return the current text in the editor."""
        return self._markdown_editor.text()
