import type { ChatUiMessage } from '../types/api';
import CitationList from './CitationList';
import RetrievedSourcesToggle from './RetrievedSourcesToggle';

type ChatMessageProps = {
  message: ChatUiMessage;
};

function ChatMessage({ message }: ChatMessageProps) {
  return (
    <article className={`chat-message ${message.role}`}>
      <div className="message-inner">
        <div className="message-body">
          <div className="message-meta">
            <strong>{message.role === 'assistant' ? 'Folder' : 'You'}</strong>
            {message.confidence !== undefined && (
              <span className={`confidence confidence-${message.confidence}`}>
                {message.confidence}
              </span>
            )}
          </div>
          <p>{message.content}</p>
          <CitationList citations={message.citations ?? []} />
          <RetrievedSourcesToggle chunks={message.retrievedChunks ?? []} />
        </div>
      </div>
    </article>
  );
}

export default ChatMessage;
