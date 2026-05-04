import type { IndexFolderResponse } from '../types/api';

type IndexingSummaryProps = {
  summary: IndexFolderResponse | null;
};

function IndexingSummary({ summary }: IndexingSummaryProps) {
  if (summary === null) {
    return null;
  }

  return (
    <section className="index-summary">
      <div className="summary-stats">
        <Stat label="Files found" value={summary.files_found} />
        <Stat label="Files indexed" value={summary.files_indexed} />
        <Stat label="Chunks created" value={summary.chunks_created} />
      </div>
      {summary.skipped_files.length > 0 && (
        <details className="skipped-files">
          <summary>Skipped files ({summary.skipped_files.length})</summary>
          <ul>
            {summary.skipped_files.map((file) => (
              <li key={file.file_id}>
                <strong>{file.name}</strong>
                <span>{file.reason}</span>
              </li>
            ))}
          </ul>
        </details>
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
    <div className="summary-stat">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

export default IndexingSummary;
