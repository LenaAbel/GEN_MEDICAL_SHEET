"""
Qt Stylesheets for clean light UI appearance.
CHU brand color: #1f80c2
"""
from PySide6.QtGui import QColor


# ==================== COLORS ====================

CHU_BLUE = QColor(31, 128, 194)  # #1f80c2


# ==================== MAIN WINDOW ====================

MAIN_WINDOW_STYLE = """
QMainWindow {
    background-color: #FFFFFF;
}
"""

# ==================== HEADER ====================

HEADER_STYLE = """
QWidget {
    background-color: #FFFFFF;
    border-bottom: 1px solid #EEEEEE;
}
"""

LOGO_STYLE = """
QLabel {
    background-color: transparent;
    padding: 10px;
}
"""

# ==================== CHAT AREA ====================

CHAT_WIDGET_STYLE = """
QScrollArea {
    background-color: #FFFFFF;
    border: none;
}
QWidget {
    background-color: #FFFFFF;
}
QScrollBar:vertical {
    background-color: #F0F0F0;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background-color: #CCCCCC;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background-color: #AAAAAA;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

# ==================== MESSAGE BUBBLES ====================

USER_BUBBLE_STYLE = """
QFrame {
    background-color: #1f80c2;
    border: none;
    padding: 12px 16px;
    border-radius: 12px;
}
QLabel {
    color: #FFFFFF;
    font-size: 14px;
    background-color: transparent;
}
QLabel a {
    color: #E0F0FF;
}
"""

ASSISTANT_BUBBLE_STYLE = """
QFrame {
    background-color: #F0F0F0;
    border: none;
    padding: 12px 16px;
    border-radius: 12px;
}
QLabel {
    color: #333333;
    font-size: 14px;
    background-color: transparent;
}
QLabel a {
    color: #1f80c2;
}
"""

# ==================== INPUT AREA ====================

INPUT_FIELD_STYLE = """
QTextEdit {
    background-color: #FFFFFF;
    color: #333333;
    border: 1px solid #DDDDDD;
    border-radius: 12px;
    padding: 12px 16px;
    font-size: 14px;
    selection-background-color: #1f80c2;
}
QTextEdit:focus {
    border: 1px solid #1f80c2;
}
"""

SEND_BUTTON_STYLE = """
QPushButton {
    background-color: #1f80c2;
    border: none;
    border-radius: 6px;
    padding: 8px;
    min-width: 36px;
    min-height: 36px;
}
QPushButton:hover {
    background-color: #2590d2;
}
QPushButton:pressed {
    background-color: #1a70b0;
}
QPushButton:disabled {
    background-color: #CCCCCC;
}
"""

AUDIO_CONTEXT_BADGE_STYLE = """
QFrame#audioContextBadge {
    color: #1568A3;
    background-color: #EEF7FC;
    border: 1px solid #BBDCF0;
    border-radius: 12px;
}
QFrame#audioContextBadge QLabel {
    color: #1568A3;
    background-color: transparent;
    border: none;
    padding: 0px;
    font-size: 12px;
    font-weight: 600;
}
"""

# ==================== SPINNER ====================

SPINNER_COLOR = CHU_BLUE
SPINNER_SIZE = 40
SPINNER_LINE_WIDTH = 3

# ==================== EDIT BUTTON====================
EDIT_BUTTON_STYLE = """
QPushButton {
                background-color: #1f80c2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1568a3;
            }
"""

# ==================== HEADER ACTIONS ====================
NEW_CONVERSATION_BUTTON_STYLE = """
QPushButton {
    background-color: transparent;
    border: 1px solid #D6E8F5;
    border-radius: 18px;
    padding: 5px;
}
QPushButton:hover {
    background-color: #EEF7FC;
}
QPushButton:pressed {
    background-color: #DCEEF9;
}
QPushButton:disabled {
    background-color: transparent;
    border-color: #E3E3E3;
}
"""

TRANSCRIPTION_BUTTON_STYLE = """
QPushButton {
    background-color: transparent;
    border: none;
    border-radius: 18px;
    padding: 6px;
}
QPushButton:hover {
    background-color: #EEF7FC;
}
QPushButton:pressed {
    background-color: #DCEEF9;
}
QPushButton:disabled {
    background-color: transparent;
}
"""

TRANSCRIPTION_TIMER_STYLE = """
QLabel {
    color: #1568A3;
    background-color: transparent;
    border: none;
    padding: 2px 4px;
    font-size: 12px;
    font-weight: 600;
}
"""

RECORDING_BUTTON_STYLE = """
QPushButton {
    background-color: #FFF1F0;
    border: 1px solid #E7AAA6;
    border-radius: 18px;
    padding: 5px;
}
QPushButton:hover {
    background-color: #FFE1DF;
}
QPushButton:pressed {
    background-color: #F8CBC8;
}
"""

RECORDING_TIMER_STYLE = """
QLabel {
    color: #A62B24;
    background-color: transparent;
    border: none;
    padding: 2px 4px;
    font-size: 12px;
    font-weight: 600;
}
"""

# ==================== EDIT DIALOG ====================
EDIT_DIALOG_STYLE = """
QDialog {
    background-color: #FFFFFF;
}
QPlainTextEdit {
    background-color: #FFFFFF;
    color: #333333;
    border: 1px solid #DDDDDD;
    border-radius: 12px;
    padding: 12px 16px;
    font-size: 14px;
    selection-background-color: #1f80c2;
}
QPlainTextEdit:focus {
    border: 1px solid #1f80c2;
}
QTextEdit {
    background-color: #FFFFFF;
    color: #333333;
    border: 1px solid #DDDDDD;
    border-radius: 12px;
    padding: 12px 16px;
    font-size: 14px;
    selection-background-color: #1f80c2;
}
QTextEdit:focus {
    border: 1px solid #1f80c2;
}
QTextBrowser {
    background-color: #FCFCFC;
    color: #333333;
    border: 1px solid #DDDDDD;
    border-radius: 12px;
    padding: 12px 16px;
    font-size: 14px;
}
QSplitter::handle {
    background-color: #E9E9E9;
    margin-left: 4px;
    margin-right: 4px;
    border-radius: 3px;
}

QToolBar {
    background: #FFFFFF;
    border: none;
    spacing: 6px;
}
QToolButton {
    background-color: #F7FAFC;
    color: #1f80c2;
    border: 1px solid #D9E7F2;
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 12px;
    font-weight: 600;
}
QToolButton:hover {
    background-color: #EEF7FC;
}
QToolButton:pressed {
    background-color: #DCEEF9;
}
"""

# ==================== DISCLAIMER ====================
DISCLAIMER_STYLE = """
QLabel {
    color: #999999;
    font-size: 11px;
    background-color: transparent;
}
"""
