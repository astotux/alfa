import { ROUTES } from '@/shared/config/routes';
import { useGetProfile } from '@/shared/hooks/queries/user/use-get-profile';
import type { AxiosError } from 'axios';
import { Navigate } from 'react-router-dom';

export const PrivateRoute = ({ children }: { children: React.ReactNode }) => {
  const { isLoading, error, data } = useGetProfile();

  if (isLoading) return null;

  if (error && (error as AxiosError).status === 401) {
    return <Navigate to={ROUTES.LOGIN} replace />;
  }

  if (!data) return <Navigate to={ROUTES.LOGIN} replace />;

  return <>{children}</>;
};
