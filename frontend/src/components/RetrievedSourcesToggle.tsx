import type { RetrievedChunk } from '../types/api';

type RetrievedSourcesToggleProps = {
  chunks: RetrievedChunk[];
};

function RetrievedSourcesToggle({ chunks }: RetrievedSourcesToggleProps) {
  if (chunks.length === 0) {
    return null;
  }

  return (
    <details className="retrieved-context">
      <summary>View retrieved context ({chunks.length})</summary>
      <div className="retrieved-list">
        {chunks.map((chunk) => (
          <article className="retrieved-card" key={chunk.chunk_id}>
            <div>
              <strong>{chunk.document_name}</strong>
              <span>
                Chunk {chunk.chunk_index}
                {chunk.score !== null
                  ? ` | Score ${chunk.score.toFixed(3)}`
                  : ''}
              </span>
            </div>
            <p>{chunk.text}</p>
            {chunk.source_url !== null && (
              <a href={chunk.source_url} target="_blank" rel="noreferrer">
                Open source
              </a>
            )}
          </article>
        ))}
      </div>
    </details>
  );
}

export default RetrievedSourcesToggle;
