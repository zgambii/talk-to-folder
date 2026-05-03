type AccessTokenInputProps = {
  accessToken: string;
  onAccessTokenChange: (accessToken: string) => void;
};

function AccessTokenInput({
  accessToken,
  onAccessTokenChange,
}: AccessTokenInputProps) {
  return (
    <section className="card">
      <div className="section-heading">
        <p className="eyebrow">Step 1</p>
        <h2>Paste a Google access token</h2>
      </div>
      <p className="muted">
        OAuth is not wired yet. For local testing, paste a short-lived Google
        Drive access token here.
      </p>
      <label className="field">
        <span>Access token</span>
        <textarea
          rows={3}
          value={accessToken}
          onChange={(event) => onAccessTokenChange(event.target.value)}
          placeholder="ya29..."
        />
      </label>
    </section>
  );
}

export default AccessTokenInput;
