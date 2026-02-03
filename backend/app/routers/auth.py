"""
Authentication router for Google OAuth flow.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
from ..auth import (
    get_authorization_url,
    exchange_code_for_credentials,
    session_store,
)
from ..models import AuthResponse, UserProfile
from ..config import settings
import logging

router = APIRouter(prefix="/auth", tags=["authentication"])
logger = logging.getLogger(__name__)


@router.get("/login")
async def login():
    """
    Initiate Google OAuth login flow.

    Returns:
        Redirect to Google OAuth consent screen
    """
    try:
        auth_url, state = get_authorization_url()
        return RedirectResponse(url=auth_url)
    except Exception as e:
        logger.error(f"Login initiation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to initiate login")


@router.get("/callback")
async def auth_callback(
    code: str = Query(...), state: str = Query(None), error: str = Query(None)
):
    """
    Handle OAuth callback from Google.

    Args:
        code: Authorization code from Google
        state: State parameter for CSRF protection
        error: Error message if authorization failed

    Returns:
        Redirect to frontend with session info
    """
    if error:
        logger.error(f"OAuth error: {error}")
        return RedirectResponse(
            url=f"{settings.frontend_url}/?error=auth_failed&message={error}"
        )

    try:
        # Exchange code for credentials
        credentials_dict, user_info = exchange_code_for_credentials(code, state)

        # Create session
        session_id = session_store.create_session(
            user_email=user_info["email"],
            credentials=credentials_dict,
            user_info=user_info,
        )

        # Redirect to frontend with session ID
        redirect_url = (
            f"{settings.frontend_url}/dashboard"
            f"?session_id={session_id}"
            f"&email={user_info['email']}"
            f"&name={user_info.get('name', '')}"
        )

        return RedirectResponse(url=redirect_url)

    except Exception as e:
        logger.error(f"OAuth callback failed: {e}")
        return RedirectResponse(
            url=f"{settings.frontend_url}/?error=auth_failed&message=Failed+to+complete+authentication"
        )


@router.post("/logout")
async def logout(session_id: str):
    """
    Logout user and destroy session.

    Args:
        session_id: User's session identifier

    Returns:
        Success message
    """
    try:
        session_store.delete_session(session_id)
        return {"success": True, "message": "Logged out successfully"}
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to logout")


@router.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """
    Get session information.

    Args:
        session_id: Session identifier

    Returns:
        Session info including user profile
    """
    session = session_store.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=401, detail="Session not found or expired. Please login again."
        )

    return {
        "valid": True,
        "user": session["user_info"],
        "email": session["email"],
    }
