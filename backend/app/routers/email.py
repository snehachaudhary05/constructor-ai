"""
Email operations router for Gmail actions.
"""

from fastapi import APIRouter, HTTPException
from ..models import SendReplyRequest, DeleteEmailRequest, EmailActionResponse
from ..auth import session_store, credentials_from_dict, refresh_credentials_if_needed
from ..services import GmailService, AIService
import logging

router = APIRouter(prefix="/email", tags=["email"])
logger = logging.getLogger(__name__)


@router.post("/generate-reply")
async def generate_reply(email_id: str, session_id: str):
    """
    Generate AI reply for a specific email.

    Args:
        email_id: Gmail message ID
        session_id: User's session ID

    Returns:
        Proposed reply text
    """
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    try:
        # Get credentials
        credentials_dict = session["credentials"]
        was_refreshed, updated_creds = refresh_credentials_if_needed(credentials_dict)

        if was_refreshed:
            session_store.update_credentials(session["email"], updated_creds)

        credentials = credentials_from_dict(updated_creds)

        # Fetch the specific email
        gmail_service = GmailService(credentials)
        emails = gmail_service.get_recent_emails(max_results=20)

        # Find the email
        target_email = next((e for e in emails if e["id"] == email_id), None)

        if not target_email:
            raise HTTPException(status_code=404, detail="Email not found")

        # Generate reply
        ai_service = AIService()
        reply_text = ai_service.generate_reply(
            email_body=target_email["body"],
            subject=target_email["subject"],
            sender=target_email["sender"],
        )

        return {
            "success": True,
            "email_id": email_id,
            "subject": target_email["subject"],
            "sender": target_email["sender"],
            "proposed_reply": reply_text,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate reply: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate reply: {str(e)}")


@router.post("/send-reply", response_model=EmailActionResponse)
async def send_reply(request: SendReplyRequest):
    """
    Send a reply to an email.

    Args:
        request: Reply request with email ID, reply text, and subject

    Returns:
        Success status
    """
    session = session_store.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    try:
        # Get credentials
        credentials_dict = session["credentials"]
        was_refreshed, updated_creds = refresh_credentials_if_needed(credentials_dict)

        if was_refreshed:
            session_store.update_credentials(session["email"], updated_creds)

        credentials = credentials_from_dict(updated_creds)

        # Send reply
        gmail_service = GmailService(credentials)
        success = gmail_service.send_reply(
            email_id=request.email_id,
            reply_text=request.reply_text,
            original_subject=request.original_subject,
        )

        if success:
            return EmailActionResponse(
                success=True, message="Reply sent successfully!"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to send reply")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send reply: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to send reply: {str(e)}"
        )


@router.post("/delete", response_model=EmailActionResponse)
async def delete_email(request: DeleteEmailRequest):
    """
    Delete an email (move to trash).

    Args:
        request: Delete request with email ID

    Returns:
        Success status
    """
    session = session_store.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    try:
        # Get credentials
        credentials_dict = session["credentials"]
        was_refreshed, updated_creds = refresh_credentials_if_needed(credentials_dict)

        if was_refreshed:
            session_store.update_credentials(session["email"], updated_creds)

        credentials = credentials_from_dict(updated_creds)

        # Delete email
        gmail_service = GmailService(credentials)
        success = gmail_service.delete_email(request.email_id)

        if success:
            return EmailActionResponse(
                success=True, message="Email deleted successfully!"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to delete email")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete email: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to delete email: {str(e)}"
        )


@router.get("/details/{email_id}")
async def get_email_details(email_id: str, session_id: str):
    """
    Get detailed information about a specific email.

    Args:
        email_id: Gmail message ID
        session_id: User's session ID

    Returns:
        Email details
    """
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    try:
        credentials_dict = session["credentials"]
        was_refreshed, updated_creds = refresh_credentials_if_needed(credentials_dict)

        if was_refreshed:
            session_store.update_credentials(session["email"], updated_creds)

        credentials = credentials_from_dict(updated_creds)

        gmail_service = GmailService(credentials)
        emails = gmail_service.get_recent_emails(max_results=20)

        target_email = next((e for e in emails if e["id"] == email_id), None)

        if not target_email:
            raise HTTPException(status_code=404, detail="Email not found")

        return {
            "success": True,
            "email": target_email,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get email details: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get email details: {str(e)}"
        )
