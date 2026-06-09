import React from 'react';
import { Button } from '../ui/button';
import { ScrollArea } from '../ui/scroll-area';
import { MessageSquare, Pencil, Plus, Trash2 } from 'lucide-react';
import type { ChatSession } from '../../types/chat';

interface ChatSidebarProps {
  sessions: ChatSession[];
  activeSessionId: string | null;
  onChatSelect: (chatId: string) => void;
  onNewChat: () => void;
  onDeleteSession: (sessionId: string) => void;
  onRenameSession: (sessionId: string, title: string) => void;
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
  onDeleteSession,
  onRenameSession,
  isLoading,
}) => {
  const handleRename = (session: ChatSession, event: React.MouseEvent) => {
    event.stopPropagation();
    const nextTitle = window.prompt('Rename chat', session.title);
    if (nextTitle?.trim()) {
      onRenameSession(session.id, nextTitle.trim());
    }
  };

  const handleDelete = (sessionId: string, event: React.MouseEvent) => {
    event.stopPropagation();
    if (window.confirm('Delete this chat? This cannot be undone.')) {
      onDeleteSession(sessionId);
    }
  };

  return (
    <div className="flex flex-col h-full">
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

      <ScrollArea className="flex-1 p-4">
        {isLoading ? (
          <div className="flex items-center justify-center h-32">
            <div className="text-sm text-muted-foreground">Loading chats...</div>
          </div>
        ) : (
          <div className="space-y-2 flex flex-col">
            {sessions.map((session) => (
              <div
                key={session.id}
                className={`group flex items-stretch rounded-lg transition-all duration-200 ${
                  session.id === activeSessionId ? 'bg-secondary' : 'hover:bg-accent/50'
                }`}
              >
                <button
                  type="button"
                  onClick={() => onChatSelect(session.id)}
                  className="flex-1 min-w-0 p-3 text-left"
                >
                  <div className="flex items-start gap-3 w-full">
                    <MessageSquare className="h-4 w-4 flex-shrink-0 text-foreground mt-0.5" />
                    <div className="flex-1 min-w-0">
                      <div className="font-medium truncate text-foreground">{session.title}</div>
                      {session.lastMessagePreview ? (
                        <div className="text-xs text-muted-foreground truncate">
                          {session.lastMessagePreview}
                        </div>
                      ) : null}
                      <div className="text-xs text-muted-foreground">
                        {formatLastActive(session.lastUpdatedAt || session.createdAt)}
                      </div>
                    </div>
                  </div>
                </button>
                <div className="flex items-center gap-1 pr-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    aria-label={`Rename ${session.title}`}
                    onClick={(event) => handleRename(session, event)}
                  >
                    <Pencil className="h-3.5 w-3.5" />
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-destructive hover:text-destructive"
                    aria-label={`Delete ${session.title}`}
                    onClick={(event) => handleDelete(session.id, event)}
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </ScrollArea>
    </div>
  );
};
