import { authService } from '@/shared/api';
import { QUERY_KEYS } from '@/shared/config/query-keys';
import { ROUTES } from '@/shared/config/routes';
import type { LoginDto } from '@/shared/types/auth.type';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

export const useLogin = () => {
  const navigate = useNavigate();

  const mutate = useMutation({
    mutationKey: [QUERY_KEYS.AUTH.LOGIN],
    mutationFn: (dto: LoginDto) => authService.login(dto),
    onSuccess: () => {
      toast.success('Вы успешно вошли в аккаунт');
      navigate(ROUTES.CHAT);
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  return mutate;
};
