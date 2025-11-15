import { Button } from '@/shared/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from '@/shared/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/shared/ui/dialog';
import { SidebarTrigger } from '@/shared/ui/sidebar';
import { cn } from '@/shared/utils/cn';
import { Ellipsis, Trash } from 'lucide-react';
import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useDeleteChat } from '@/shared/hooks/queries/chat/use-delete-chat';

export const Header = () => {
  const { id } = useParams();
  const [open, setOpen] = useState(false);
  const { mutate: deleteChat, isPending } = useDeleteChat();

  const handleDelete = () => {
    if (id) {
      deleteChat({ id });
      setOpen(false);
    }
  };

  // Показываем кнопку удаления только если есть ID чата
  if (!id) {
    return (
      <div className="flex items-center justify-between border-b px-4 pb-3">
        <SidebarTrigger />
      </div>
    );
  }

  return (
    <>
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
              <DropdownAction type="dandger" onClick={() => setOpen(true)}>
                <Trash className="size-4" />
                <p className="text-sm">Удалить</p>
              </DropdownAction>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Удалить чат?</DialogTitle>
            <DialogDescription>
              Вы точно хотите удалить этот чат? Это действие нельзя отменить.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setOpen(false)}
              disabled={isPending}
            >
              Отмена
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
              disabled={isPending}
            >
              {isPending ? 'Удаление...' : 'Удалить'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
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
