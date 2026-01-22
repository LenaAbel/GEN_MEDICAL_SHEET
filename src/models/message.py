"""
Data models for chat messages.
"""
from dataclasses import dataclass
from enum import Enum


# ==================== ENUMS ====================

class Role(Enum):
    """Roles used in chat conversation."""
    USER = "user"
    ASSISTANT = "assistant"


# ==================== DATA CLASSES ====================

@dataclass
class Message:
    """Represents a single chat message."""
    role: Role
    content: str
