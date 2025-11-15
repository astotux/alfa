import { chatService } from '@/shared/api/services/chat.service';
import { QUERY_KEYS } from '@/shared/config/query-keys';
import { ROUTES } from '@/shared/config/routes';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

export const useDeleteChat = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationKey: [QUERY_KEYS.CHAT.DELETE_CHAT],
    mutationFn: ({ id }: { id: string }) => chatService.deleteChat({ id }),

    onSuccess: (_, variables) => {
      // Инвалидируем список чатов
      queryClient.invalidateQueries({ 
        queryKey: [QUERY_KEYS.CHAT.GET_CHATS] 
      });
      // Удаляем кэш конкретного чата
      queryClient.removeQueries({ 
        queryKey: [QUERY_KEYS.CHAT.GET_CHAT, variables.id] 
      });
      // Редиректим на страницу создания нового чата
      navigate(ROUTES.CHAT);
      toast.success('Чат успешно удален');
    },

    onError: () => {
      toast.error('Произошла ошибка при удалении чата');
    },
  });

  return mutation;
};

