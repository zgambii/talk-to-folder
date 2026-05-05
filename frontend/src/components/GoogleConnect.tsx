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
    <section
      className={
        isAuthenticated
          ? 'google-connect'
          : 'google-connect google-connect--plain'
      }
    >
      {isAuthenticated ? (
        <div>
          <span className="connection-dot" />
          <div>
            <strong>Google Drive connected</strong>
            <button type="button" className="text-button" onClick={onLogout}>
              Log out
            </button>
          </div>
        </div>
      ) : (
        <button
          type="button"
          className="connect-button"
          disabled={isLoading}
          onClick={onConnect}
        >
          {isLoading ? 'Checking...' : 'Connect Google Drive'}
        </button>
      )}
    </section>
  );
}

export default GoogleConnect;
