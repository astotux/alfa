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
import { Ellipsis, Trash, Link2, LogOut } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useDeleteChat } from '@/shared/hooks/queries/chat/use-delete-chat';
import { useGetSyncToken } from '@/shared/hooks/queries/user/use-get-sync-token';
import { useGetProfile } from '@/shared/hooks/queries/user/use-get-profile';
import { useLogout } from '@/shared/hooks/queries/auth/use-logout';

export const Header = () => {
  const { id } = useParams();
  const [open, setOpen] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [syncToken, setSyncToken] = useState<string | null>(null);
  const { mutate: deleteChat, isPending } = useDeleteChat();
  const { mutate: getSyncToken, isPending: isTokenLoading } = useGetSyncToken();
  const { data: profile } = useGetProfile();
  const { mutate: logout, isPending: isLogoutPending } = useLogout();
  
  const isSynced = profile?.data?.telegram_id !== null && profile?.data?.telegram_id !== undefined;

  const handleDelete = () => {
    if (id) {
      deleteChat({ id });
      setOpen(false);
    }
  };

  useEffect(() => {
    if (dropdownOpen && !syncToken && !isTokenLoading && !isSynced) {
      getSyncToken(undefined, {
        onSuccess: (response) => {
          const token = response.data.token;
          setSyncToken(token);
        },
      });
    }
  }, [dropdownOpen, isSynced]);

  const telegramLink = syncToken && !isSynced
    ? `https://t.me/alfaassistant_bot?start=${syncToken}`
    : null;

  return (
    <>
      <div className="flex items-center justify-between border-b px-4 pb-3">
        <SidebarTrigger />
        <div>
          <DropdownMenu open={dropdownOpen} onOpenChange={setDropdownOpen}>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost">
                <Ellipsis className="size-5" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              className="w-fit min-w-40 p-2 rounded-2xl"
              align="end"
            >
              {telegramLink && (
                <DropdownAction
                  type="default"
                  onClick={() => {
                    window.open(telegramLink, '_blank', 'noopener,noreferrer');
                  }}
                >
                  <Link2 className="size-4" />
                  <p className="text-sm">Синхронизировать с ТГ ботом</p>
                </DropdownAction>
              )}
              {!telegramLink && isTokenLoading && (
                <DropdownAction type="default" onClick={() => {}}>
                  <p className="text-sm">Загрузка...</p>
                </DropdownAction>
              )}
              {id && (
                <DropdownAction type="dandger" onClick={() => setOpen(true)}>
                  <Trash className="size-4" />
                  <p className="text-sm">Удалить чат</p>
                </DropdownAction>
              )}
              <DropdownAction
                type="dandger"
                onClick={() => logout()}
                disabled={isLogoutPending}
              >
                <LogOut className="size-4" />
                <p className="text-sm">
                  {isLogoutPending ? 'Выход...' : 'Выйти из аккаунта'}
                </p>
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
  disabled?: boolean;
};
const DropdownAction = ({
  children,
  onClick,
  type = 'default',
  disabled = false,
}: Props) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={cn(
        'flex items-center gap-2 p-2 w-full rounded-xl transition-all',
        {
          'text-destructive hover:bg-destructive/10  ': type === 'dandger',
          'cursor-not-allowed opacity-60': disabled,
          'cursor-pointer': !disabled,
        }
      )}
    >
      {children}
    </button>
  );
};
