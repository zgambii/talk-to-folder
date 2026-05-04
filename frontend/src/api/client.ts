import type {
  AuthStatusResponse,
  ChatRequest,
  ChatResponse,
  IndexFolderRequest,
  IndexFolderResponse,
  LogoutResponse,
} from '../types/api';

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') ||
  'http://localhost:8000';

type IndexFolderParams = {
  folderUrl: string;
};

type SendChatMessageParams = {
  folderId: string;
  message: string;
};

export async function indexFolder({
  folderUrl,
}: IndexFolderParams): Promise<IndexFolderResponse> {
  return postJson<IndexFolderRequest, IndexFolderResponse>(
    '/api/folders/index',
    { folder_url: folderUrl },
  );
}

export async function sendChatMessage({
  folderId,
  message,
}: SendChatMessageParams): Promise<ChatResponse> {
  return postJson<ChatRequest, ChatResponse>('/api/chat', {
    folder_id: folderId,
    message,
  });
}

export async function getAuthStatus(): Promise<AuthStatusResponse> {
  return getJson<AuthStatusResponse>('/api/auth/me');
}

export async function logout(): Promise<LogoutResponse> {
  return postJson<Record<string, never>, LogoutResponse>(
    '/api/auth/logout',
    {},
  );
}

export function googleLoginUrl(): string {
  return `${API_BASE_URL}/api/auth/google/login`;
}

async function getJson<TResponse>(path: string): Promise<TResponse> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    credentials: 'include',
  });

  if (!response.ok) {
    throw new Error(await responseErrorMessage(response));
  }

  return response.json() as Promise<TResponse>;
}

async function postJson<TRequest, TResponse>(
  path: string,
  body: TRequest,
  headers: Record<string, string> = {},
): Promise<TResponse> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    throw new Error(await responseErrorMessage(response));
  }

  return response.json() as Promise<TResponse>;
}

async function responseErrorMessage(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown };
    if (typeof body.detail === 'string') {
      return body.detail;
    }
  } catch {
    // Fall through to the status text when the backend does not return JSON.
  }

  return `Request failed with status ${response.status}`;
}
