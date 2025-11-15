import {
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenuItem,
} from '@/shared/ui/sidebar';
import { cn } from '@/shared/utils/cn';
import { ChevronUp } from 'lucide-react';
import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

type Props = {
  title: string;
  data: {
    title: string;
    link: string;
  }[];
};

export const SidebarCollapse = ({ data, title }: Props) => {
  const [open, setOpen] = useState(true);
  const { pathname } = useLocation();

  return (
    <SidebarGroup key={'chats'}>
      <SidebarGroupLabel onClick={() => setOpen((prev) => !prev)}>
        <div className="flex items-center gap-2 group cursor-pointer">
          <span>{title}</span>
          <ChevronUp
            size={16}
            className={cn('opacity-0 transition-all group-hover:opacity-100', {
              'rotate-180': open,
            })}
          />
        </div>
      </SidebarGroupLabel>
      {open && (
        <SidebarGroupContent>
          {data.map((item, index) => (
            <SidebarMenuItem
              className={cn(
                'list-none p-2! rounded-xl  hover:bg-primary/10 text-ellipsis overflow-hidden whitespace-nowrap',
                {
                  'bg-primary/10': pathname === item.link,
                }
              )}
              key={index}
            >
              <Link to={item.link}>
                <span>{item.title}</span>
              </Link>
            </SidebarMenuItem>
          ))}
        </SidebarGroupContent>
      )}
    </SidebarGroup>
  );
};
