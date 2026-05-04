import type { FolderConversation } from '../types/api';

type FolderConversationListProps = {
  activeConversationId: string | null;
  conversations: FolderConversation[];
  onSelectConversation: (conversationId: string) => void;
};

function FolderConversationList({
  activeConversationId,
  conversations,
  onSelectConversation,
}: FolderConversationListProps) {
  if (conversations.length === 0) {
    return (
      <div className="sidebar-empty">
        <p>No folder chats yet.</p>
        <span>Add a Drive folder to start a saved conversation.</span>
      </div>
    );
  }

  return (
    <nav className="conversation-list" aria-label="Folder conversations">
      {conversations.map((conversation) => (
        <button
          type="button"
          className={
            conversation.id === activeConversationId
              ? 'conversation-item active'
              : 'conversation-item'
          }
          key={conversation.id}
          onClick={() => onSelectConversation(conversation.id)}
        >
          <span>{conversation.title}</span>
          <small>
            {conversation.messages.length === 0
              ? 'No messages yet'
              : `${conversation.messages.length} messages`}
          </small>
        </button>
      ))}
    </nav>
  );
}

export default FolderConversationList;
