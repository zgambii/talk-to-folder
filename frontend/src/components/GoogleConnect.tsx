type GoogleConnectProps = {
  isAuthenticated: boolean;
  isLoading: boolean;
  onConnect: () => void;
  onLogout: () => void;
};

function GoogleConnect({
  isAuthenticated,
  isLoading,
  onConnect,
  onLogout,
}: GoogleConnectProps) {
  return (
    <section className="card">
      <div className="section-heading">
        <p className="eyebrow">Step 1</p>
        <h2>Connect Google Drive</h2>
      </div>
      <p className="muted">
        Sign in with Google to grant read-only Drive access. The backend stores
        the token in a signed session cookie.
      </p>
      {isAuthenticated ? (
        <div className="inline-actions">
          <span className="status-pill">Connected</span>
          <button type="button" className="secondary-button" onClick={onLogout}>
            Log out
          </button>
        </div>
      ) : (
        <button type="button" disabled={isLoading} onClick={onConnect}>
          {isLoading ? 'Checking...' : 'Connect Google Drive'}
        </button>
      )}
    </section>
  );
}

export default GoogleConnect;
