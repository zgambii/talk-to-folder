import { useState } from 'react';
import { indexFolder, sendChatMessage } from './api/client';
import AccessTokenInput from './components/AccessTokenInput';
import ChatPanel from './components/ChatPanel';
import FolderIndexer from './components/FolderIndexer';
import IndexingSummary from './components/IndexingSummary';
import type { ChatResponse, IndexFolderResponse } from './types/api';

function App() {
  const [accessToken, setAccessToken] = useState('');
  const [folderUrl, setFolderUrl] = useState('');
  const [indexingSummary, setIndexingSummary] =
    useState<IndexFolderResponse | null>(null);
  const [message, setMessage] = useState('');
  const [chatResponse, setChatResponse] = useState<ChatResponse | null>(null);
  const [isIndexing, setIsIndexing] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const folderId = indexingSummary?.folder_id ?? null;
  const canIndex = accessToken.trim().length > 0 && folderUrl.trim().length > 0;

  async function handleIndexFolder() {
    setIsIndexing(true);
    setError(null);
    setChatResponse(null);

    try {
      const summary = await indexFolder({
        folderUrl,
        accessToken,
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
          Paste a Drive access token, index a folder, then ask questions backed
          by retrieved sources.
        </p>
      </header>

      {error !== null && <div className="error-banner">{error}</div>}

      <div className="content-grid">
        <div className="stack">
          <AccessTokenInput
            accessToken={accessToken}
            onAccessTokenChange={setAccessToken}
          />
          <FolderIndexer
            folderUrl={folderUrl}
            isIndexing={isIndexing}
            canIndex={canIndex}
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
