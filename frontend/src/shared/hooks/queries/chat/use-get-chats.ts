import { chatService } from '@/shared/api/services/chat.service';
import { QUERY_KEYS } from '@/shared/config/query-keys';
import { ROUTES } from '@/shared/config/routes';
import { useQuery } from '@tanstack/react-query';

export const useGetChats = () => {
  const query = useQuery({
    queryKey: [QUERY_KEYS.CHAT.GET_CHATS],
    queryFn: () => chatService.getChats(),
    select: (data) =>
      data.data.map((chat) => ({
        title: chat.title,
        link: `${ROUTES.CHAT}/${chat.id}`,
      })),
  });

  return query;
};

