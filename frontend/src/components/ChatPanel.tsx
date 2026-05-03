import type { ChatResponse } from '../types/api';
import CitationList from './CitationList';
import RetrievedSources from './RetrievedSources';

type ChatPanelProps = {
  folderId: string | null;
  message: string;
  isSending: boolean;
  response: ChatResponse | null;
  onMessageChange: (message: string) => void;
  onSendMessage: () => void;
};

function ChatPanel({
  folderId,
  message,
  isSending,
  response,
  onMessageChange,
  onSendMessage,
}: ChatPanelProps) {
  const isDisabled = folderId === null;

  return (
    <section className="card">
      <div className="section-heading">
        <p className="eyebrow">Step 3</p>
        <h2>Ask the folder</h2>
      </div>
      <label className="field">
        <span>Question</span>
        <textarea
          rows={4}
          value={message}
          disabled={isDisabled}
          onChange={(event) => onMessageChange(event.target.value)}
          placeholder={
            isDisabled
              ? 'Index a folder before asking questions.'
              : 'What does this folder say about...?'
          }
        />
      </label>
      <button
        type="button"
        disabled={isDisabled || isSending || !message.trim()}
        onClick={onSendMessage}
      >
        {isSending ? 'Asking...' : 'Ask Question'}
      </button>
      {response !== null && (
        <div className="answer">
          <div className="answer-header">
            <h3>Answer</h3>
            <span className={`confidence confidence-${response.confidence}`}>
              {response.confidence}
            </span>
          </div>
          <p>{response.answer}</p>
          <CitationList citations={response.citations} />
          <RetrievedSources chunks={response.retrieved_chunks} />
        </div>
      )}
    </section>
  );
}

export default ChatPanel;
