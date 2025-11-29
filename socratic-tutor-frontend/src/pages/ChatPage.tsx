import React, { useState, useEffect } from 'react';
import { MessageList } from '../components/chat/MessageList';
import { ChatInput } from '../components/chat/ChatInput';
import { Header } from '../components/layout/Header';
import { PreferencesDrawer } from '../components/layout/PreferencesDrawer';
import { TypingIndicator } from '../components/chat/TypingIndicator';
import { ChatSidebar } from '../components/chat/ChatSidebar';
import { Button } from '../components/ui/button';
import { Menu } from 'lucide-react';
import { 
  sendMessage, 
  getSessions, 
  getSessionMessages,
  Message,
  Preferences,
  SessionSummary,
  defaultPreferences
} from '../services/chatService';

type ChatSession = {
  id: string;
  title: string;
  createdAt: string;
  messages: Message[];
};

export const ChatPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingSessions, setIsLoadingSessions] = useState(false);
  const [preferencesOpen, setPreferencesOpen] = useState(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [preferences, setPreferences] = useState<Preferences>(defaultPreferences);
  const [error, setError] = useState<string | null>(null);

  // Initialize sessions from backend
  const [sessions, setSessions] = useState<ChatSession[]>([]);

  // Load sessions on component mount
  useEffect(() => {
    loadSessions();
  }, []);

  // Load session messages when active session changes
  useEffect(() => {
    if (activeSessionId) {
      loadSessionMessages(activeSessionId);
    }
  }, [activeSessionId]);

  const loadSessions = async () => {
    setIsLoadingSessions(true);
    try {
      const response = await getSessions();
      const chatSessions: ChatSession[] = response.sessions.map(summary => ({
        id: summary.id,
        title: summary.title,
        createdAt: summary.created_at,
        messages: [] // Will be loaded on demand
      }));
      setSessions(chatSessions);
      
      // Set first session as active if none selected
      if (!activeSessionId && chatSessions.length > 0) {
        setActiveSessionId(chatSessions[0].id);
      }
    } catch (error) {
      console.error('Error loading sessions:', error);
    } finally {
      setIsLoadingSessions(false);
    }
  };

  const loadSessionMessages = async (sessionId: string) => {
    try {
      const response = await getSessionMessages(sessionId);
      setSessions(prev => prev.map(session => 
        session.id === sessionId 
          ? { ...session, messages: response.messages }
          : session
      ));
    } catch (error) {
      console.error('Error loading session messages:', error);
    }
  };

  const handleNewChat = async () => {
    const newSession: ChatSession = {
      id: `temp-${Date.now()}`,
      title: 'New Chat',
      createdAt: new Date().toISOString(),
      messages: []
    };
    
    setSessions(prev => [newSession, ...prev]);
    setActiveSessionId(newSession.id);
    setMobileSidebarOpen(false);
  };

  const handleChatSelect = async (sessionId: string) => {
    setActiveSessionId(sessionId);
    setMobileSidebarOpen(false);
  };

  const handleSendMessage = async (userMessage: string) => {
    if (!activeSessionId) return;
    
    // Add user message immediately
    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: userMessage
    };
    
    setSessions(prev => prev.map(session => 
      session.id === activeSessionId 
        ? { 
            ...session, 
            messages: [...session.messages, userMsg],
            title: session.messages.length === 0 ? userMessage.substring(0, 30) + (userMessage.length > 30 ? '...' : '') : session.title
          }
        : session
    ));
    
    setIsLoading(true);

    try {
      // Get current session messages
      const currentSession = sessions.find(s => s.id === activeSessionId);
      const messages = currentSession ? [...currentSession.messages, userMsg] : [userMsg];
      
      // Send to backend
      const response = await sendMessage({
        messages,
        preferences,
        session_id: activeSessionId.startsWith('temp-') ? undefined : activeSessionId
      });
      
      const aiMsg: Message = {
        id: response.reply_message.id,
        role: 'assistant',
        content: response.reply_message.content,
        timestamp: response.reply_message.timestamp
      };
      
      // Update session with backend response and new session ID if this was a temp session
      setSessions(prev => prev.map(session => 
        session.id === activeSessionId 
          ? { 
              ...session, 
              id: response.session_id, // Update with real session ID from backend
              messages: [...session.messages, aiMsg]
            }
          : session
      ));
      
      // Update active session ID if this was a temp session
      if (activeSessionId.startsWith('temp-')) {
        setActiveSessionId(response.session_id);
      }
      
    } catch (error) {
      console.error('Error getting AI response:', error);
      // Add error message as AI response
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: error instanceof Error ? error.message : "I'm having trouble responding right now. Please try again."
      };
      
      setSessions(prev => prev.map(session => 
        session.id === activeSessionId 
          ? { 
              ...session, 
              messages: [...session.messages, errorMessage]
            }
          : session
      ));
    } finally {
      setIsLoading(false);
    }
  };

  const activeSession = sessions.find(s => s.id === activeSessionId);

  return (
    <div className="flex h-screen bg-background">
      {/* Left Sidebar */}
      <aside className="hidden md:flex md:w-72 bg-background border-r border-border flex-col h-full">
        <ChatSidebar 
          sessions={sessions}
          activeSessionId={activeSessionId}
          onChatSelect={handleChatSelect}
          onNewChat={handleNewChat}
          isLoading={isLoadingSessions}
        />
      </aside>
      
      {/* Right Main Area */}
      <main className="flex-1 flex flex-col min-w-0">
        <Header onOpenPreferences={() => setPreferencesOpen(true)} />
        <section className="flex-1 overflow-hidden flex flex-col p-4">
          {activeSession && activeSession.messages.length === 0 ? (
            <div className="flex-1 flex items-center justify-center text-muted-foreground">
              Start a conversation
            </div>
          ) : (
            <>
              <div className="flex-1 overflow-hidden">
                <MessageList messages={activeSession?.messages || []} />
              </div>
              {isLoading && <TypingIndicator />}
            </>
          )}
          <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
        </section>
      </main>

      {/* Mobile Sidebar Overlay */}
      {mobileSidebarOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div 
            className="absolute inset-0 bg-black/50" 
            onClick={() => setMobileSidebarOpen(false)}
          />
          <div className="absolute left-0 top-0 h-full w-72 bg-background">
            <ChatSidebar 
              sessions={sessions}
              activeSessionId={activeSessionId}
              onChatSelect={handleChatSelect}
              onNewChat={handleNewChat}
              isLoading={isLoadingSessions}
            />
          </div>
        </div>
      )}
      
      {/* Mobile Menu Button */}
      <Button
        variant="ghost"
        size="icon"
        onClick={() => setMobileSidebarOpen(true)}
        className="fixed bottom-6 left-6 z-40 md:hidden h-14 w-14 rounded-full shadow-lg"
        aria-label="Open chat menu"
      >
        <Menu className="h-6 w-6" />
      </Button>
      
      <PreferencesDrawer 
        open={preferencesOpen} 
        onOpenChange={setPreferencesOpen}
        preferences={preferences}
        onPreferencesChange={setPreferences}
      />
    </div>
  );
};
