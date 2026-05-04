import type { Citation } from '../types/api';

type CitationListProps = {
  citations: Citation[];
};

function CitationList({ citations }: CitationListProps) {
  if (citations.length === 0) {
    return null;
  }

  return (
    <div className="citation-block">
      <span>Citations</span>
      <ul className="citation-list">
        {citations.map((citation) => (
          <li
            className="citation-card"
            key={`${citation.chunk_id}-${citation.quote}`}
          >
            <strong>{citation.document_name}</strong>
            <p>"{citation.quote}"</p>
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
