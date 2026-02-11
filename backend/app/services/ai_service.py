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

    def categorize_email(self, email_body: str, subject: str) -> dict:
        """Categorize email and detect priority level."""
        prompt = f"""Analyze this email and provide:
1. Category (Work, Personal, Promotions, Important, Spam)
2. Priority (High, Medium, Low)
3. Action needed (Reply, Read, Archive, Delete)

Subject: {subject}
Content: {email_body[:1000]}

Respond in format: Category|Priority|Action"""
        
        try:
            response = self._generate_completion(prompt, max_tokens=50)
            parts = response.split('|')
            if len(parts) >= 3:
                return {
                    "category": parts[0].strip(),
                    "priority": parts[1].strip(), 
                    "action": parts[2].strip()
                }
        except:
            pass
            
        # Fallback categorization
        subject_lower = subject.lower()
        body_lower = email_body.lower()
        
        if any(word in subject_lower + body_lower for word in ["urgent", "asap", "deadline", "important"]):
            priority = "High"
        elif any(word in subject_lower + body_lower for word in ["meeting", "project", "work", "business"]):
            priority = "Medium"  
        else:
            priority = "Low"
            
        if any(word in subject_lower for word in ["promotion", "sale", "offer", "discount"]):
            category = "Promotions"
        elif any(word in subject_lower + body_lower for word in ["work", "project", "meeting", "business"]):
            category = "Work"
        else:
            category = "Personal"
            
        return {"category": category, "priority": priority, "action": "Read"}

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

    def generate_email_template(self, template_type: str, context: dict = None) -> str:
        """Generate email templates for common scenarios."""
        templates = {
            "thank_you": "Thank you for your email. I appreciate you reaching out and will review your message carefully.",
            "follow_up": "I wanted to follow up on our previous conversation regarding {topic}. Please let me know if you have any updates.",
            "meeting_request": "I hope this email finds you well. I would like to schedule a meeting to discuss {topic}. Are you available {time}?",
            "out_of_office": "Thank you for your email. I am currently out of the office and will respond to your message when I return on {return_date}.",
            "acknowledgment": "I have received your email regarding {topic} and will get back to you within {timeframe}."
        }
        
        if template_type in templates:
            template = templates[template_type]
            if context:
                try:
                    return template.format(**context)
                except:
                    pass
            return template
            
        # Generate custom template with AI
        prompt = f"""Generate a professional email template for: {template_type}
Make it polite, concise, and professional."""
        return self._generate_completion(prompt, max_tokens=200)

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
        if any(kw in msg_lower for kw in ["show", "read", "get", "fetch", "last", "recent", "email", "emails", "inbox"]):
            intent = "read_emails"
            if not count:
                count = 5

        # Check for reply intent
        elif any(kw in msg_lower for kw in ["reply", "respond", "answer", "write back"]):
            intent = "reply_to_email"

        # Check for delete intent  
        elif any(kw in msg_lower for kw in ["delete", "remove", "trash", "clear"]):
            intent = "delete_email"
            
        # Check for search intent
        elif any(kw in msg_lower for kw in ["search", "find", "look for", "filter"]):
            intent = "search_emails"
            
        # Check for organize/categorize intent
        elif any(kw in msg_lower for kw in ["organize", "sort", "categorize", "label", "priority"]):
            intent = "organize_emails"
            
        # Check for bulk operations
        elif any(kw in msg_lower for kw in ["all", "bulk", "multiple", "mass"]):
            intent = "bulk_operation"
            
        # Check for templates
        elif any(kw in msg_lower for kw in ["template", "draft", "compose"]):
            intent = "email_template"
            
        # Check for unread emails  
        elif "unread" in msg_lower:
            intent = "read_emails"
            count = None  # Get all unread
            
        # Check for important emails
        elif any(kw in msg_lower for kw in ["important", "urgent", "priority"]):
            intent = "priority_emails"

        return {
            "intent": intent,
            "parameters": {
                "count": count,
                "sender": self._extract_sender(user_message),
                "subject_keyword": self._extract_subject_keyword(user_message),
                "email_reference": None,
                "filter_type": self._extract_filter_type(user_message)
            },
            "confidence": "high"
        }
        
    def _extract_sender(self, message: str) -> Optional[str]:
        """Extract sender information from user message."""
        import re
        # Look for "from [name/email]" patterns
        patterns = [
            r'from\s+([\w\s@.]+)',
            r'by\s+([\w\s@.]+)',
            r'sender\s+([\w\s@.]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message.lower())
            if match:
                return match.group(1).strip()
        return None
        
    def _extract_subject_keyword(self, message: str) -> Optional[str]:
        """Extract subject keywords from user message."""
        import re
        patterns = [
            r'subject\s+["\']([^"\']+)["\']',
            r'about\s+["\']([^"\']+)["\']',
            r'regarding\s+([\w\s]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message.lower())
            if match:
                return match.group(1).strip()
        return None
        
    def _extract_filter_type(self, message: str) -> Optional[str]:
        """Extract filter type from user message."""
        msg_lower = message.lower()
        if "unread" in msg_lower:
            return "unread"
        elif any(kw in msg_lower for kw in ["important", "urgent", "priority"]):
            return "important"
        elif "spam" in msg_lower:
            return "spam"
        elif "promotions" in msg_lower:
            return "promotions"
        return None

    def generate_chatbot_response(
        self, user_message: str, context: Optional[str] = None
    ) -> str:
        """Generate a conversational response for the chatbot."""
        # Handle simple greetings and casual questions directly
        user_lower = user_message.lower().strip()
        
        # Basic greetings
        if user_lower in ["hi", "hii", "hello", "hey", "greetings"]:
            return "Hello! 👋 I'm your AI email assistant. I can help you manage your Gmail inbox with reading, replying, deleting, and searching emails. What would you like to do?"
        
        # Casual questions with friendly responses but clear boundaries
        if user_lower in ["how are you", "how are u", "how r u", "how's it going"]:
            return "I'm doing great, thanks for asking! 😊 I'm here and ready to help you manage your emails. Want to check your inbox or do something with your emails?"
        
        if user_lower in ["what's up", "whats up", "sup"]:
            return "Not much, just waiting to help you with your emails! 📧 What would you like to do - check recent emails, reply to someone, or search for something specific?"
        
        # Check for non-email related queries and redirect firmly
        non_email_keywords = [
            "homework", "assignment", "study", "learn", "teach", "explain", "definition", 
            "calculate", "solve", "math", "physics", "chemistry", "biology", "history",
            "weather", "news", "joke", "story", "recipe", "cooking", "travel", "movie",
            "music", "game", "sports", "politics", "health", "medical", "diagnosis",
            "programming", "code", "python", "javascript", "html", "css", "database",
            "what is", "how to", "tell me about", "can you help me with", "i need help with"
        ]
        
        if any(keyword in user_lower for keyword in non_email_keywords):
            return "I'm specifically designed as an AI Email Assistant for Gmail management only. I can help you with:\n\n📧 Reading emails\n✍️ Replying to emails\n🗑️ Deleting emails\n🔍 Searching emails\n📋 Organizing emails\n\nFor other topics, please use a general AI assistant. What would you like to do with your emails?"
        
        context_text = f"\n\nContext: {context}" if context else ""
        prompt = f"""You are STRICTLY an email assistant for Gmail management only. Do not help with any non-email topics.

If the user asks about anything other than email management (homework, general questions, explanations, etc.), respond with:
"I'm specifically designed as an AI Email Assistant for Gmail management only. I can help you read, reply to, delete, search, and organize your emails. For other topics, please use a general AI assistant. What would you like to do with your emails?"

Only help with: reading emails, replying to emails, deleting emails, searching emails, organizing emails.

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
        # Check for greeting in prompt
        if any(greeting in prompt.lower() for greeting in ["hi", "hello", "hey", "hii", "greetings"]):
            return "Hello! 👋 I'm your AI email assistant. I can help you manage your Gmail inbox. What would you like to do?"
        
        if "summarize" in prompt.lower():
            return "This email contains important information. Please review the full content."

        # Only use formal reply template for actual email reply generation, not chat
        if "reply" in prompt.lower() and "email" in prompt.lower() and "generate" in prompt.lower():
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

        # For general questions (including off-topic ones)
        if any(kw in prompt.lower() for kw in ["what is", "how to", "tell me", "explain"]):
            return "I'm an email assistant focused on helping you manage your Gmail. I can help you read, reply to, delete, search, organize, and categorize your emails. What would you like to do with your emails?"
        
        return "I'm here to help with your emails. I can:\n• Read recent/unread emails\n• Reply with AI assistance\n• Delete unwanted emails\n• Search and filter emails\n• Organize by priority/category\n• Generate email templates\n\nWhat would you like to do?"

