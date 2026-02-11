"""
Google OAuth2 authentication handling.
"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import json
from typing import Tuple, Optional
from ..config import settings


# Gmail API scopes
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]


def create_oauth_flow() -> Flow:
    """
    Create a Google OAuth2 flow instance.

    Returns:
        Flow object configured for Gmail API access
    """
    client_config = {
        "web": {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.google_redirect_uri],
        }
    }

    flow = Flow.from_client_config(
        client_config=client_config,
        scopes=SCOPES,
        redirect_uri=settings.google_redirect_uri,
    )

    return flow


def get_authorization_url() -> Tuple[str, str]:
    """
    Generate the Google OAuth authorization URL.

    Returns:
        Tuple of (authorization_url, state)
    """
    flow = create_oauth_flow()
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="select_account",  # Force account selection screen
        login_hint=None,  # Don't pre-select any account
    )
    return authorization_url, state


def exchange_code_for_credentials(code: str, state: str) -> Tuple[dict, dict]:
    """
    Exchange authorization code for credentials.

    Args:
        code: Authorization code from Google
        state: State parameter for CSRF protection

    Returns:
        Tuple of (credentials_dict, user_info)

    Raises:
        Exception: If token exchange fails
    """
    flow = create_oauth_flow()
    flow.fetch_token(code=code)

    credentials = flow.credentials

    # Get user info
    user_info = get_user_info(credentials)

    # Convert credentials to dictionary for storage
    credentials_dict = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

    return credentials_dict, user_info


def get_user_info(credentials: Credentials) -> dict:
    """
    Get user profile information from Google.

    Args:
        credentials: Google OAuth2 credentials

    Returns:
        Dictionary with user info (email, name, picture)
    """
    service = build("oauth2", "v2", credentials=credentials)
    user_info = service.userinfo().get().execute()

    return {
        "email": user_info.get("email"),
        "name": user_info.get("name"),
        "picture": user_info.get("picture"),
    }


def credentials_from_dict(credentials_dict: dict) -> Credentials:
    """
    Create Credentials object from dictionary.

    Args:
        credentials_dict: Dictionary containing credential fields

    Returns:
        Credentials object
    """
    return Credentials(
        token=credentials_dict.get("token"),
        refresh_token=credentials_dict.get("refresh_token"),
        token_uri=credentials_dict.get("token_uri"),
        client_id=credentials_dict.get("client_id"),
        client_secret=credentials_dict.get("client_secret"),
        scopes=credentials_dict.get("scopes"),
    )


def refresh_credentials_if_needed(credentials_dict: dict) -> Tuple[bool, dict]:
    """
    Refresh credentials if they're expired.

    Args:
        credentials_dict: Dictionary containing credential fields

    Returns:
        Tuple of (was_refreshed, updated_credentials_dict)
    """
    credentials = credentials_from_dict(credentials_dict)

    if not credentials.valid:
        if credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())

                # Update the credentials dictionary
                updated_dict = {
                    "token": credentials.token,
                    "refresh_token": credentials.refresh_token,
                    "token_uri": credentials.token_uri,
                    "client_id": credentials.client_id,
                    "client_secret": credentials.client_secret,
                    "scopes": credentials.scopes,
                }

                return True, updated_dict
            except Exception as e:
                raise Exception(f"Failed to refresh credentials: {str(e)}")

    return False, credentials_dict
