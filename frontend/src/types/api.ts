export type Confidence = 'low' | 'medium' | 'high';

export type SkippedFile = {
  file_id: string;
  name: string;
  mime_type: string | null;
  reason: string;
};

export type Citation = {
  chunk_id: string;
  document_name: string;
  source_url: string | null;
  quote: string;
};

export type RetrievedChunk = {
  chunk_id: string;
  document_id: string;
  document_name: string;
  source_url: string | null;
  chunk_index: number;
  text: string;
  score: number | null;
};

export type IndexFolderRequest = {
  folder_url: string;
};

export type IndexFolderResponse = {
  folder_id: string;
  folder_url: string;
  /** Present after backend returns Drive metadata; omit on older servers. */
  name?: string | null;
  files_found: number;
  files_indexed: number;
  chunks_created: number;
  skipped_files: SkippedFile[];
};

export type ChatRequest = {
  folder_id: string;
  message: string;
};

export type ChatResponse = {
  answer: string;
  confidence: Confidence;
  citations: Citation[];
  retrieved_chunks: RetrievedChunk[];
};

export type ChatUiMessage = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  createdAt: string;
  confidence?: Confidence;
  citations?: Citation[];
  retrievedChunks?: RetrievedChunk[];
};

export type FolderConversation = {
  id: string;
  folderId: string;
  folderUrl: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  indexingSummary?: IndexFolderResponse;
  messages: ChatUiMessage[];
};

export type AuthStatusResponse = {
  authenticated: boolean;
};

export type LogoutResponse = {
  success: boolean;
};
