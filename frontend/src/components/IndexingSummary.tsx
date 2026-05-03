import type { IndexFolderResponse } from '../types/api';

type IndexingSummaryProps = {
  summary: IndexFolderResponse | null;
};

function IndexingSummary({ summary }: IndexingSummaryProps) {
  if (summary === null) {
    return null;
  }

  return (
    <section className="card">
      <div className="section-heading">
        <p className="eyebrow">Indexed</p>
        <h2>Folder summary</h2>
      </div>
      <div className="stats-grid">
        <Stat label="Files found" value={summary.files_found} />
        <Stat label="Files indexed" value={summary.files_indexed} />
        <Stat label="Chunks created" value={summary.chunks_created} />
      </div>
      {summary.skipped_files.length > 0 && (
        <div className="stack">
          <h3>Skipped files</h3>
          <ul className="list">
            {summary.skipped_files.map((file) => (
              <li key={file.file_id}>
                <strong>{file.name}</strong>
                <span>{file.reason}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

type StatProps = {
  label: string;
  value: number;
};

function Stat({ label, value }: StatProps) {
  return (
    <div className="stat">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

export default IndexingSummary;
