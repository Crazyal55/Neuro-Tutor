/**
 * Chat service for communicating with Neuro Tutor backend.
 */

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api';

export interface SourceCitation {
  filename: string;
  locator: string;
  score: number;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  sources?: SourceCitation[];
}

export interface Preferences {
  verbosity_level: number;
  explanation_style: 'concise' | 'step_by_step' | 'analogy';
  reading_mode: 'compact' | 'comfortable';
  visual_aids: boolean;
}

export interface ChatRequest {
  messages: Message[];
  preferences?: Preferences;
  session_id?: string;
  subject_id?: string | null;
}

export interface ChatResponse {
  session_id: string;
  reply_message: Message;
  sources?: SourceCitation[];
}

export interface ChatStreamHandlers {
  onToken: (token: string) => void;
  onDone: (response: ChatResponse) => void;
  onError: (error: Error) => void;
}

export interface SessionSummary {
  id: string;
  title: string;
  created_at: string;
  last_updated_at: string;
  message_count: number;
  last_message_preview?: string | null;
  subject_id?: string | null;
}

export interface SessionListResponse {
  sessions: SessionSummary[];
}

export interface SessionMessagesResponse {
  session_id: string;
  messages: Message[];
}

/**
 * Send a message to chat API (non-streaming fallback)
 */
export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error sending message:', error);
    if (error instanceof Error) {
      throw new Error(getUserFriendlyErrorMessage(error));
    }
    throw error;
  }
}

/**
 * Stream a chat response via Server-Sent Events
 */
export async function sendMessageStream(
  request: ChatRequest,
  handlers: ChatStreamHandlers,
): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'text/event-stream',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    if (!response.body) {
      throw new Error('Streaming is not supported in this browser.');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const events = buffer.split('\n\n');
      buffer = events.pop() || '';

      for (const eventBlock of events) {
        const dataLine = eventBlock
          .split('\n')
          .find((line) => line.startsWith('data: '));

        if (!dataLine) {
          continue;
        }

        const payload = JSON.parse(dataLine.slice(6)) as {
          type: string;
          content?: string;
          session_id?: string;
          reply_message?: Message;
          sources?: SourceCitation[];
          detail?: string;
        };

        if (payload.type === 'token' && payload.content) {
          handlers.onToken(payload.content);
        } else if (payload.type === 'done' && payload.session_id && payload.reply_message) {
          handlers.onDone({
            session_id: payload.session_id,
            reply_message: {
              ...payload.reply_message,
              sources: payload.sources,
            },
            sources: payload.sources,
          });
        } else if (payload.type === 'error') {
          throw new Error(payload.detail || 'Streaming failed');
        }
      }
    }
  } catch (error) {
    console.error('Error streaming message:', error);
    if (error instanceof Error) {
      handlers.onError(new Error(getUserFriendlyErrorMessage(error)));
      return;
    }
    handlers.onError(new Error('Streaming failed unexpectedly.'));
  }
}

/**
 * Get all chat sessions
 */
export async function getSessions(): Promise<SessionListResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/sessions`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching sessions:', error);
    throw error;
  }
}

/**
 * Get messages for a specific session
 */
export async function getSessionMessages(sessionId: string): Promise<SessionMessagesResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}/messages`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching session messages:', error);
    throw error;
  }
}

/**
 * Delete a session
 */
export async function deleteSession(sessionId: string): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}`, {
      method: 'DELETE',
    });
    
    if (!response.ok && response.status !== 204) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
  } catch (error) {
    console.error('Error deleting session:', error);
    throw error;
  }
}

/**
 * Rename a session
 */
export async function updateSessionTitle(
  sessionId: string,
  title: string,
): Promise<SessionSummary> {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ title }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error updating session title:', error);
    throw error;
  }
}

/**
 * Convert technical errors to user-friendly messages
 */
function getUserFriendlyErrorMessage(error: Error): string {
  const message = error.message.toLowerCase();
  
  if (message.includes('network') || message.includes('fetch')) {
    return "I'm having trouble connecting to my brain right now. Please check your internet connection and try again.";
  }
  
  if (message.includes('timeout')) {
    return "I'm thinking a bit too slowly right now. Let me try that again - could you please resend your message?";
  }
  
  if (message.includes('500') || message.includes('internal server error')) {
    return "I seem to have hit a mental roadblock. Let's try that question again in a different way.";
  }
  
  if (message.includes('429') || message.includes('rate limit')) {
    return "Whoa, slow down there! My brain needs a moment to catch up. Let's try again in a few seconds.";
  }
  
  if (message.includes('401') || message.includes('unauthorized')) {
    return "I seem to have lost my connection to the knowledge network. Please let me know if this keeps happening.";
  }
  
  if (message.includes('404') || message.includes('not found')) {
    return "I can't seem to find what I'm looking for. Could we try starting a new conversation?";
  }
  
  if (message.includes('400') || message.includes('bad request')) {
    return "I'm not quite sure what you're asking. Could you try phrasing that differently?";
  }
  
  // Generic fallback
  return "I'm having a bit of trouble processing that right now. Could you try asking in a different way, or let's start fresh with a new question?";
}

/**
 * Default preferences
 */
export const defaultPreferences: Preferences = {
  verbosity_level: 3,
  explanation_style: 'step_by_step',
  reading_mode: 'comfortable',
  visual_aids: true,
};
