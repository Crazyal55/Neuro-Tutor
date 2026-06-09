import type { Message } from '../services/chatService';

export interface ChatSession {
  id: string;
  title: string;
  createdAt: string;
  lastUpdatedAt?: string;
  lastMessagePreview?: string | null;
  subjectId?: string | null;
  messages: Message[];
}

export function createTempSession(): ChatSession {
  return {
    id: `temp-${Date.now()}`,
    title: 'New Chat',
    createdAt: new Date().toISOString(),
    subjectId: null,
    messages: [],
  };
}
