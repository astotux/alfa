import {
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  Sidebar as SidebarMain,
  SidebarMenuItem,
} from '@/shared/ui/sidebar';
import { sidebarConfig } from './sidebar.config';
import { Link, useLocation } from 'react-router-dom';
import { cn } from '@/shared/utils/cn';
import { SidebarCollapse } from './sidebar-collapse';

export const Sidebar = () => {
  const chats = [
    {
      title: 'Мой первый промт в этом приложении',
      link: '/chat/1',
    },
    {
      title: 'Как сделать чат в этом приложении',
      link: '/chat/2',
    },
    {
      title: 'Как получить ответ от AI в этом приложении',
      link: '/chat/3',
    },
  ];

  return (
    <SidebarMain>
      <SidebarContent className="py-4 px-2 flex flex-col gap-6">
        {sidebarConfig.map((item) => (
          <SidebarMenuItem
            className="list-none p-2! rounded-xl  hover:bg-primary/10 "
            key={item.link}
          >
            <Link className="flex items-center gap-2 " to={item.link}>
              {item.icon && <item.icon className="size-4" />}
              <span className="text-sm">{item.title}</span>
            </Link>
          </SidebarMenuItem>
        ))}
        <SidebarCollapse data={chats} title="Чаты" />
      </SidebarContent>
    </SidebarMain>
  );
};
