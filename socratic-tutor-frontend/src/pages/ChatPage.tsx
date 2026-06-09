import React, { useCallback, useEffect, useState } from 'react';
import { MessageList } from '../components/chat/MessageList';
import { ChatInput } from '../components/chat/ChatInput';
import { Header } from '../components/layout/Header';
import { PreferencesDrawer } from '../components/layout/PreferencesDrawer';
import { ErrorBanner } from '../components/layout/ErrorBanner';
import { ChatSidebar } from '../components/chat/ChatSidebar';
import { MaterialsDrawer } from '../components/layout/MaterialsDrawer';
import { Button } from '../components/ui/button';
import { Menu } from 'lucide-react';
import {
  sendMessageStream,
  getSessions,
  getSessionMessages,
  deleteSession,
  updateSessionTitle,
  type Message,
  type Preferences,
  type SessionSummary,
} from '../services/chatService';
import { loadPreferences, savePreferences } from '../lib/preferencesStorage';
import { getSubjects, type SubjectSummary } from '../services/subjectService';
import { ChatSession, createTempSession } from '../types/chat';

function mapSessionSummary(summary: SessionSummary): ChatSession {
  return {
    id: summary.id,
    title: summary.title,
    createdAt: summary.created_at,
    lastUpdatedAt: summary.last_updated_at,
    lastMessagePreview: summary.last_message_preview,
    subjectId: summary.subject_id ?? null,
    messages: [],
  };
}

