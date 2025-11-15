import { chatService } from '@/shared/api/services/chat.service';
import { QUERY_KEYS } from '@/shared/config/query-keys';
import { useQuery } from '@tanstack/react-query';

export const useGetChats = () => {
  const query = useQuery({
    queryKey: [QUERY_KEYS.CHAT.GET_CHATS],
    queryFn: () => chatService.getChats(),
    select: (data) => data.data,
  });

  return query;
};

