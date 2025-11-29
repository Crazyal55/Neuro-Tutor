"""
LLM client service for Neuro Tutor.

Implements OpenRouter integration for real AI responses.
Uses Socratic methodology to guide student learning.
"""

import logging
import asyncio
from datetime import datetime
from typing import List, Dict
import uuid
import httpx

from app.models.chat import Message, Preferences
from app.core.config import settings
from app.core.openrouter_secrets import get_openrouter_api_key, get_default_model

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SocraticPromptBuilder:
    """Builds Socratic tutoring prompts based on user preferences."""
    
    @staticmethod
    def build_system_prompt(preferences: Preferences) -> str:
        """Create a comprehensive Socratic tutoring system prompt."""
        
        base_prompt = """You are a Socratic tutor who guides students to discover answers through thoughtful questions rather than giving direct answers. Your approach should:

1. Ask probing questions to understand what of student already knows
2. Break complex topics into manageable steps 
3. Use analogies and examples when helpful
4. Encourage critical thinking and self-discovery
5. Adapt your questioning based on student responses

Style Guidelines:"""
        
        # Add style-specific instructions
        style_instructions = SocraticPromptBuilder._get_style_instructions(preferences)
        verbosity_instructions = SocraticPromptBuilder._get_verbosity_instructions(preferences)
        reading_instructions = SocraticPromptBuilder._get_reading_instructions(preferences)
        visual_instructions = SocraticPromptBuilder._get_visual_instructions(preferences)
        
        return f"{base_prompt}\n{style_instructions}\n{verbosity_instructions}\n{reading_instructions}\n{visual_instructions}"
    
    @staticmethod
    def _get_style_instructions(preferences: Preferences) -> str:
        """Get style-specific instructions."""
        if preferences.explanation_style == "concise":
            return "- Be brief and direct in your questions\n- Focus on most important concepts\n- Use 1-2 questions per interaction"
        elif preferences.explanation_style == "step_by_step":
            return "- Break topics into logical steps\n- Ask questions to confirm understanding before proceeding\n- Use numbered steps when helpful"
        elif preferences.explanation_style == "analogy":
            return "- Use relatable analogies and comparisons\n- Ask if analogy helps understanding\n- Connect new concepts to familiar ones"
        return "- Balance questioning style to match student needs"
    
    @staticmethod
    def _get_verbosity_instructions(preferences: Preferences) -> str:
        """Get verbosity-level instructions."""
        if preferences.verbosity_level == 1:
            return "- Keep responses very brief (1-2 sentences)"
        elif preferences.verbosity_level == 2:
            return "- Use moderate length responses (2-3 sentences)"
        elif preferences.verbosity_level >= 4:
            return "- Provide detailed explanations\n- Include context and deeper connections"
        return "- Use natural, conversational length"
    
    @staticmethod
    def _get_reading_instructions(preferences: Preferences) -> str:
        """Get reading mode instructions."""
        if preferences.reading_mode == "comfortable":
            return "- Use short paragraphs and clear spacing\n- Break complex ideas into smaller chunks"
        return "- Use clear, readable formatting"
    
    @staticmethod
    def _get_visual_instructions(preferences: Preferences) -> str:
        """Get visual aids instructions."""
        if preferences.visual_aids:
            return "- Suggest visual representations when helpful (diagrams, examples)"
        return "- Focus on verbal explanations unless visual aids are requested"


