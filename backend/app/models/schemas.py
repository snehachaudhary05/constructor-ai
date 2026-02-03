"""
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserProfile(BaseModel):
    """User profile information from Google."""
    email: str
    name: str
    picture: Optional[str] = None


class AuthResponse(BaseModel):
    """Authentication response."""
    success: bool
    message: str
    user: Optional[UserProfile] = None
    session_id: Optional[str] = None


class EmailSummary(BaseModel):
    """Email summary with AI-generated content."""
    id: str
    sender: str
    sender_email: str
    subject: str
    snippet: str
    date: str
    summary: str
    body_preview: str


class EmailResponse(BaseModel):
    """AI-generated email response."""
    email_id: str
    subject: str
    proposed_reply: str
    original_subject: str
    original_sender: str


class ChatMessage(BaseModel):
    """Chat message in the conversation."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: Optional[datetime] = None
    metadata: Optional[dict] = None


class ChatRequest(BaseModel):
    """User chat message request."""
    message: str
    session_id: str


class ChatResponse(BaseModel):
    """Chatbot response."""
    message: str
    action: Optional[str] = None
    data: Optional[dict] = None


class EmailActionRequest(BaseModel):
    """Request for email actions."""
    action: str  # 'read', 'reply', 'delete'
    session_id: str
    email_id: Optional[str] = None
    message: Optional[str] = None


class EmailActionResponse(BaseModel):
    """Response for email actions."""
    success: bool
    message: str
    data: Optional[dict] = None


class SendReplyRequest(BaseModel):
    """Request to send an email reply."""
    session_id: str
    email_id: str
    reply_text: str
    original_subject: str


class DeleteEmailRequest(BaseModel):
    """Request to delete an email."""
    session_id: str
    email_id: str


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
