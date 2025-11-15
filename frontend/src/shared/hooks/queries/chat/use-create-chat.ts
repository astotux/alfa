import { chatService } from '@/shared/api/services/chat.service';
import { QUERY_KEYS } from '@/shared/config/query-keys';
import { ROUTES } from '@/shared/config/routes';
import type { CreateChatDto } from '@/shared/types/chat.type';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

export const useCreateChat = () => {
  const navigate = useNavigate();

  const mutation = useMutation({
    mutationKey: [QUERY_KEYS.CHAT.CREATE_CHAT],
    mutationFn: (dto: CreateChatDto) => chatService.createChat(dto),

    onSuccess: ({ data }) => {
      navigate(`${ROUTES.CHAT}/${data.chatId}`);
    },

    onError: () => {
      toast.error('Произошла ошибка при создании чата');
    },
  });

  return mutation;
};
