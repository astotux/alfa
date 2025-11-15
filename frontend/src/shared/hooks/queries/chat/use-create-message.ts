import { chatService } from '@/shared/api/services/chat.service';
import { QUERY_KEYS } from '@/shared/config/query-keys';
import type { CreateMessageDto } from '@/shared/types/chat.type';
import { useMutation, useQueryClient } from '@tanstack/react-query';

export const useCreateMessage = () => {
  const queryClient = useQueryClient();

  const mutate = useMutation({
    mutationKey: [QUERY_KEYS.CHAT.CREATE_MESSAGE],
    mutationFn: (dto: CreateMessageDto) => chatService.createMessage(dto),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.CHAT.GET_CHAT] });
    },
  });

  return mutate;
};
