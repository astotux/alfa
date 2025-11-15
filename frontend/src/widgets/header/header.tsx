import { Button } from '@/shared/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from '@/shared/ui/dropdown-menu';
import { SidebarTrigger } from '@/shared/ui/sidebar';
import { cn } from '@/shared/utils/cn';
import { Ellipsis, Trash } from 'lucide-react';

export const Header = () => {
  return (
    <div className="flex items-center justify-between border-b px-4 pb-3">
      <SidebarTrigger />
      <div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost">
              <Ellipsis className="size-5" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            className="w-fit min-w-40 p-2 rounded-2xl"
            align="end"
          >
            <DropdownAction type="dandger">
              <Trash className="size-4" />
              <p className="text-sm">Удалить</p>
            </DropdownAction>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
};

type Props = {
  onClick?: () => void;
  type?: 'default' | 'dandger';
  children: React.ReactNode;
};
const DropdownAction = ({ children, onClick, type = 'default' }: Props) => {
  return (
    <button
      onClick={onClick}
      className={cn(
        'flex items-center gap-2 p-2 w-full rounded-xl cursor-pointer transition-all',
        {
          'text-destructive hover:bg-destructive/10  ': type === 'dandger',
        }
      )}
    >
      {children}
    </button>
  );
};
