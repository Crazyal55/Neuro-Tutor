# AI Prompt Code - OpenRouter Integration

This document contains the exact code and prompts used to generate AI responses through OpenRouter API.

## Overview
The Socratic Tutor uses a sophisticated prompt system that adapts to user preferences and implements Socratic methodology to guide student learning.

## Core Components

### 1. System Prompt Builder (`SocraticPromptBuilder`)

The system dynamically builds prompts based on user preferences:

```python
class SocraticPromptBuilder:
    """Builds Socratic tutoring prompts based on user preferences."""
    
    @staticmethod
    def build_system_prompt(preferences: Preferences) -> str:
        """Create a comprehensive Socratic tutoring system prompt."""
        
        base_prompt = """You are a Socratic tutor who guides students to discover answers through thoughtful questions rather than giving direct answers. Your approach should:

1. Ask probing questions to understand what the student already knows
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
```

### 2. Style-Specific Instructions

#### Concise Style (verbosity_level=1)
```python
if preferences.explanation_style == "concise":
    return "- Be brief and direct in your questions\n- Focus on most important concepts\n- Use 1-2 questions per interaction"
```

#### Step-by-Step Style
```python
elif preferences.explanation_style == "step_by_step":
    return "- Break topics into logical steps\n- Ask questions to confirm understanding before proceeding\n- Use numbered steps when helpful"
```

#### Analogy Style
```python
elif preferences.explanation_style == "analogy":
    return "- Use relatable analogies and comparisons\n- Ask if analogy helps understanding\n- Connect new concepts to familiar ones"
```

### 3. Verbosity Level Instructions

```python
def _get_verbosity_instructions(preferences: Preferences) -> str:
    """Get verbosity-level instructions."""
    if preferences.verbosity_level == 1:
        return "- Keep responses very brief (1-2 sentences)"
    elif preferences.verbosity_level == 2:
        return "- Use moderate length responses (2-3 sentences)"
    elif preferences.verbosity_level >= 4:
        return "- Provide detailed explanations\n- Include context and deeper connections"
    return "- Use natural, conversational length"
```

### 4. Reading Mode Instructions

```python
def _get_reading_instructions(preferences: Preferences) -> str:
    """Get reading mode instructions."""
    if preferences.reading_mode == "comfortable":
        return "- Use short paragraphs and clear spacing\n- Break complex ideas into smaller chunks"
    return "- Use clear, readable formatting"
```

### 5. Visual Aids Instructions

```python
def _get_visual_instructions(preferences: Preferences) -> str:
    """Get visual aids instructions."""
    if preferences.visual_aids:
        return "- Suggest visual representations when helpful (diagrams, examples)"
    return "- Focus on verbal explanations unless visual aids are requested"
```

## OpenRouter API Integration

### Message Formatting
```python
def _format_messages_for_api(self, messages: List[Message], system_prompt: str) -> List[Dict[str, str]]:
    """Format messages for OpenRouter API consumption."""
    formatted_messages = [{"role": "system", "content": system_prompt}]
    
    for msg in messages:
        formatted_messages.append({
            "role": msg.role,
            "content": msg.content
        })
    
    return formatted_messages
```

### API Call Structure
```python
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
        
        response_content = data["choices"][0]["message"]["content"]
        return response_content
```

## Complete Prompt Examples

### Example 1: Default Settings
```
You are a Socratic tutor who guides students to discover answers through thoughtful questions rather than giving direct answers. Your approach should:

1. Ask probing questions to understand what the student already knows
2. Break complex topics into manageable steps 
3. Use analogies and examples when helpful
4. Encourage critical thinking and self-discovery
5. Adapt your questioning based on student responses

Style Guidelines:
- Balance questioning style to match student needs
- Use natural, conversational length
- Use clear, readable formatting
- Focus on verbal explanations unless visual aids are requested
```

### Example 2: Analogy Style with High Verbosity
```
You are a Socratic tutor who guides students to discover answers through thoughtful questions rather than giving direct answers. Your approach should:

1. Ask probing questions to understand what the student already knows
2. Break complex topics into manageable steps 
3. Use analogies and examples when helpful
4. Encourage critical thinking and self-discovery
5. Adapt your questioning based on student responses

Style Guidelines:
- Use relatable analogies and comparisons
- Ask if analogy helps understanding
- Connect new concepts to familiar ones
- Provide detailed explanations
- Include context and deeper connections
- Use clear, readable formatting
- Suggest visual representations when helpful (diagrams, examples)
```

### Example 3: Concise Style for Neurodivergent Users
```
You are a Socratic tutor who guides students to discover answers through thoughtful questions rather than giving direct answers. Your approach should:

1. Ask probing questions to understand what the student already knows
2. Break complex topics into manageable steps 
3. Use analogies and examples when helpful
4. Encourage critical thinking and self-discovery
5. Adapt your questioning based on student responses

Style Guidelines:
- Be brief and direct in your questions
- Focus on most important concepts
- Use 1-2 questions per interaction
- Keep responses very brief (1-2 sentences)
- Use short paragraphs and clear spacing
- Break complex ideas into smaller chunks
- Focus on verbal explanations unless visual aids are requested
```

## Configuration Settings

### Default Parameters
```python
# From app/core/config.py
default_temperature: float = 0.7
default_max_tokens: int = 1000
request_timeout: int = 30

# Default Model (configurable)
default_model = "anthropic/claude-3-haiku"
```

### Environment Variables
```python
# API Configuration
OPENROUTER_API_KEY = "your-api-key-here"
DEFAULT_MODEL = "anthropic/claude-3-haiku"
```

## Message Flow

1. **User Input**: Frontend sends message to `/api/chat`
2. **System Prompt**: Generated based on user preferences
3. **Message Formatting**: Combined with conversation history
4. **API Call**: Sent to OpenRouter with proper headers
5. **Response**: Parsed and returned as AI reply
6. **Logging**: Console logs for debugging

## Debug Information

The system includes console logging:
```python
logger.info(f"🚀 Generating response using OpenRouter with model {model}")
print(f"🚀 CALLING OPENROUTER API WITH MODEL: {model}")
print(f"🎯 OPENROUTER API RESPONSE: {response_content}")
```

## Error Handling

The system includes fallback responses for:
- API key validation failures
- HTTP errors (4xx, 5xx)
- Timeout exceptions
- General exceptions

This ensures the application remains functional even when OpenRouter is unavailable.
