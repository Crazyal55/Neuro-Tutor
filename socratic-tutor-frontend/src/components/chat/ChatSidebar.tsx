import React from 'react';
import { Button } from '../ui/button';
import { ScrollArea } from '../ui/scroll-area';
import { MessageSquare, Plus } from 'lucide-react';

type Message = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
};

type ChatSession = {
  id: string;
  title: string;
  createdAt: string;
  messages: Message[];
};

interface ChatSidebarProps {
  sessions: ChatSession[];
  activeSessionId: string | null;
  onChatSelect: (chatId: string) => void;
  onNewChat: () => void;
  isLoading?: boolean;
}

const formatLastActive = (createdAt: string) => {
  const date = new Date(createdAt);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
};

export const ChatSidebar: React.FC<ChatSidebarProps> = ({ 
  sessions, 
  activeSessionId,
  onChatSelect, 
  onNewChat,
  isLoading
}) => {
  return (
    <div className="flex flex-col h-full">
      {/* New Chat Button */}
      <div className="p-4 border-b border-border flex-shrink-0">
        <Button 
          onClick={onNewChat}
          className="w-full justify-start gap-2"
          variant="outline"
        >
          <Plus className="h-4 w-4" />
          New Chat
        </Button>
      </div>

      {/* Chat List */}
      <ScrollArea className="flex-1 p-4">
        {isLoading ? (
          <div className="flex items-center justify-center h-32">
            <div className="text-sm text-muted-foreground">Loading chats...</div>
          </div>
        ) : (
          <div className="space-y-2 flex flex-col">
            {sessions.map((session) => (
              <Button
                key={session.id}
                onClick={() => onChatSelect(session.id)}
                variant={session.id === activeSessionId ? "secondary" : "ghost"}
                className="w-full justify-start p-3 h-auto text-left rounded-lg hover:bg-accent/50 hover:shadow-md transition-all duration-200"
              >
                <div className="flex items-center gap-3 w-full">
                  <MessageSquare className="h-4 w-4 flex-shrink-0 text-black dark:text-white" />
                  <div className="flex-1 min-w-0">
                    <div className="font-medium truncate text-black dark:text-white">{session.title}</div>
                    <div className="text-xs text-gray-600 dark:text-gray-400">{formatLastActive(session.createdAt)}</div>
                  </div>
                </div>
              </Button>
            ))}
          </div>
        )}
      </ScrollArea>
    </div>
  );
};
