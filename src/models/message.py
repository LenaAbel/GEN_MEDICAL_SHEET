from dataclasses import dataclass
from enum import Enum

class Role(Enum):
    # Define roles used in chat messages
    USER = "user"
    ASSISTANT = "assistant"

@dataclass
class Message:
    # Represent a chat message
    role: Role
    content: str
