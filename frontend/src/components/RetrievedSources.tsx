import type { RetrievedChunk } from '../types/api';

type RetrievedSourcesProps = {
  chunks: RetrievedChunk[];
};

function RetrievedSources({ chunks }: RetrievedSourcesProps) {
  if (chunks.length === 0) {
    return null;
  }

  return (
    <details className="sources">
      <summary>Retrieved sources ({chunks.length})</summary>
      <div className="stack">
        {chunks.map((chunk) => (
          <article className="source" key={chunk.chunk_id}>
            <div>
              <strong>{chunk.document_name}</strong>
              <span>Chunk {chunk.chunk_index}</span>
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

export default RetrievedSources;
