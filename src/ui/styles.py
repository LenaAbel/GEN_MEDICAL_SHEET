"""
Qt Stylesheets for clean light UI appearance.
CHU brand color: #1f80c2
"""

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
    margin: 8px 20px 8px 100px;
    padding: 12px 16px;
    border-radius: 12px;
}
QLabel {
    color: #FFFFFF;
    font-size: 14px;
    background-color: transparent;
}
"""

ASSISTANT_BUBBLE_STYLE = """
QFrame {
    background-color: #F0F0F0;
    border: none;
    margin: 8px 100px 8px 20px;
    padding: 12px 16px;
    border-radius: 12px;
}
QLabel {
    color: #333333;
    font-size: 14px;
    background-color: transparent;
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
