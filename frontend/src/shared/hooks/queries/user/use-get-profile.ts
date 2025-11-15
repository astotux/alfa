import { userService } from '@/shared/api';
import { QUERY_KEYS } from '@/shared/config/query-keys';
import { useQuery } from '@tanstack/react-query';

export const useGetProfile = () => {
  const query = useQuery({
    queryKey: [QUERY_KEYS.USER.GET_PROFILE],
    queryFn: () => userService.getProfile(),
  });

  return query;
};
