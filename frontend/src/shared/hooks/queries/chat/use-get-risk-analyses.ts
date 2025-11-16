import { chatService } from '@/shared/api/services/chat.service';
import { QUERY_KEYS } from '@/shared/config/query-keys';
import { ROUTES } from '@/shared/config/routes';
import { useQuery } from '@tanstack/react-query';

export const useGetRiskAnalyses = () => {
  const query = useQuery({
    queryKey: [QUERY_KEYS.CHAT.GET_RISK_ANALYSES],
    queryFn: () => chatService.getChats('risk_vision'),
    select: (data) =>
      data.data.map((chat) => ({
        title: chat.title,
        link: `${ROUTES.RISK_VISION}/${chat.id}`,
      })),
  });

  return query;
};

