import type { ReactNode } from 'react';

type AppShellProps = {
  sidebar: ReactNode;
  children: ReactNode;
};

function AppShell({ sidebar, children }: AppShellProps) {
  return (
    <div className="app-shell">
      {sidebar}
      <main className="main-panel">{children}</main>
    </div>
  );
}

export default AppShell;
