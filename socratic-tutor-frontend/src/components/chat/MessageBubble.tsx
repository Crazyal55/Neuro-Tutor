import React from 'react';
import { cn } from '../../lib/utils';

interface MessageBubbleProps {
  role: 'user' | 'assistant';
  content: string;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ role, content }) => {
  const isUser = role === 'user';
  
  return (
    <div
      className={cn(
        "flex w-full mb-4 transition-all duration-300 ease-in-out",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      <div
        className={cn(
          "max-w-xs lg:max-w-md px-5 py-4 rounded-2xl text-sm leading-relaxed transition-all duration-200 hover:shadow-md",
          isUser
            ? "bg-blue-500 text-white rounded-br-sm shadow-sm hover:bg-blue-600"
            : "bg-card text-foreground rounded-bl-sm border border-border shadow-sm hover:shadow-lg"
        )}
      >
        {content}
      </div>
    </div>
  );
};
