"""
Sample tests for authentication module.
"""

import pytest
from app.auth.session import SessionStore


def test_session_creation():
    """Test creating a new session."""
    store = SessionStore()

    session_id = store.create_session(
        user_email="test@example.com",
        credentials={"token": "test_token"},
        user_info={"name": "Test User", "email": "test@example.com"},
    )

    assert session_id is not None
    assert len(session_id) > 0

    # Retrieve session
    session = store.get_session(session_id)
    assert session is not None
    assert session["email"] == "test@example.com"
    assert session["user_info"]["name"] == "Test User"


def test_session_expiration():
    """Test session expiration."""
    store = SessionStore()

    session_id = store.create_session(
        user_email="test@example.com",
        credentials={"token": "test_token"},
        user_info={"name": "Test User", "email": "test@example.com"},
    )

    # Valid session
    session = store.get_session(session_id)
    assert session is not None

    # Invalid session ID
    invalid_session = store.get_session("invalid_id")
    assert invalid_session is None


def test_session_deletion():
    """Test deleting a session."""
    store = SessionStore()

    session_id = store.create_session(
        user_email="test@example.com",
        credentials={"token": "test_token"},
        user_info={"name": "Test User", "email": "test@example.com"},
    )

    # Delete session
    result = store.delete_session(session_id)
    assert result is True

    # Session should not exist
    session = store.get_session(session_id)
    assert session is None


def test_update_credentials():
    """Test updating session credentials."""
    store = SessionStore()

    session_id = store.create_session(
        user_email="test@example.com",
        credentials={"token": "old_token"},
        user_info={"name": "Test User", "email": "test@example.com"},
    )

    # Update credentials
    new_credentials = {"token": "new_token", "refresh_token": "refresh"}
    result = store.update_credentials(session_id, new_credentials)
    assert result is True

    # Verify update
    session = store.get_session(session_id)
    assert session["credentials"]["token"] == "new_token"
    assert session["credentials"]["refresh_token"] == "refresh"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
