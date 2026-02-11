"""
AI service for generating email summaries and responses.
Supports OpenAI, Anthropic, and Google Gemini APIs with smart fallbacks.
"""

from typing import Optional
import time
import logging

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from ..config import settings


class AIService:
    """Service for AI-powered email operations."""

    def __init__(self):
        """Initialize AI service based on configured provider."""
        self.provider = settings.ai_provider.lower()
        self.max_retries = 3
        self.retry_delay = 1

        if self.provider == "openai":
            if not settings.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            self.openai_client = OpenAI(api_key=settings.openai_api_key)
            self.model = "gpt-4o"

        elif self.provider == "anthropic":
            if not settings.anthropic_api_key:
                raise ValueError("Anthropic API key not configured")
            self.anthropic_client = anthropic.Anthropic(
                api_key=settings.anthropic_api_key
            )
            self.model = "claude-3-sonnet-20240229"

        elif self.provider == "gemini":
            if not settings.gemini_api_key:
                raise ValueError("Gemini API key not configured")
            genai.configure(api_key=settings.gemini_api_key)
            self.gemini_client = genai.GenerativeModel('gemini-2.5-flash')
            self.model = "gemini-2.5-flash"

        elif self.provider == "fallback":
            self.model = "fallback"
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")

    def summarize_email(self, email_body: str, subject: str) -> str:
        """Generate a concise summary of an email."""
        prompt = f"""Summarize the following email in 2-3 concise sentences.

Subject: {subject}
Content: {email_body[:2000]}

Summary:"""
        return self._generate_completion(prompt, max_tokens=150)

    def generate_reply(
        self, email_body: str, subject: str, sender: str, context: Optional[str] = None
    ) -> str:
        """Generate a professional reply to an email."""
        context_text = f"\n\nContext: {context}" if context else ""
        prompt = f"""Write a professional email reply to {sender}.

Subject: {subject}
Original email: {email_body[:1500]}
{context_text}

Reply:"""
        return self._generate_completion(prompt, max_tokens=300)

    def parse_user_intent(self, user_message: str) -> dict:
        """Parse user's command to determine intent (keyword-based, no API calls)."""
        import re

        msg_lower = user_message.lower()
        intent = "general"
        count = None

        # Extract number if present
        numbers = re.findall(r'\d+', user_message)
        if numbers:
            count = int(numbers[0])

        # Check for read emails intent
        if any(kw in msg_lower for kw in ["show", "read", "get", "fetch", "last", "recent", "email", "emails"]):
            intent = "read_emails"
            if not count:
                count = 5

        # Check for reply intent
        elif any(kw in msg_lower for kw in ["reply", "respond", "answer"]):
            intent = "reply_to_email"

        # Check for delete intent
        elif "delete" in msg_lower or "remove" in msg_lower:
            intent = "delete_email"

        # Check for search intent
        elif "search" in msg_lower or "find" in msg_lower:
            intent = "search_emails"

        return {
            "intent": intent,
            "parameters": {
                "count": count,
                "sender": None,
                "subject_keyword": None,
                "email_reference": None
            },
            "confidence": "high"
        }

    def generate_chatbot_response(
        self, user_message: str, context: Optional[str] = None
    ) -> str:
        """Generate a conversational response for the chatbot."""
        context_text = f"\n\nContext: {context}" if context else ""
        prompt = f"""You are a helpful email assistant. Respond naturally.

User: {user_message}
{context_text}

Response:"""
        return self._generate_completion(prompt, max_tokens=200)

    def _generate_completion(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate completion with retry logic for rate limits."""
        for attempt in range(self.max_retries):
            try:
                if self.provider == "openai":
                    response = self.openai_client.chat.completions.create(
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=max_tokens,
                        temperature=0.7
                    )
                    return response.choices[0].message.content.strip()

                elif self.provider == "anthropic":
                    response = self.anthropic_client.messages.create(
                        model=self.model,
                        max_tokens=max_tokens,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    return response.content[0].text.strip()

                elif self.provider == "gemini":
                    response = self.gemini_client.generate_content(prompt)
                    return response.text.strip()

                elif self.provider == "fallback":
                    return self._fallback_response(prompt)

            except Exception as e:
                error_msg = str(e).lower()

                # Handle rate limit errors with backoff
                if "429" in str(e) or "quota" in error_msg or "rate" in error_msg:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(
                        f"Rate limited (attempt {attempt + 1}/{self.max_retries}). "
                        f"Waiting {wait_time}s..."
                    )

                    if attempt < self.max_retries - 1:
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.warning("Rate limit retries exhausted, using fallback")
                        return self._fallback_response(prompt)
                else:
                    logger.error(f"AI service error: {e}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    return self._fallback_response(prompt)

        return self._fallback_response(prompt)

    def _fallback_response(self, prompt: str) -> str:
        """Generate response without external API."""
        if "summarize" in prompt.lower():
            return "This email contains important information. Please review the full content."

        if "reply" in prompt.lower():
            return "Thank you for reaching out. I appreciate your message and will respond shortly with a detailed reply."

        if "indent" in prompt.lower() or "classify" in prompt.lower():
            import json
            if any(kw in prompt.lower() for kw in ["email", "show", "read", "last"]):
                return json.dumps({
                    "intent": "read_emails",
                    "parameters": {"count": 5, "sender": None, "subject_keyword": None, "email_reference": None},
                    "confidence": "high"
                })
            return json.dumps({
                "intent": "general",
                "parameters": {"count": None, "sender": None, "subject_keyword": None, "email_reference": None},
                "confidence": "medium"
            })

        return "I'm here to help with your emails. Ask me to show recent emails, reply, delete, or search."

