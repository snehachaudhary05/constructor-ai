"""
Chatbot router for conversational AI interface.
"""

from fastapi import APIRouter, HTTPException
from ..models import ChatRequest, ChatResponse
from ..auth import session_store, credentials_from_dict, refresh_credentials_if_needed
from ..services import GmailService, AIService
import logging

router = APIRouter(prefix="/chatbot", tags=["chatbot"])
logger = logging.getLogger(__name__)


@router.post("/message", response_model=ChatResponse)
async def process_message(request: ChatRequest):
    """Process user message and determine action."""
    session = session_store.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    try:
        ai_service = AIService()
        intent_data = ai_service.parse_user_intent(request.message)
        intent = intent_data.get("intent", "general")
        parameters = intent_data.get("parameters", {})

        logger.info(f"Intent: {intent}, parameters: {parameters}")

        if intent == "read_emails":
            return await handle_read_emails(session, parameters, ai_service)

        elif intent == "reply_to_email":
            return ChatResponse(
                message="I can help you reply. Please let me show you your recent emails first, then select one to reply to.",
                action="read_emails_for_reply",
            )

        elif intent == "delete_email":
            return ChatResponse(
                message="I can help you delete an email. Let me show you your recent emails first.",
                action="read_emails_for_delete",
            )

        elif intent == "search_emails":
            sender = parameters.get("sender")
            keyword = parameters.get("subject_keyword")
            if sender or keyword:
                return await handle_search_emails(session, sender, keyword, ai_service)
            return ChatResponse(
                message="What would you like to search for? Specify a sender or subject keyword.",
                action="general",
            )

        else:
            try:
                response = ai_service.generate_chatbot_response(
                    request.message,
                    context=f"User: {session['email']}. Can read/reply/delete/search emails."
                )
                return ChatResponse(message=response, action="general")
            except Exception as e:
                logger.warning(f"Response generation failed: {e}")
                return ChatResponse(
                    message="I'm here to help manage your emails. Show recent emails, reply, delete, or search.",
                    action="general",
                )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Message processing error: {e}")
        return ChatResponse(
            message="Sorry, I encountered an error. Please try again.",
            action="error",
        )


async def handle_read_emails(session: dict, parameters: dict, ai_service: AIService):
    """Handle reading recent emails."""
    try:
        credentials_dict = session["credentials"]
        was_refreshed, updated_creds = refresh_credentials_if_needed(credentials_dict)

        if was_refreshed:
            session_store.update_credentials(session["email"], updated_creds)

        credentials = credentials_from_dict(updated_creds)
        gmail_service = GmailService(credentials)
        
        count = parameters.get("count", 5)
        count = min(max(count if count else 5, 1), 10)

        emails = gmail_service.get_recent_emails(max_results=count)

        if not emails:
            return ChatResponse(
                message="You don't have any emails in your inbox.",
                action="no_emails",
            )

        email_summaries = []
        for email in emails:
            try:
                summary = ai_service.summarize_email(email["body"], email["subject"])
            except Exception as e:
                logger.warning(f"Summary failed for {email['id']}: {e}")
                summary = email["snippet"][:200] or "Email preview unavailable"

            email_summaries.append({
                "id": email["id"],
                "sender": email["sender"],
                "sender_email": email["sender_email"],
                "subject": email["subject"],
                "date": email["date"],
                "snippet": email["snippet"],
                "summary": summary,
                "body_preview": email["body"][:200],
            })

        return ChatResponse(
            message=f"Here are your {len(email_summaries)} most recent emails:",
            action="show_emails",
            data={"emails": email_summaries},
        )

    except Exception as e:
        logger.error(f"Read emails failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch emails.")


async def handle_search_emails(session: dict, sender: str, keyword: str, ai_service: AIService):
    """Handle searching emails."""
    try:
        credentials_dict = session["credentials"]
        was_refreshed, updated_creds = refresh_credentials_if_needed(credentials_dict)

        if was_refreshed:
            session_store.update_credentials(session["email"], updated_creds)

        credentials = credentials_from_dict(updated_creds)
        gmail_service = GmailService(credentials)

        query_parts = []
        if sender:
            query_parts.append(f"from:{sender}")
        if keyword:
            query_parts.append(f"subject:{keyword}")

        emails = gmail_service.search_emails(" ".join(query_parts), max_results=5)

        if not emails:
            return ChatResponse(
                message="No emails found matching your search.",
                action="no_results",
            )

        email_summaries = []
        for email in emails:
            try:
                summary = ai_service.summarize_email(email["body"], email["subject"])
            except Exception as e:
                logger.warning(f"Summary failed: {e}")
                summary = email["snippet"][:200]

            email_summaries.append({
                "id": email["id"],
                "sender": email["sender"],
                "sender_email": email["sender_email"],
                "subject": email["subject"],
                "date": email["date"],
                "summary": summary,
            })

        return ChatResponse(
            message=f"Found {len(email_summaries)} emails:",
            action="show_emails",
            data={"emails": email_summaries},
        )

    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail="Search failed.")


@router.get("/welcome/{session_id}")
async def get_welcome_message(session_id: str):
    """Get personalized welcome message."""
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")

    user_info = session["user_info"]
    name = user_info.get("name", "there")

    welcome_message = f"""Hello {name}! 👋

I'm your AI email assistant. I can help you manage your Gmail inbox with:

📧 **Read Emails** - View recent emails with AI summaries
✍️ **Reply to Emails** - Generate professional responses
🗑️ **Delete Emails** - Remove unwanted emails
🔍 **Search Emails** - Find specific emails

Just tell me what you'd like! Examples:
- "Show me my last 5 emails"
- "Help me reply to the email from John"
- "Delete emails from spam@example.com"

What would you like to do?"""

    return {"message": welcome_message, "user": user_info}
