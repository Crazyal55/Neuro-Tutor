/**
 * Chat service for communicating with Neuro Tutor backend.
 */

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
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
}

export interface ChatResponse {
  session_id: string;
  reply_message: Message;
}

export interface SessionSummary {
  id: string;
  title: string;
  created_at: string;
  last_updated_at: string;
  message_count: number;
}

export interface SessionListResponse {
  sessions: SessionSummary[];
}

export interface SessionMessagesResponse {
  session_id: string;
  messages: Message[];
}

/**
 * Send a message to chat API
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
