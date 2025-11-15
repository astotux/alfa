import {
  SidebarContent,
  Sidebar as SidebarMain,
  SidebarMenuItem,
} from '@/shared/ui/sidebar';
import { sidebarConfig } from './sidebar.config';
import { Link } from 'react-router-dom';

import { SidebarCollapse } from './sidebar-collapse';
import { useGetChats } from '@/shared/hooks/queries/chat/use-get-chats';

export const Sidebar = () => {
  const { data: chatsData = [], isLoading } = useGetChats();

  return (
    <SidebarMain>
      <SidebarContent className="py-4 px-2 flex flex-col gap-6 no-scrollbar">
        {sidebarConfig.map((item) => (
          <Link to={item.link}>
            <SidebarMenuItem
              className="list-none p-2! rounded-xl  hover:bg-primary/10 "
              key={item.link}
            >
              <div className="flex items-center gap-2 ">
                {item.icon && <item.icon className="size-4" />}
                <span className="text-sm">{item.title}</span>
              </div>
            </SidebarMenuItem>
          </Link>
        ))}
        {!isLoading && chatsData.length > 0 && (
          <SidebarCollapse data={chatsData} title="Чаты" />
        )}
      </SidebarContent>
    </SidebarMain>
  );
};
