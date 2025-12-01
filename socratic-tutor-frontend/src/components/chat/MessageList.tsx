import React, { useEffect, useRef } from 'react';
import { MessageBubble } from './MessageBubble';
import { ScrollArea } from '../ui/scroll-area';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

interface MessageListProps {
  messages: Message[];
}

export const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  const chatRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    const element = chatRef.current;
    if (element) element.scrollTop = element.scrollHeight;
  }, [messages]);

  return (
    <ScrollArea ref={chatRef} className="flex-1 px-6 py-6">
      <div className="space-y-4 max-w-3xl mx-auto">
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            role={message.role}
            content={message.content}
          />
        ))}
      </div>
    </ScrollArea>
  );
};
