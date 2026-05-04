type FolderIndexerProps = {
  folderUrl: string;
  isIndexing: boolean;
  canIndex: boolean;
  isAuthenticated: boolean;
  onFolderUrlChange: (folderUrl: string) => void;
  onIndexFolder: () => void;
};

function FolderIndexer({
  folderUrl,
  isIndexing,
  canIndex,
  isAuthenticated,
  onFolderUrlChange,
  onIndexFolder,
}: FolderIndexerProps) {
  return (
    <section className="card">
      <div className="section-heading">
        <p className="eyebrow">Step 2</p>
        <h2>Index a Drive folder</h2>
      </div>
      <label className="field">
        <span>Folder URL</span>
        <input
          type="url"
          value={folderUrl}
          onChange={(event) => onFolderUrlChange(event.target.value)}
          placeholder="https://drive.google.com/drive/folders/..."
        />
      </label>
      <button
        type="button"
        disabled={!canIndex || isIndexing}
        onClick={onIndexFolder}
      >
        {isIndexing ? 'Indexing...' : 'Index Folder'}
      </button>
      {!isAuthenticated && (
        <p className="muted">Connect Google Drive before indexing a folder.</p>
      )}
    </section>
  );
}

export default FolderIndexer;
