import { useEffect, useState } from 'react';
import {
  getAuthStatus,
  googleLoginUrl,
  indexFolder,
  logout,
  sendChatMessage,
} from './api/client';
import AppShell from './components/AppShell';
import ChatView from './components/ChatView';
import NewFolderModal from './components/NewFolderModal';
import Sidebar from './components/Sidebar';
import {
  createChatMessage,
  useFolderConversations,
} from './hooks/useFolderConversations';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isAuthLoading, setIsAuthLoading] = useState(true);
  const [isNewFolderModalOpen, setIsNewFolderModalOpen] = useState(false);
  const [isIndexing, setIsIndexing] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const {
    activeConversation,
    activeConversationId,
    appendMessage,
    conversations,
    createConversation,
    setActiveConversationId,
  } = useFolderConversations();

  useEffect(() => {
    async function loadAuthStatus() {
      try {
        const status = await getAuthStatus();
        setIsAuthenticated(status.authenticated);
      } catch (caughtError) {
        setError(errorMessage(caughtError));
      } finally {
        setIsAuthLoading(false);
      }
    }

    void loadAuthStatus();
  }, []);

  function handleConnectGoogle() {
    window.location.assign(googleLoginUrl());
  }

  function handleOpenNewFolderModal() {
    setError(null);
    setIsNewFolderModalOpen(true);
  }

  async function handleLogout() {
    setError(null);

    try {
      await logout();
      setIsAuthenticated(false);
    } catch (caughtError) {
      setError(errorMessage(caughtError));
    }
  }

  async function handleIndexFolder(folderUrl: string) {
    setIsIndexing(true);
    setError(null);

    try {
      const summary = await indexFolder({
        folderUrl,
      });
      createConversation({
        folderUrl,
        indexingSummary: summary,
      });
      setIsNewFolderModalOpen(false);
    } catch (caughtError) {
      setError(errorMessage(caughtError));
    } finally {
      setIsIndexing(false);
    }
  }

  async function handleSendMessage(message: string) {
    if (activeConversation === null) {
      return;
    }

    const conversationId = activeConversation.id;
    const folderId = activeConversation.folderId;
    const userMessage = createChatMessage({
      role: 'user',
      content: message,
    });

    appendMessage(conversationId, userMessage);
    setIsSending(true);
    setError(null);

    try {
      const response = await sendChatMessage({
        folderId,
        message,
      });
      appendMessage(
        conversationId,
        createChatMessage({
          role: 'assistant',
          content: response.answer,
          confidence: response.confidence,
          citations: response.citations,
          retrievedChunks: response.retrieved_chunks,
        }),
      );
    } catch (caughtError) {
      setError(errorMessage(caughtError));
    } finally {
      setIsSending(false);
    }
  }

  return (
    <>
      <AppShell
        sidebar={
          <Sidebar
            activeConversationId={activeConversationId}
            conversations={conversations}
            isAuthenticated={isAuthenticated}
            isAuthLoading={isAuthLoading}
            onConnectGoogle={handleConnectGoogle}
            onLogout={handleLogout}
            onNewFolderChat={handleOpenNewFolderModal}
            onSelectConversation={setActiveConversationId}
          />
        }
      >
        <ChatView
          activeConversation={activeConversation}
          error={error}
          isAuthenticated={isAuthenticated}
          isAuthLoading={isAuthLoading}
          isSending={isSending}
          onConnectGoogle={handleConnectGoogle}
          onNewFolderChat={handleOpenNewFolderModal}
          onSendMessage={handleSendMessage}
        />
      </AppShell>
      {isNewFolderModalOpen && (
        <NewFolderModal
          error={error}
          isIndexing={isIndexing}
          isOpen={isNewFolderModalOpen}
          onClose={() => setIsNewFolderModalOpen(false)}
          onSubmit={handleIndexFolder}
        />
      )}
    </>
  );
}

function errorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  return 'Something went wrong.';
}

export default App;
