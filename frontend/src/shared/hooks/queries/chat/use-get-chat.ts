import { chatService } from '@/shared/api/services/chat.service';
import { QUERY_KEYS } from '@/shared/config/query-keys';
import { useQuery } from '@tanstack/react-query';

export const useGetChat = (id: string) => {
  const query = useQuery({
    queryKey: [QUERY_KEYS.CHAT.GET_CHAT],
    queryFn: () => chatService.getChat({ id: id || '' }),
    enabled: !!id,
    select: (data) => data.data,
  });

  return query;
};
