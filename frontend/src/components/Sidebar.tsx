import { Link } from 'react-router-dom';
import type { FolderConversation } from '../types/api';
import FolderConversationList from './FolderConversationList';
import GoogleConnect from './GoogleConnect';
import NewFolderChatButton from './NewFolderChatButton';

type SidebarProps = {
  activeConversationId: string | null;
  conversations: FolderConversation[];
  isAuthenticated: boolean;
  isAuthLoading: boolean;
  onConnectGoogle: () => void;
  onLogout: () => void;
  onNewFolderChat: () => void;
  onSelectConversation: (conversationId: string) => void;
};

function Sidebar({
  activeConversationId,
  conversations,
  isAuthenticated,
  isAuthLoading,
  onConnectGoogle,
  onLogout,
  onNewFolderChat,
  onSelectConversation,
}: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="brand-block">
        <div className="brand-mark">TF</div>
        <div>
          <p>Talk to</p>
          <strong>Folder</strong>
        </div>
      </div>

      <NewFolderChatButton
        disabled={!isAuthenticated || isAuthLoading}
        onClick={onNewFolderChat}
      />

      <div className="sidebar-section">
        <p className="sidebar-label">Folder chats</p>
        <FolderConversationList
          activeConversationId={activeConversationId}
          conversations={conversations}
          onSelectConversation={onSelectConversation}
        />
      </div>

      <GoogleConnect
        isAuthenticated={isAuthenticated}
        isLoading={isAuthLoading}
        onConnect={onConnectGoogle}
        onLogout={onLogout}
      />

      <nav className="sidebar-legal" aria-label="Legal">
        <Link to="/privacy">Privacy Policy</Link>
        <span aria-hidden="true">·</span>
        <Link to="/terms">Terms of Service</Link>
      </nav>
    </aside>
  );
}

export default Sidebar;
