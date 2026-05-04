type NewFolderChatButtonProps = {
  disabled: boolean;
  onClick: () => void;
};

function NewFolderChatButton({ disabled, onClick }: NewFolderChatButtonProps) {
  return (
    <button
      type="button"
      className="new-chat-button"
      disabled={disabled}
      onClick={onClick}
    >
      <span>+</span>
      New Folder Chat
    </button>
  );
}

export default NewFolderChatButton;
