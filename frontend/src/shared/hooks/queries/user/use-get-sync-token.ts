import { userService } from '@/shared/api';
import { QUERY_KEYS } from '@/shared/config/query-keys';
import { useMutation } from '@tanstack/react-query';

export const useGetSyncToken = () => {
  const mutation = useMutation({
    mutationKey: [QUERY_KEYS.USER.GET_SYNC_TOKEN],
    mutationFn: () => userService.getSyncToken(),
  });

  return mutation;
};