class OpenRouterClient:
    """Client for interacting with OpenRouter API."""
    
    def __init__(self):
        self.api_key = get_openrouter_api_key()
        self.base_url = "https://openrouter.ai/api/v1"
        self.default_model = get_default_model()
        self.default_temperature = settings.default_temperature
        self.default_max_tokens = settings.default_max_tokens
    
    def _validate_api_key(self) -> bool:
        """Validate that API key is properly configured."""
        return (
            self.api_key and 
            self.api_key != "YOUR_OPENROUTER_API_KEY_HERE" and
            self.api_key != "your-openrouter-api-key-here"
        )
    
    def _format_messages_for_api(self, messages: List[Message], system_prompt: str) -> List[Dict[str, str]]:
        """Format messages for OpenRouter API consumption."""
        formatted_messages = [{"role": "system", "content": system_prompt}]
        
        for msg in messages:
            formatted_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        return formatted_messages
    
    async def _call_openrouter_api(self, messages: List[Dict], model: str, temperature: float, max_tokens: int) -> str:
        """Call OpenRouter API and return response content."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://neurotutor.local",
            "X-Title": "NeuroTutor-Dev"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            # CONSOLE LOG: Log OpenRouter response for debugging
            response_content = data["choices"][0]["message"]["content"]
            logger.info(f"🎯 OPENROUTER RESPONSE: {response_content[:100]}...")
            print(f"🎯 OPENROUTER API RESPONSE: {response_content}")
            
            return response_content
    
    async def generate_response(self, messages: List[Message], preferences: Preferences, session_id: str = None):
        """
        Generate a Socratic response using OpenRouter API.
        
        Args:
            messages: List of previous messages in the conversation
            preferences: User preferences for response style
            session_id: Optional session identifier
            
        Returns:
            Dict containing reply_message and session_id
        """
        try:
            # Validate API key
            if not self._validate_api_key():
                logger.warning("OpenRouter API key not properly configured, using fallback")
                return self._create_fallback_response("Please configure your OpenRouter API key to use AI tutoring.", session_id)
            
            # Use default preferences if not provided
            if not preferences:
                preferences = Preferences()
            
            # Build Socratic system prompt
            system_prompt = SocraticPromptBuilder.build_system_prompt(preferences)
            
            # Format messages for API
            formatted_messages = self._format_messages_for_api(messages, system_prompt)
            
            # Determine model and parameters
            model = getattr(preferences, 'model', self.default_model) or self.default_model
            temperature = getattr(preferences, 'temperature', self.default_temperature) or self.default_temperature
            
            logger.info(f"🚀 Generating response using OpenRouter with model {model}")
            print(f"🚀 CALLING OPENROUTER API WITH MODEL: {model}")
            
            # Call OpenRouter API
            response_content = await self._call_openrouter_api(
                formatted_messages, 
                model, 
                temperature, 
                self.default_max_tokens
            )
            
            # Create response message
            reply_message = Message(
                id=str(uuid.uuid4()),
                role="assistant",
                content=response_content,
                timestamp=datetime.utcnow()
            )
            
            logger.info(f"✅ Generated response successfully for session {session_id}")
            print(f"✅ SUCCESSFULLY GENERATED REAL OPENROUTER RESPONSE")
            
            return {
                "reply_message": reply_message,
                "session_id": session_id or str(uuid.uuid4())
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenRouter HTTP error: {e.response.status_code} - {e.response.text}")
            return self._create_fallback_response("I'm having trouble connecting to the AI service. Let me help you with a different approach.", session_id)
        except httpx.TimeoutException:
            logger.error("OpenRouter API timeout")
            return self._create_fallback_response("The connection timed out. Let's try a more focused question.", session_id)
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return self._create_fallback_response("I'm experiencing technical difficulties. How can I help you with a simpler question?", session_id)
    
    def _create_fallback_response(self, message: str, session_id: str) -> Dict:
        """Create a fallback response when API calls fail."""
        fallback_message = Message(
            id=str(uuid.uuid4()),
            role="assistant",
            content=message,
            timestamp=datetime.utcnow()
        )
        
        return {
            "reply_message": fallback_message,
            "session_id": session_id or str(uuid.uuid4())
        }


# Global OpenRouter client instance
llm_client = OpenRouterClient()


async def generate_response(messages: List[Message], preferences: Preferences = None, session_id: str = None):
    """
    Generate a reply to user's message using Socratic methodology with OpenRouter.
    
    Args:
        messages: List of previous messages in the conversation
        preferences: User preferences for response style
        session_id: Optional session identifier
        
    Returns:
        Dict containing reply_message and session_id
    """
    return await llm_client.generate_response(messages, preferences, session_id)


def create_message(role: str, content: str) -> Message:
    """Create a new message with timestamp."""
    return Message(
        id=str(uuid.uuid4()),
        role=role,
        content=content,
        timestamp=datetime.utcnow()
    )
