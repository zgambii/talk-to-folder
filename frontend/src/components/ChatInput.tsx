import type { FormEvent, KeyboardEvent } from 'react';
import { useState } from 'react';

type ChatInputProps = {
  disabled: boolean;
  isSending: boolean;
  onSendMessage: (message: string) => void;
};

function ChatInput({ disabled, isSending, onSendMessage }: ChatInputProps) {
  const [message, setMessage] = useState('');

  function submitMessage() {
    const trimmedMessage = message.trim();
    if (trimmedMessage.length === 0 || disabled || isSending) {
      return;
    }

    onSendMessage(trimmedMessage);
    setMessage('');
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    submitMessage();
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      submitMessage();
    }
  }

  return (
    <form className="chat-input-wrap" onSubmit={handleSubmit}>
      <textarea
        aria-label="Ask a question"
        rows={1}
        value={message}
        disabled={disabled || isSending}
        onChange={(event) => setMessage(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={
          disabled
            ? 'Create or select a folder chat to ask questions.'
            : 'Ask about this folder...'
        }
      />
      <button
        type="submit"
        className="send-button"
        disabled={disabled || isSending || !message.trim()}
      >
        {isSending ? '...' : 'Send'}
      </button>
    </form>
  );
}

export default ChatInput;
