import { chatService } from '@/shared/api/services/chat.service';
import { QUERY_KEYS } from '@/shared/config/query-keys';
import { ROUTES } from '@/shared/config/routes';
import type { CreateChatDto } from '@/shared/types/chat.type';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

export const useCreateChat = (baseRoute: string = ROUTES.CHAT) => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationKey: [QUERY_KEYS.CHAT.CREATE_CHAT],
    mutationFn: (dto: CreateChatDto) => chatService.createChat(dto),

    onSuccess: ({ data }) => {
      const isRiskVision = baseRoute === ROUTES.RISK_VISION;
      queryClient.invalidateQueries({ 
        queryKey: [QUERY_KEYS.CHAT.GET_CHATS] 
      });
      if (isRiskVision) {
        queryClient.invalidateQueries({ 
          queryKey: [QUERY_KEYS.CHAT.GET_RISK_ANALYSES] 
        });
      }
      navigate(`${baseRoute}/${data.chatId}`);
    },

    onError: () => {
      toast.error('Произошла ошибка при создании чата');
    },
  });

  return mutation;
};
