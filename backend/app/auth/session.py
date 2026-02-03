"""
Session management for authenticated users.
Stores user credentials and tokens in memory (for simplicity).
In production, use Redis or a proper database.
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
import secrets
from ..config import settings


class SessionStore:
    """In-memory session store for user credentials."""

    def __init__(self):
        self._sessions: Dict[str, dict] = {}

    def create_session(self, user_email: str, credentials: dict, user_info: dict) -> str:
        """
        Create a new session for an authenticated user.

        Args:
            user_email: User's email address
            credentials: Google OAuth credentials
            user_info: User profile information

        Returns:
            session_id: Unique session identifier
        """
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=settings.session_expire_hours)

        self._sessions[session_id] = {
            "email": user_email,
            "credentials": credentials,
            "user_info": user_info,
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "last_accessed": datetime.utcnow(),
        }

        return session_id

    def get_session(self, session_id: str) -> Optional[dict]:
        """
        Get session data by session ID.

        Args:
            session_id: Session identifier

        Returns:
            Session data or None if not found/expired
        """
        if session_id not in self._sessions:
            return None

        session = self._sessions[session_id]

        # Check if session has expired
        if datetime.utcnow() > session["expires_at"]:
            del self._sessions[session_id]
            return None

        # Update last accessed time
        session["last_accessed"] = datetime.utcnow()

        return session

    def update_credentials(self, session_id: str, credentials: dict) -> bool:
        """
        Update credentials for a session (e.g., after token refresh).

        Args:
            session_id: Session identifier
            credentials: Updated credentials

        Returns:
            True if updated, False if session not found
        """
        if session_id not in self._sessions:
            return False

        self._sessions[session_id]["credentials"] = credentials
        return True

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session identifier

        Returns:
            True if deleted, False if not found
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def cleanup_expired_sessions(self):
        """Remove all expired sessions."""
        now = datetime.utcnow()
        expired_sessions = [
            sid for sid, data in self._sessions.items() if now > data["expires_at"]
        ]
        for sid in expired_sessions:
            del self._sessions[sid]


# Global session store instance
session_store = SessionStore()
