from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QWidget, QLabel, QFrame
from PySide6.QtCore import Qt
from models.message import Role

class ChatWidget(QScrollArea):
    def __init__(self):
        super().__init__()
        # Configure scroll area
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Create container layout for messages
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.layout.addStretch()
        self.setWidget(self.container)

    def add_message(self, text: str, role: Role):
        # Create message bubble and label
        bubble = QFrame()
        bubble_layout = QVBoxLayout(bubble)
        label = QLabel(text)
        label.setWordWrap(True)
        bubble_layout.addWidget(label)
        
        # Style bubble according to role
        if role == Role.USER:
            bubble.setStyleSheet("background-color: #007AFF; color: white; border-radius: 10px; padding: 10px;")
            label.setAlignment(Qt.AlignRight)
        else:
            bubble.setStyleSheet("background-color: #E5E5EA; color: black; border-radius: 10px; padding: 10px;")
            label.setAlignment(Qt.AlignLeft)
        
        # Insert bubble and scroll to bottom
        self.layout.insertWidget(self.layout.count() - 1, bubble)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
