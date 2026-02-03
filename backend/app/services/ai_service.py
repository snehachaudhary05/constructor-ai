"""
AI service for generating email summaries and responses.
Supports OpenAI, Anthropic, and Google Gemini APIs.
"""

from typing import List, Optional
from openai import OpenAI
import anthropic
import google.generativeai as genai
from ..config import settings


class AIService:
    """Service for AI-powered email operations."""

    def __init__(self):
        """Initialize AI service based on configured provider."""
        self.provider = settings.ai_provider.lower()

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
            # Fallback mode - works without any AI API
            self.model = "fallback"

        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")

    def summarize_email(self, email_body: str, subject: str) -> str:
        """
        Generate a concise summary of an email.

        Args:
            email_body: Full email body text
            subject: Email subject line

        Returns:
            AI-generated summary (2-3 sentences)
        """
        prompt = f"""Summarize the following email in 2-3 concise sentences. Focus on the key points and action items.

Subject: {subject}

Email content:
{email_body[:2000]}

Provide a clear, professional summary:"""

        return self._generate_completion(prompt, max_tokens=150)

    def generate_reply(
        self, email_body: str, subject: str, sender: str, context: Optional[str] = None
    ) -> str:
        """
        Generate a professional reply to an email.

        Args:
            email_body: Original email body
            subject: Original email subject
            sender: Sender's name
            context: Additional context for the reply

        Returns:
            AI-generated reply text
        """
        context_text = f"\n\nAdditional context: {context}" if context else ""

        prompt = f"""Write a professional, friendly email reply to the following email. Keep it concise but complete.

From: {sender}
Subject: {subject}

Original email:
{email_body[:1500]}
{context_text}

Generate a professional reply:"""

        return self._generate_completion(prompt, max_tokens=300)

    def parse_user_intent(self, user_message: str) -> dict:
        """
        Parse user's natural language command to determine intent and extract parameters.

        Args:
            user_message: User's chat message

        Returns:
            Dictionary with intent and parameters
        """
        import logging
        import json
        import re

        logger = logging.getLogger(__name__)

        # Simple keyword-based intent detection for fallback mode
        if self.provider == "fallback":
            msg_lower = user_message.lower()
            intent = "general"
            count = None

            # Extract number if present
            numbers = re.findall(r'\d+', user_message)
            if numbers:
                count = int(numbers[0])

            # Check for read emails intent
            if any(keyword in msg_lower for keyword in ["show", "read", "get", "fetch", "last", "recent", "email"]):
                intent = "read_emails"
                if not count:
                    count = 5  # Default to 5 emails

            # Check for reply intent
            elif any(keyword in msg_lower for keyword in ["reply", "respond", "answer"]):
                intent = "reply_to_email"

            # Check for delete intent
            elif "delete" in msg_lower or "remove" in msg_lower:
                intent = "delete_email"

            # Check for search intent
            elif "search" in msg_lower or "find" in msg_lower:
                intent = "search_emails"

            logger.info(f"Fallback intent parsing: {intent} with count={count}")

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

        # For AI providers, use AI-based intent parsing
        prompt = f"""Analyze this user message and determine their intent related to email management.

User message: "{user_message}"

Classify the intent as one of:
- "read_emails": User wants to see recent emails
- "reply_to_email": User wants to reply to an email
- "delete_email": User wants to delete an email
- "search_emails": User wants to search for specific emails
- "general": General conversation or unclear intent

Also extract any parameters like:
- number of emails to show
- sender name or email
- subject keywords
- email reference (like "email 1", "the first one", etc.)

Respond in this exact JSON format:
{{
    "intent": "intent_name",
    "parameters": {{
        "count": number or null,
        "sender": "sender" or null,
        "subject_keyword": "keyword" or null,
        "email_reference": "reference" or null
    }},
    "confidence": "high" or "medium" or "low"
}}

JSON response:"""

        response = self._generate_completion(prompt, max_tokens=200)

        # Parse JSON response
        try:
            # Extract JSON from response (in case there's extra text)
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except Exception as e:
            logger.error(f"Failed to parse intent: {e}, response: {response}")

        # Fallback to general intent
        return {
            "intent": "general",
            "parameters": {},
            "confidence": "low",
        }

    def generate_chatbot_response(
        self, user_message: str, context: Optional[str] = None
    ) -> str:
        """
        Generate a conversational response for the chatbot.

        Args:
            user_message: User's message
            context: Additional context from conversation

        Returns:
            Chatbot response
        """
        context_text = f"\n\nContext: {context}" if context else ""

        prompt = f"""You are a helpful email assistant chatbot. Respond naturally and professionally to the user's message.

User: {user_message}
{context_text}
"""

        return self._generate_completion(prompt, max_tokens=200)

    def _generate_completion(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate completion using configured AI provider."""
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
                # Simple fallback mode without AI
                if "Summarize" in prompt or "summary" in prompt.lower():
                    # Extract email content
                    lines = prompt.split('\n')
                    content_lines = [l for l in lines if l.strip() and not l.startswith('Subject:') and not l.startswith('Email')]
                    preview = ' '.join(content_lines[:3])[:200]
                    return f"This email discusses: {preview}..."

                elif "reply" in prompt.lower() or "response" in prompt.lower():
                    return "Thank you for your email. I have reviewed your message and will get back to you shortly with a detailed response."

                elif "intent" in prompt.lower() or "classify" in prompt.lower():
                    # Simple intent parsing for chatbot
                    import json
                    user_msg = prompt.lower()
                    if "email" in user_msg or "show" in user_msg or "read" in user_msg or "last" in user_msg:
                        intent = "read_emails"
                        count = 5
                        # Try to extract number
                        import re
                        numbers = re.findall(r'\d+', prompt)
                        if numbers:
                            count = int(numbers[0])
                        return json.dumps({
                            "intent": intent,
                            "parameters": {"count": count, "sender": None, "subject_keyword": None, "email_reference": None},
                            "confidence": "high"
                        })
                    elif "reply" in user_msg:
                        return json.dumps({
                            "intent": "reply_to_email",
                            "parameters": {"count": None, "sender": None, "subject_keyword": None, "email_reference": "first"},
                            "confidence": "high"
                        })
                    elif "delete" in user_msg:
                        return json.dumps({
                            "intent": "delete_email",
                            "parameters": {"count": None, "sender": None, "subject_keyword": None, "email_reference": "first"},
                            "confidence": "high"
                        })
                    else:
                        return json.dumps({
                            "intent": "general",
                            "parameters": {"count": None, "sender": None, "subject_keyword": None, "email_reference": None},
                            "confidence": "medium"
                        })

                else:
                    # General chatbot response
                    return "I'm here to help you manage your emails. You can ask me to show your recent emails, reply to messages, or delete emails."

        except Exception as e:
            print(f"AI service error: {e}")
            raise Exception(f"Failed to generate AI response: {str(e)}")

