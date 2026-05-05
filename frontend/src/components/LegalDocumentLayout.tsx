import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';

type LegalDocumentLayoutProps = {
  children: ReactNode;
  title: string;
};

function LegalDocumentLayout({ children, title }: LegalDocumentLayoutProps) {
  return (
    <div className="legal-page">
      <header className="legal-page-header">
        <Link className="legal-back" to="/">
          ← Back to Talk to Folder
        </Link>
        <p className="eyebrow">Talk to Folder</p>
        <h1>{title}</h1>
        <p className="muted legal-updated">Last updated: May 4, 2026</p>
      </header>
      <article className="legal-prose">{children}</article>
    </div>
  );
}

export default LegalDocumentLayout;
