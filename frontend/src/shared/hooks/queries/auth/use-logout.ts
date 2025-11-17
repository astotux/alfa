import { authService } from '@/shared/api';
import { QUERY_KEYS } from '@/shared/config/query-keys';
import { ROUTES } from '@/shared/config/routes';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

export const useLogout = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  return useMutation({
    mutationKey: [QUERY_KEYS.AUTH.LOGOUT],
    mutationFn: () => authService.logout(),
    onSuccess: () => {
      queryClient.clear();
      toast.success('Вы вышли из аккаунта');
      navigate(ROUTES.LOGIN, { replace: true });
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });
};

