import type { FolderConversation } from '../types/api';
import ChatInput from './ChatInput';
import ChatMessage from './ChatMessage';
import IndexingSummary from './IndexingSummary';

const STARTER_PROMPTS = [
  'Summarize this folder',
  'What are the key decisions?',
  'What risks or open questions are mentioned?',
];

type ChatViewProps = {
  activeConversation: FolderConversation | null;
  error: string | null;
  isAuthenticated: boolean;
  isAuthLoading: boolean;
  isSending: boolean;
  onConnectGoogle: () => void;
  onNewFolderChat: () => void;
  onSendMessage: (message: string) => void;
};

function ChatView({
  activeConversation,
  error,
  isAuthenticated,
  isAuthLoading,
  isSending,
  onConnectGoogle,
  onNewFolderChat,
  onSendMessage,
}: ChatViewProps) {
  const canSend = isAuthenticated && activeConversation !== null;

  return (
    <section className="chat-view">
      {error !== null && (
        <div className="chat-error-bar" role="alert">
          {error}
        </div>
      )}
      <div className="chat-scroll">
        {isAuthenticated && activeConversation !== null && (
          <header className="chat-header">
            <div>
              <p className="eyebrow">Folder chat</p>
              <h1>{activeConversation.title}</h1>
              <a
                href={activeConversation.folderUrl}
                target="_blank"
                rel="noreferrer"
              >
                Open Drive folder
              </a>
            </div>
            <IndexingSummary
              summary={activeConversation.indexingSummary ?? null}
            />
          </header>
        )}

        {isAuthLoading && (
          <div className="center-state">
            <p className="eyebrow">Loading</p>
            <h1>Checking your Google Drive connection...</h1>
          </div>
        )}

        {!isAuthenticated && !isAuthLoading && (
          <div className="center-state">
            <p className="eyebrow">Talk to Folder</p>
            <h1>Connect Google Drive to chat with your folders.</h1>
            <p>
              Once connected, paste a folder link and we will build a searchable
              context for the conversation.
            </p>
            <button type="button" onClick={onConnectGoogle}>
              Connect Google Drive
            </button>
          </div>
        )}

        {isAuthenticated && activeConversation === null && (
          <div className="center-state">
            <p className="eyebrow">No folder selected</p>
            <h1>Start by adding a Drive folder.</h1>
            <p>
              Each folder becomes its own local chat history, so you can return
              to previous conversations from the sidebar.
            </p>
            <button type="button" onClick={onNewFolderChat}>
              Add Drive folder
            </button>
          </div>
        )}

        {isAuthenticated &&
          activeConversation !== null &&
          activeConversation.messages.length === 0 && (
            <div className="starter-panel">
              <p className="eyebrow">Try asking</p>
              <h2>What would you like to know about this folder?</h2>
              <div className="starter-grid">
                {STARTER_PROMPTS.map((prompt) => (
                  <button
                    type="button"
                    className="starter-card"
                    disabled={isSending}
                    key={prompt}
                    onClick={() => onSendMessage(prompt)}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          )}

        {isAuthenticated &&
          activeConversation !== null &&
          activeConversation.messages.length > 0 && (
            <div className="message-list">
              {activeConversation.messages.map((message) => (
                <ChatMessage message={message} key={message.id} />
              ))}
              {isSending && (
                <div className="assistant-loading">
                  Reading folder context...
                </div>
              )}
            </div>
          )}
      </div>

      <div className="chat-input-panel">
        <ChatInput
          disabled={!canSend}
          isSending={isSending}
          onSendMessage={onSendMessage}
        />
      </div>
    </section>
  );
}

export default ChatView;
