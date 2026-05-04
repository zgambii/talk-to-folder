import { useEffect, useState } from 'react';
import {
  getAuthStatus,
  googleLoginUrl,
  indexFolder,
  logout,
  sendChatMessage,
} from './api/client';
import ChatPanel from './components/ChatPanel';
import FolderIndexer from './components/FolderIndexer';
import GoogleConnect from './components/GoogleConnect';
import IndexingSummary from './components/IndexingSummary';
import type { ChatResponse, IndexFolderResponse } from './types/api';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isAuthLoading, setIsAuthLoading] = useState(true);
  const [folderUrl, setFolderUrl] = useState('');
  const [indexingSummary, setIndexingSummary] =
    useState<IndexFolderResponse | null>(null);
  const [message, setMessage] = useState('');
  const [chatResponse, setChatResponse] = useState<ChatResponse | null>(null);
  const [isIndexing, setIsIndexing] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const folderId = indexingSummary?.folder_id ?? null;
  const canIndex = isAuthenticated && folderUrl.trim().length > 0;

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

  async function handleLogout() {
    setError(null);

    try {
      await logout();
      setIsAuthenticated(false);
      setIndexingSummary(null);
      setChatResponse(null);
    } catch (caughtError) {
      setError(errorMessage(caughtError));
    }
  }

  async function handleIndexFolder() {
    setIsIndexing(true);
    setError(null);
    setChatResponse(null);

    try {
      const summary = await indexFolder({
        folderUrl,
      });
      setIndexingSummary(summary);
    } catch (caughtError) {
      setError(errorMessage(caughtError));
    } finally {
      setIsIndexing(false);
    }
  }

  async function handleSendMessage() {
    if (folderId === null) {
      return;
    }

    setIsSending(true);
    setError(null);

    try {
      const response = await sendChatMessage({
        folderId,
        message,
      });
      setChatResponse(response);
    } catch (caughtError) {
      setError(errorMessage(caughtError));
    } finally {
      setIsSending(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="hero">
        <p className="eyebrow">Talk to Folder</p>
        <h1>Ask grounded questions about a Google Drive folder.</h1>
        <p>
          Connect Google Drive, index a folder, then ask questions backed by
          retrieved sources.
        </p>
      </header>

      {error !== null && <div className="error-banner">{error}</div>}

      <div className="content-grid">
        <div className="stack">
          <GoogleConnect
            isAuthenticated={isAuthenticated}
            isLoading={isAuthLoading}
            onConnect={handleConnectGoogle}
            onLogout={handleLogout}
          />
          <FolderIndexer
            folderUrl={folderUrl}
            isIndexing={isIndexing}
            canIndex={canIndex}
            isAuthenticated={isAuthenticated}
            onFolderUrlChange={setFolderUrl}
            onIndexFolder={handleIndexFolder}
          />
          <IndexingSummary summary={indexingSummary} />
        </div>

        <ChatPanel
          folderId={folderId}
          message={message}
          isSending={isSending}
          response={chatResponse}
          onMessageChange={setMessage}
          onSendMessage={handleSendMessage}
        />
      </div>
    </main>
  );
}

function errorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  return 'Something went wrong.';
}

export default App;
