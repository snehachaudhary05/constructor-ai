"""
Chatbot router for conversational AI interface.
"""

from fastapi import APIRouter, HTTPException
from typing import List
from ..models import ChatRequest, ChatResponse, EmailSummary
from ..auth import session_store, credentials_from_dict, refresh_credentials_if_needed
from ..services import GmailService, AIService
import logging

router = APIRouter(prefix="/chatbot", tags=["chatbot"])
logger = logging.getLogger(__name__)


@router.post("/message", response_model=ChatResponse)
async def process_message(request: ChatRequest):
    """
    Process user message and determine action.

    Args:
        request: User message and session ID

    Returns:
        Chatbot response with action and data
    """
    # Validate session
    session = session_store.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    try:
        # Initialize AI service
        ai_service = AIService()

        # Parse user intent
        intent_data = ai_service.parse_user_intent(request.message)
        intent = intent_data.get("intent", "general")
        parameters = intent_data.get("parameters", {})

        logger.info(f"Parsed intent: {intent}, parameters: {parameters}")

        # Handle different intents
        if intent == "read_emails":
            return await handle_read_emails(session, parameters, ai_service)

        elif intent == "reply_to_email":
            # For reply intent, we need more context
            return ChatResponse(
                message="I can help you reply to an email. Please first let me show you your recent emails, then you can choose which one to reply to.",
                action="read_emails_for_reply",
            )

        elif intent == "delete_email":
            return ChatResponse(
                message="I can help you delete an email. Please let me show you your recent emails first, then you can choose which one to delete.",
                action="read_emails_for_delete",
            )

        elif intent == "search_emails":
            sender = parameters.get("sender")
            keyword = parameters.get("subject_keyword")

            if sender or keyword:
                return await handle_search_emails(
                    session, sender, keyword, ai_service
                )
            else:
                return ChatResponse(
                    message="What would you like to search for? Please specify a sender name or subject keyword.",
                    action="general",
                )

        else:
            # General conversation
            response = ai_service.generate_chatbot_response(
                request.message,
                context=f"User is logged in as {session['email']}. Available actions: read emails, reply to emails, delete emails, search emails.",
            )

            return ChatResponse(message=response, action="general")

    except Exception as e:
        logger.error(f"Message processing failed: {e}")
        return ChatResponse(
            message=f"Sorry, I encountered an error: {str(e)}. Please try again.",
            action="error",
        )


async def handle_read_emails(session: dict, parameters: dict, ai_service: AIService):
    """Handle reading recent emails."""
    try:
        # Get credentials and refresh if needed
        credentials_dict = session["credentials"]
        was_refreshed, updated_creds = refresh_credentials_if_needed(credentials_dict)

        if was_refreshed:
            session_store.update_credentials(session["email"], updated_creds)

        credentials = credentials_from_dict(updated_creds)

        # Fetch emails
        gmail_service = GmailService(credentials)
        count = parameters.get("count", 5)
        count = min(max(count if count else 5, 1), 10)  # Limit between 1-10

        emails = gmail_service.get_recent_emails(max_results=count)

        if not emails:
            return ChatResponse(
                message="You don't have any emails in your inbox.",
                action="no_emails",
            )

        # Generate summaries for each email
        email_summaries = []
        for email in emails:
            try:
                summary = ai_service.summarize_email(email["body"], email["subject"])
                email_summaries.append(
                    {
                        "id": email["id"],
                        "sender": email["sender"],
                        "sender_email": email["sender_email"],
                        "subject": email["subject"],
                        "date": email["date"],
                        "snippet": email["snippet"],
                        "summary": summary,
                        "body_preview": email["body"][:200],
                    }
                )
            except Exception as e:
                logger.error(f"Failed to summarize email {email['id']}: {e}")
                email_summaries.append(
                    {
                        "id": email["id"],
                        "sender": email["sender"],
                        "sender_email": email["sender_email"],
                        "subject": email["subject"],
                        "date": email["date"],
                        "snippet": email["snippet"],
                        "summary": "Summary unavailable",
                        "body_preview": email["body"][:200],
                    }
                )

        return ChatResponse(
            message=f"Here are your {len(email_summaries)} most recent emails:",
            action="show_emails",
            data={"emails": email_summaries},
        )

    except Exception as e:
        logger.error(f"Failed to read emails: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch emails: {str(e)}")


async def handle_search_emails(
    session: dict, sender: str, keyword: str, ai_service: AIService
):
    """Handle searching emails."""
    try:
        credentials_dict = session["credentials"]
        was_refreshed, updated_creds = refresh_credentials_if_needed(credentials_dict)

        if was_refreshed:
            session_store.update_credentials(session["email"], updated_creds)

        credentials = credentials_from_dict(updated_creds)
        gmail_service = GmailService(credentials)

        # Build search query
        query_parts = []
        if sender:
            query_parts.append(f"from:{sender}")
        if keyword:
            query_parts.append(f"subject:{keyword}")

        query = " ".join(query_parts)

        emails = gmail_service.search_emails(query, max_results=5)

        if not emails:
            return ChatResponse(
                message=f"No emails found matching your search criteria.",
                action="no_results",
            )

        # Generate summaries
        email_summaries = []
        for email in emails:
            summary = ai_service.summarize_email(email["body"], email["subject"])
            email_summaries.append(
                {
                    "id": email["id"],
                    "sender": email["sender"],
                    "sender_email": email["sender_email"],
                    "subject": email["subject"],
                    "date": email["date"],
                    "summary": summary,
                }
            )

        return ChatResponse(
            message=f"Found {len(email_summaries)} emails matching your search:",
            action="show_emails",
            data={"emails": email_summaries},
        )

    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/welcome/{session_id}")
async def get_welcome_message(session_id: str):
    """
    Get personalized welcome message for the chatbot.

    Args:
        session_id: User's session ID

    Returns:
        Welcome message with user info
    """
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")

    user_info = session["user_info"]
    name = user_info.get("name", "there")

    welcome_message = f"""Hello {name}! 👋

I'm your AI email assistant. I can help you manage your Gmail inbox with the following capabilities:

📧 **Read Emails** - View your recent emails with AI-generated summaries
✍️ **Reply to Emails** - Generate professional responses to your emails
🗑️ **Delete Emails** - Remove unwanted emails from your inbox
🔍 **Search Emails** - Find specific emails by sender or subject

Just tell me what you'd like to do in natural language! For example:
- "Show me my last 5 emails"
- "Help me reply to the email from John"
- "Delete emails from spam@example.com"

What would you like to do?"""

    return {"message": welcome_message, "user": user_info}
