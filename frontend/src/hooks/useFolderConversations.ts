import { useCallback, useEffect, useMemo, useState } from 'react';
import type {
  ChatUiMessage,
  FolderConversation,
  IndexFolderResponse,
} from '../types/api';

const STORAGE_KEY = 'talk-to-folder:conversations';

type StoredConversations = {
  activeConversationId: string | null;
  conversations: FolderConversation[];
};

type CreateConversationParams = {
  folderUrl: string;
  indexingSummary: IndexFolderResponse;
};

export function useFolderConversations() {
  const [storedState] = useState(loadStoredConversations);
  const [conversations, setConversations] = useState<FolderConversation[]>(
    storedState.conversations,
  );
  const [activeConversationId, setActiveConversationId] = useState<
    string | null
  >(storedState.activeConversationId);

  useEffect(() => {
    const payload: StoredConversations = {
      activeConversationId,
      conversations,
    };

    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
  }, [activeConversationId, conversations]);

  const activeConversation = useMemo(
    () =>
      conversations.find(
        (conversation) => conversation.id === activeConversationId,
      ) ?? null,
    [activeConversationId, conversations],
  );

  const createConversation = useCallback(
    ({ folderUrl, indexingSummary }: CreateConversationParams) => {
      const now = new Date().toISOString();
      const conversation: FolderConversation = {
        id: createId(),
        folderId: indexingSummary.folder_id,
        folderUrl,
        title: conversationTitle(indexingSummary),
        createdAt: now,
        updatedAt: now,
        indexingSummary,
        messages: [],
      };

      setConversations((currentConversations) => [
        conversation,
        ...currentConversations,
      ]);
      setActiveConversationId(conversation.id);

      return conversation;
    },
    [],
  );

  const appendMessage = useCallback(
    (conversationId: string, message: ChatUiMessage) => {
      setConversations((currentConversations) =>
        currentConversations.map((conversation) => {
          if (conversation.id !== conversationId) {
            return conversation;
          }

          return {
            ...conversation,
            updatedAt: message.createdAt,
            messages: [...conversation.messages, message],
          };
        }),
      );
    },
    [],
  );

  return {
    activeConversation,
    activeConversationId,
    appendMessage,
    conversations,
    createConversation,
    setActiveConversationId,
  };
}

export function createChatMessage(
  message: Omit<ChatUiMessage, 'id' | 'createdAt'>,
): ChatUiMessage {
  return {
    ...message,
    id: createId(),
    createdAt: new Date().toISOString(),
  };
}

function loadStoredConversations(): StoredConversations {
  const emptyState: StoredConversations = {
    activeConversationId: null,
    conversations: [],
  };

  try {
    const storedValue = localStorage.getItem(STORAGE_KEY);
    if (storedValue === null) {
      return emptyState;
    }

    const parsedValue = JSON.parse(storedValue) as Partial<StoredConversations>;
    const conversations = Array.isArray(parsedValue.conversations)
      ? parsedValue.conversations.filter(isFolderConversation)
      : [];
    const activeConversationId =
      typeof parsedValue.activeConversationId === 'string' &&
      conversations.some(
        (conversation) => conversation.id === parsedValue.activeConversationId,
      )
        ? parsedValue.activeConversationId
        : (conversations[0]?.id ?? null);

    return {
      activeConversationId,
      conversations,
    };
  } catch {
    return emptyState;
  }
}

function isFolderConversation(value: unknown): value is FolderConversation {
  if (typeof value !== 'object' || value === null) {
    return false;
  }

  const conversation = value as Partial<FolderConversation>;

  return (
    typeof conversation.id === 'string' &&
    typeof conversation.folderId === 'string' &&
    typeof conversation.folderUrl === 'string' &&
    typeof conversation.title === 'string' &&
    typeof conversation.createdAt === 'string' &&
    typeof conversation.updatedAt === 'string' &&
    Array.isArray(conversation.messages)
  );
}

function conversationTitle(summary: IndexFolderResponse): string {
  const name = summary.name?.trim();
  if (name !== undefined && name.length > 0) {
    return name;
  }

  return 'Drive Folder';
}

function createId(): string {
  if ('randomUUID' in crypto) {
    return crypto.randomUUID();
  }

  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}
