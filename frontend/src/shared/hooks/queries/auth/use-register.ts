import { authService } from '@/shared/api';
import { QUERY_KEYS } from '@/shared/config/query-keys';
import { ROUTES } from '@/shared/config/routes';
import type { RegisterDto } from '@/shared/types/auth.type';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

export const useRegister = () => {
  const navigate = useNavigate();

  const mutate = useMutation({
    mutationKey: [QUERY_KEYS.AUTH.REGISTER],
    mutationFn: (dto: RegisterDto) => authService.register(dto),
    onSuccess: () => {
      navigate(ROUTES.LOGIN);
      toast.success(
        'Вы успешно зарегистрировались, пожалуйста, войдите в аккаунт'
      );
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  return mutate;
};
