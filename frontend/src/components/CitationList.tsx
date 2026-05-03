import type { Citation } from '../types/api';

type CitationListProps = {
  citations: Citation[];
};

function CitationList({ citations }: CitationListProps) {
  if (citations.length === 0) {
    return null;
  }

  return (
    <div className="stack">
      <h3>Citations</h3>
      <ul className="list">
        {citations.map((citation) => (
          <li key={`${citation.chunk_id}-${citation.quote}`}>
            <strong>{citation.document_name}</strong>
            <span>"{citation.quote}"</span>
            {citation.source_url !== null && (
              <a href={citation.source_url} target="_blank" rel="noreferrer">
                Open source
              </a>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default CitationList;
