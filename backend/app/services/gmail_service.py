"""
Gmail API service for email operations.
"""

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText
import base64
from typing import List, Optional
from datetime import datetime
import re


class GmailService:
    """Service for Gmail API operations."""

    def __init__(self, credentials: Credentials):
        """
        Initialize Gmail service with user credentials.

        Args:
            credentials: Google OAuth2 credentials
        """
        self.service = build("gmail", "v1", credentials=credentials)

    def get_recent_emails(self, max_results: int = 5) -> List[dict]:
        """
        Fetch recent emails from the user's inbox.

        Args:
            max_results: Maximum number of emails to fetch (default: 5)

        Returns:
            List of email dictionaries with metadata and content
        """
        try:
            # Get list of messages
            results = (
                self.service.users()
                .messages()
                .list(userId="me", labelIds=["INBOX"], maxResults=max_results)
                .execute()
            )

            messages = results.get("messages", [])

            if not messages:
                return []

            emails = []
            for message in messages:
                email_data = self._get_email_details(message["id"])
                if email_data:
                    emails.append(email_data)

            return emails

        except Exception as e:
            raise Exception(f"Failed to fetch emails: {str(e)}")

    def _get_email_details(self, message_id: str) -> Optional[dict]:
        """
        Get detailed information about a specific email.

        Args:
            message_id: Gmail message ID

        Returns:
            Dictionary with email details
        """
        try:
            message = (
                self.service.users()
                .messages()
                .get(userId="me", id=message_id, format="full")
                .execute()
            )

            headers = message["payload"]["headers"]
            subject = self._get_header(headers, "Subject")
            sender = self._get_header(headers, "From")
            date = self._get_header(headers, "Date")

            # Extract sender name and email
            sender_name, sender_email = self._parse_sender(sender)

            # Get email body
            body = self._get_email_body(message["payload"])

            # Get snippet (short preview)
            snippet = message.get("snippet", "")

            return {
                "id": message_id,
                "subject": subject,
                "sender": sender_name,
                "sender_email": sender_email,
                "date": date,
                "snippet": snippet,
                "body": body,
                "thread_id": message.get("threadId"),
            }

        except Exception as e:
            print(f"Error getting email details for {message_id}: {str(e)}")
            return None

    def _get_header(self, headers: List[dict], name: str) -> str:
        """Extract header value by name."""
        for header in headers:
            if header["name"].lower() == name.lower():
                return header["value"]
        return ""

    def _parse_sender(self, sender: str) -> tuple:
        """
        Parse sender string into name and email.

        Args:
            sender: Sender string (e.g., "John Doe <john@example.com>")

        Returns:
            Tuple of (name, email)
        """
        # Match pattern: Name <email@example.com>
        match = re.match(r"(.+?)\s*<(.+?)>", sender)
        if match:
            return match.group(1).strip().strip('"'), match.group(2).strip()

        # If no name, just return email
        return sender, sender

    def _get_email_body(self, payload: dict) -> str:
        """
        Extract email body from payload.

        Args:
            payload: Email payload from Gmail API

        Returns:
            Email body text
        """
        body = ""

        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    if "data" in part["body"]:
                        body = base64.urlsafe_b64decode(part["body"]["data"]).decode(
                            "utf-8"
                        )
                        break
                elif part["mimeType"] == "text/html" and not body:
                    if "data" in part["body"]:
                        # Fallback to HTML if plain text not available
                        body = base64.urlsafe_b64decode(part["body"]["data"]).decode(
                            "utf-8"
                        )
        else:
            if "body" in payload and "data" in payload["body"]:
                body = base64.urlsafe_b64decode(payload["body"]["data"]).decode(
                    "utf-8"
                )

        return body

    def send_reply(
        self, email_id: str, reply_text: str, original_subject: str
    ) -> bool:
        """
        Send a reply to an email.

        Args:
            email_id: ID of the email to reply to
            reply_text: Text of the reply
            original_subject: Original email subject

        Returns:
            True if sent successfully
        """
        try:
            # Get the original message to get thread_id
            original_message = (
                self.service.users().messages().get(userId="me", id=email_id).execute()
            )

            thread_id = original_message["threadId"]

            # Get original headers for Reply-To
            headers = original_message["payload"]["headers"]
            to_email = self._get_header(headers, "From")
            message_id = self._get_header(headers, "Message-ID")

            # Prepare subject with Re: prefix if not already present
            subject = original_subject
            if not subject.lower().startswith("re:"):
                subject = f"Re: {subject}"

            # Create the message
            message = MIMEText(reply_text)
            message["to"] = to_email
            message["subject"] = subject
            message["In-Reply-To"] = message_id
            message["References"] = message_id

            # Encode the message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

            # Send the message
            send_message = {
                "raw": raw_message,
                "threadId": thread_id,
            }

            self.service.users().messages().send(
                userId="me", body=send_message
            ).execute()

            return True

        except Exception as e:
            raise Exception(f"Failed to send reply: {str(e)}")

    def delete_email(self, email_id: str) -> bool:
        """
        Delete an email (move to trash).

        Args:
            email_id: Gmail message ID

        Returns:
            True if deleted successfully
        """
        try:
            self.service.users().messages().trash(userId="me", id=email_id).execute()
            return True

        except Exception as e:
            raise Exception(f"Failed to delete email: {str(e)}")

    def search_emails(self, query: str, max_results: int = 10) -> List[dict]:
        """
        Search emails by query.

        Args:
            query: Gmail search query (e.g., "from:example@gmail.com")
            max_results: Maximum number of results

        Returns:
            List of email dictionaries
        """
        try:
            results = (
                self.service.users()
                .messages()
                .list(userId="me", q=query, maxResults=max_results)
                .execute()
            )

            messages = results.get("messages", [])

            if not messages:
                return []

            emails = []
            for message in messages:
                email_data = self._get_email_details(message["id"])
                if email_data:
                    emails.append(email_data)

            return emails

        except Exception as e:
            raise Exception(f"Failed to search emails: {str(e)}")
