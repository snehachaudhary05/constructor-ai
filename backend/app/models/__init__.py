"""Models package."""

from .schemas import (
    UserProfile,
    AuthResponse,
    EmailSummary,
    EmailResponse,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    EmailActionRequest,
    EmailActionResponse,
    SendReplyRequest,
    DeleteEmailRequest,
    ErrorResponse,
)

__all__ = [
    "UserProfile",
    "AuthResponse",
    "EmailSummary",
    "EmailResponse",
    "ChatMessage",
    "ChatRequest",
    "ChatResponse",
    "EmailActionRequest",
    "EmailActionResponse",
    "SendReplyRequest",
    "DeleteEmailRequest",
    "ErrorResponse",
]
