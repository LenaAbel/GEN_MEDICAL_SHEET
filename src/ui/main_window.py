from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton
from PySide6.QtCore import QThread, Signal
from ui.chat_widget import ChatWidget
from services.mistral_service import MistralService
from models.message import Role

class ApiWorker(QThread):
    response_ready = Signal(str)
    
    def __init__(self, service: MistralService, user_text: str):
        super().__init__()
        # Store service instance and the user text to send
        self.mistral_service = service
        self.user_text = user_text
    
    def run(self):
        # Call service in background and emit assistant text
        assistant_text = self.mistral_service.send_message(self.user_text)
        self.response_ready.emit(assistant_text)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Initialize window
        self.setWindowTitle("Medical Sheet Generator")
        self.setMinimumSize(800, 600)
        
        # Create single service instance to keep conversation context
        self.mistral_service = MistralService()
        self.setup_ui()
    
    def setup_ui(self):
        # Build UI layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        self.chat_widget = ChatWidget()
        layout.addWidget(self.chat_widget)
        
        input_layout = QHBoxLayout()
        self.input_field = QTextEdit()
        self.input_field.setMaximumHeight(80)
        self.input_field.setPlaceholderText("Type your message...")
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)
    
    def send_message(self):
        # Read text from input and ignore if empty
        user_text = self.input_field.toPlainText().strip()
        if not user_text:
            return
        
        # Display user message and prepare UI for background call
        self.chat_widget.add_message(user_text, Role.USER)
        self.input_field.clear()
        self.send_button.setEnabled(False)
        
        # Start background worker to call API
        self.api_worker = ApiWorker(self.mistral_service, user_text)
        self.api_worker.response_ready.connect(self.handle_response)
        self.api_worker.start()
    
    def handle_response(self, assistant_text: str):
        # Display assistant reply and re-enable UI control
        self.chat_widget.add_message(assistant_text, Role.ASSISTANT)
        self.send_button.setEnabled(True)
