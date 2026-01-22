"""
Custom loading spinner widget for PySide6.
"""
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QPainter, QColor, QPen

from ui.styles import SPINNER_COLOR, SPINNER_SIZE, SPINNER_LINE_WIDTH


class LoadingSpinner(QWidget):
    """Animated circular loading spinner."""

    def __init__(self, parent: QWidget = None, color: QColor = None) -> None:
        super().__init__(parent)
        self._angle = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)
        self._color = color or SPINNER_COLOR
        self._line_width = SPINNER_LINE_WIDTH
        self._size = SPINNER_SIZE
        
        self.setFixedSize(self._size, self._size)
        # Start hidden, show when spinning
        self.setVisible(False)

    # ==================== PUBLIC METHODS ====================

    def start(self) -> None:
        """Start spinning animation."""
        self.setVisible(True)
        self._timer.start(50)

    def stop(self) -> None:
        """Stop spinning animation."""
        self._timer.stop()
        self.setVisible(False)

    def set_color(self, color: QColor) -> None:
        """Set spinner color."""
        self._color = color

    # ==================== INTERNAL ====================

    def _rotate(self) -> None:
        """Increment angle and trigger repaint."""
        self._angle = (self._angle + 30) % 360
        self.update()

    # ==================== PAINTING ====================

    def paintEvent(self, event) -> None:
        """Draw the spinner arc."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        pen = QPen(self._color)
        pen.setWidth(self._line_width)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        
        margin = self._line_width + 2
        rect = QRectF(margin, margin, self._size - 2 * margin, self._size - 2 * margin)
        
        # Draw partial arc (270 degrees) starting from current angle
        painter.drawArc(rect, self._angle * 16, 270 * 16)
