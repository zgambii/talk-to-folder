import { useState } from 'react';
import type { FormEvent } from 'react';

type NewFolderModalProps = {
  error: string | null;
  isIndexing: boolean;
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (folderUrl: string) => void;
};

function NewFolderModal({
  error,
  isIndexing,
  isOpen,
  onClose,
  onSubmit,
}: NewFolderModalProps) {
  const [folderUrl, setFolderUrl] = useState('');

  if (!isOpen) {
    return null;
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit(folderUrl);
  }

  return (
    <div className="modal-backdrop" role="presentation">
      <div
        aria-labelledby="new-folder-title"
        aria-modal="true"
        className="modal-card"
        role="dialog"
      >
        <div className="modal-header">
          <div>
            <p className="eyebrow">New folder chat</p>
            <h2 id="new-folder-title">Paste a Google Drive folder link</h2>
          </div>
          <button
            type="button"
            className="icon-button"
            disabled={isIndexing}
            onClick={onClose}
          >
            Close
          </button>
        </div>

        <p className="muted">
          We will index supported files in the folder, save this chat locally,
          and use it as the context for your questions.
        </p>

        <form className="folder-form" onSubmit={handleSubmit}>
          <label className="field">
            <span>Drive folder URL</span>
            <input
              autoFocus
              value={folderUrl}
              disabled={isIndexing}
              onChange={(event) => setFolderUrl(event.target.value)}
              placeholder="https://drive.google.com/drive/folders/..."
            />
          </label>

          {error !== null && <div className="inline-error">{error}</div>}

          <button type="submit" disabled={isIndexing || !folderUrl.trim()}>
            {isIndexing ? 'Indexing folder...' : 'Create folder chat'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default NewFolderModal;
