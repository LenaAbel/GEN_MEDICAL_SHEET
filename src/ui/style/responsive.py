"""Responsive layout helpers shared by the UI widgets."""
from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QScrollArea, QVBoxLayout

from domain.models.message import Role


@dataclass(frozen=True)
class MainWindowMetrics:
    """Layout values tuned for a given window width."""

    header_height: int
    header_margins: tuple[int, int, int, int]
    input_margins: tuple[int, int, int, int]
    input_spacing: int
    logo_height: int
    input_max_height: int
    send_button_size: int
    spinner_size: int


@dataclass(frozen=True)
class ChatMetrics:
    """Layout values tuned for the chat viewport width."""

    container_margins: tuple[int, int, int, int]
    bubble_side_margin: int
    bubble_inner_margin: int


def main_window_metrics(width: int) -> MainWindowMetrics:
    """Return spacing and sizing values that scale with the window width."""
    if width < 760:
        return MainWindowMetrics(
            header_height=56,
            header_margins=(12, 6, 12, 6),
            input_margins=(16, 12, 16, 14),
            input_spacing=8,
            logo_height=30,
            input_max_height=88,
            send_button_size=34,
            spinner_size=30,
        )

    if width < 1120:
        return MainWindowMetrics(
            header_height=60,
            header_margins=(16, 8, 16, 8),
            input_margins=(36, 14, 36, 18),
            input_spacing=10,
            logo_height=36,
            input_max_height=96,
            send_button_size=36,
            spinner_size=34,
        )

    return MainWindowMetrics(
        header_height=68,
        header_margins=(20, 10, 20, 10),
        input_margins=(60, 16, 60, 20),
        input_spacing=12,
        logo_height=42,
        input_max_height=104,
        send_button_size=40,
        spinner_size=40,
    )


def chat_metrics(width: int) -> ChatMetrics:
    """Return chat container and bubble spacing values for a viewport width."""
    if width < 760:
        return ChatMetrics(
            container_margins=(20, 20, 20, 20),
            bubble_side_margin=20,
            bubble_inner_margin=40,
        )

    if width < 1120:
        return ChatMetrics(
            container_margins=(28, 20, 28, 20),
            bubble_side_margin=32,
            bubble_inner_margin=72,
        )

    return ChatMetrics(
        container_margins=(36, 20, 36, 20),
        bubble_side_margin=48,
        bubble_inner_margin=120,
    )


def bubble_margins(width: int, role: Role) -> tuple[int, int, int, int]:
    """Return chat bubble margins that preserve readable line length."""
    metrics = chat_metrics(width)
    side_margin = metrics.bubble_side_margin
    inner_margin = metrics.bubble_inner_margin

    if role == Role.USER:
        return (inner_margin, 8, side_margin, 8)
    return (side_margin, 8, inner_margin, 8)


def bubble_alignment(role: Role) -> Qt.AlignmentFlag:
    """Return the horizontal alignment for a bubble based on sender role."""
    return Qt.AlignRight if role == Role.USER else Qt.AlignLeft


def chat_container_margins(width: int) -> tuple[int, int, int, int]:
    """Return the outer chat container margins for the current width."""
    return chat_metrics(width).container_margins


def register_chat_bubble(
    chat_area: QScrollArea,
    container_layout: QVBoxLayout,
    bubbles: list[tuple[QFrame, Role]],
    bubble: QFrame,
    role: Role,
) -> None:
    """Store a bubble and apply responsive spacing immediately."""
    bubbles.append((bubble, role))
    apply_chat_responsive_layout(chat_area, container_layout, bubbles)


def insert_chat_bubble(
    container_layout: QVBoxLayout,
    bubble: QFrame,
    role: Role,
) -> None:
    """Insert a bubble using the alignment that matches its sender role."""
    insert_position = container_layout.count() - 1
    container_layout.insertWidget(insert_position, bubble, bubble_alignment(role))


def apply_chat_responsive_layout(
    chat_area: QScrollArea,
    container_layout: QVBoxLayout,
    bubbles: list[tuple[QFrame, Role]],
) -> None:
    """Apply all width-based chat spacing rules in one place."""
    width = chat_area.viewport().width()
    metrics = chat_metrics(width)
    container_layout.setContentsMargins(*metrics.container_margins)

    for bubble, role in bubbles:
        layout = bubble.layout()
        if layout is None:
            continue
        layout.setContentsMargins(*bubble_margins(width, role))


def dialog_size_for_parent(parent_width: int | None, parent_height: int | None) -> tuple[int, int]:
    """Compute a compact responsive size for standard dialogs."""
    width = parent_width or 900
    height = parent_height or 700
    dialog_width = max(520, min(900, int(width * 0.72)))
    dialog_height = max(360, min(640, int(height * 0.62)))
    return dialog_width, dialog_height


def edit_dialog_size_for_parent(parent_width: int | None, parent_height: int | None) -> tuple[int, int]:
    """Compute a larger responsive size for the markdown editing dialog."""
    width = parent_width or 900
    height = parent_height or 700
    dialog_width = max(820, min(1280, int(width * 0.94)))
    dialog_height = max(620, min(980, int(height * 0.88)))
    return dialog_width, dialog_height
