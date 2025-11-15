import { SidebarProvider, SidebarTrigger } from '@/shared/ui/sidebar';
import { Sidebar } from '../sidebar/sidebar';
import { Header } from '../header/header';

export const Layout = ({ children }: { children: React.ReactNode }) => {
  return (
    <SidebarProvider>
      <Sidebar />
      <main className="w-full flex flex-col py-3">
        <Header />
        <div className="flex-1 px-4">{children}</div>
      </main>
    </SidebarProvider>
  );
};