export const ChatPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingSessions, setIsLoadingSessions] = useState(false);
  const [preferencesOpen, setPreferencesOpen] = useState(false);
  const [materialsOpen, setMaterialsOpen] = useState(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [preferences, setPreferences] = useState<Preferences>(() => loadPreferences());
  const [error, setError] = useState<string | null>(null);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [subjects, setSubjects] = useState<SubjectSummary[]>([]);

  const createAndSelectTempSession = useCallback(() => {
    const newSession = createTempSession();
    setSessions([newSession]);
    setActiveSessionId(newSession.id);
    return newSession;
  }, []);

  const loadSessions = useCallback(async () => {
    setIsLoadingSessions(true);
    setError(null);

    try {
      const response = await getSessions();
      const chatSessions = response.sessions.map(mapSessionSummary);

      if (chatSessions.length === 0) {
        createAndSelectTempSession();
        return;
      }

      setSessions(chatSessions);
      setActiveSessionId((current) => current ?? chatSessions[0].id);
    } catch (loadError) {
      console.error('Error loading sessions:', loadError);
      setError(
        "I couldn't load your chat history. Check that the backend is running, then try again.",
      );
      createAndSelectTempSession();
    } finally {
      setIsLoadingSessions(false);
    }
  }, [createAndSelectTempSession]);

  useEffect(() => {
    void loadSessions();
  }, [loadSessions]);

  useEffect(() => {
    void getSubjects()
      .then(setSubjects)
      .catch((loadError) => {
        console.error('Error loading subjects:', loadError);
      });
  }, [materialsOpen]);

  useEffect(() => {
    if (activeSessionId && !activeSessionId.startsWith('temp-')) {
      void loadSessionMessages(activeSessionId);
    }
  }, [activeSessionId]);

  const loadSessionMessages = async (sessionId: string) => {
    try {
      const response = await getSessionMessages(sessionId);
      setSessions((prev) =>
        prev.map((session) =>
          session.id === sessionId
            ? { ...session, messages: response.messages }
            : session,
        ),
      );
    } catch (loadError) {
      console.error('Error loading session messages:', loadError);
      setError("I couldn't load messages for this chat. Please try selecting it again.");
    }
  };

  const handlePreferencesChange = (nextPreferences: Preferences) => {
    setPreferences(nextPreferences);
    savePreferences(nextPreferences);
  };

  const handleNewChat = () => {
    const newSession = createTempSession();
    setSessions((prev) => [newSession, ...prev]);
    setActiveSessionId(newSession.id);
    setMobileSidebarOpen(false);
  };

  const handleChatSelect = (sessionId: string) => {
    setActiveSessionId(sessionId);
    setMobileSidebarOpen(false);
  };

  const handleDeleteSession = async (sessionId: string) => {
    try {
      if (!sessionId.startsWith('temp-')) {
        await deleteSession(sessionId);
      }

      setSessions((prev) => {
        const remaining = prev.filter((session) => session.id !== sessionId);

        if (activeSessionId === sessionId) {
          if (remaining.length > 0) {
            setActiveSessionId(remaining[0].id);
          } else {
            const fallback = createTempSession();
            setActiveSessionId(fallback.id);
            return [fallback];
          }
        }

        return remaining;
      });
    } catch (deleteError) {
      console.error('Error deleting session:', deleteError);
      setError("I couldn't delete that chat. Please try again.");
    }
  };

  const handleRenameSession = async (sessionId: string, title: string) => {
    if (sessionId.startsWith('temp-')) {
      setSessions((prev) =>
        prev.map((session) =>
          session.id === sessionId ? { ...session, title } : session,
        ),
      );
      return;
    }

    try {
      const updated = await updateSessionTitle(sessionId, title);
      setSessions((prev) =>
        prev.map((session) =>
          session.id === sessionId
            ? {
                ...session,
                title: updated.title,
                lastUpdatedAt: updated.last_updated_at,
                lastMessagePreview: updated.last_message_preview,
              }
            : session,
        ),
      );
    } catch (renameError) {
      console.error('Error renaming session:', renameError);
      setError("I couldn't rename that chat. Please try again.");
    }
  };

  const handleSubjectChange = (subjectId: string | null) => {
    if (!activeSessionId) {
      return;
    }
    setSessions((prev) =>
      prev.map((session) =>
        session.id === activeSessionId ? { ...session, subjectId } : session,
      ),
    );
  };

  const handleSendMessage = async (userMessage: string) => {
    if (!activeSessionId) {
      return;
    }

    const streamingSessionId = activeSessionId;
    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: userMessage,
    };
    const assistantMsgId = `ai-${Date.now()}`;
    const assistantPlaceholder: Message = {
      id: assistantMsgId,
      role: 'assistant',
      content: '',
    };

    setSessions((prev) =>
      prev.map((session) =>
        session.id === streamingSessionId
          ? {
              ...session,
              messages: [...session.messages, userMsg, assistantPlaceholder],
              title:
                session.messages.length === 0
                  ? `${userMessage.substring(0, 30)}${userMessage.length > 30 ? '...' : ''}`
                  : session.title,
              lastMessagePreview: userMessage,
              lastUpdatedAt: new Date().toISOString(),
            }
          : session,
      ),
    );

    setIsLoading(true);

    const currentSession = sessions.find((session) => session.id === streamingSessionId);
    const messages = currentSession ? [...currentSession.messages, userMsg] : [userMsg];
    const subjectId = currentSession?.subjectId ?? null;

    await sendMessageStream(
      {
        messages,
        preferences,
        session_id: streamingSessionId.startsWith('temp-') ? undefined : streamingSessionId,
        subject_id: subjectId,
      },
      {
        onToken: (token) => {
          setSessions((prev) =>
            prev.map((session) =>
              session.id === streamingSessionId
                ? {
                    ...session,
                    messages: session.messages.map((message) =>
                      message.id === assistantMsgId
                        ? { ...message, content: message.content + token }
                        : message,
                    ),
                  }
                : session,
            ),
          );
        },
        onDone: (response) => {
          setSessions((prev) =>
            prev.map((session) =>
              session.id === streamingSessionId
                ? {
                    ...session,
                    id: response.session_id,
                    subjectId: subjectId,
                    messages: session.messages.map((message) =>
                      message.id === assistantMsgId
                        ? {
                            ...response.reply_message,
                            sources: response.sources ?? response.reply_message.sources,
                          }
                        : message,
                    ),
                    lastMessagePreview: response.reply_message.content,
                    lastUpdatedAt: new Date().toISOString(),
                  }
                : session,
            ),
          );

          if (streamingSessionId.startsWith('temp-')) {
            setActiveSessionId(response.session_id);
          }
          setIsLoading(false);
        },
        onError: (streamError) => {
          setSessions((prev) =>
            prev.map((session) =>
              session.id === streamingSessionId
                ? {
                    ...session,
                    messages: session.messages.map((message) =>
                      message.id === assistantMsgId
                        ? { ...message, content: streamError.message }
                        : message,
                    ),
                    lastMessagePreview: streamError.message,
                  }
                : session,
            ),
          );
          setIsLoading(false);
        },
      },
    );
  };

  const activeSession = sessions.find((session) => session.id === activeSessionId);

  return (
    <div className="flex h-screen bg-background">
      <aside className="hidden md:flex md:w-72 bg-background border-r border-border flex-col h-full">
        <ChatSidebar
          sessions={sessions}
          activeSessionId={activeSessionId}
          onChatSelect={handleChatSelect}
          onNewChat={handleNewChat}
          onDeleteSession={handleDeleteSession}
          onRenameSession={handleRenameSession}
          isLoading={isLoadingSessions}
        />
      </aside>

      <main className="flex-1 flex flex-col min-w-0">
        <Header
          onOpenPreferences={() => setPreferencesOpen(true)}
          onOpenMaterials={() => setMaterialsOpen(true)}
          subjects={subjects}
          selectedSubjectId={activeSession?.subjectId ?? null}
          onSubjectChange={handleSubjectChange}
        />
        {error ? <ErrorBanner message={error} onDismiss={() => setError(null)} /> : null}
        <section className="flex-1 overflow-hidden flex flex-col">
          {activeSession && activeSession.messages.length === 0 ? (
            <div className="flex-1 flex items-center justify-center text-muted-foreground">
              Start a conversation
            </div>
          ) : (
            <MessageList messages={activeSession?.messages || []} />
          )}
          <ChatInput
            onSendMessage={handleSendMessage}
            disabled={isLoading || !activeSessionId}
          />
        </section>
      </main>

      {mobileSidebarOpen ? (
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
              onDeleteSession={handleDeleteSession}
              onRenameSession={handleRenameSession}
              isLoading={isLoadingSessions}
            />
          </div>
        </div>
      ) : null}

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
        onPreferencesChange={handlePreferencesChange}
      />

      <MaterialsDrawer
        open={materialsOpen}
        onOpenChange={setMaterialsOpen}
        selectedSubjectId={activeSession?.subjectId ?? null}
        onSubjectCreated={(subject) => {
          setSubjects((prev) => [subject, ...prev]);
          if (activeSessionId) {
            handleSubjectChange(subject.id);
          }
        }}
      />
    </div>
  );
};
