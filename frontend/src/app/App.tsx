import Chat from '@/features/chat/chat';
import { Register } from '@/pages';
import { Login } from '@/pages';
import { ROUTES } from '@/shared/config/routes';
import { Navigate, Outlet, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'sonner';
import { PrivateRoute } from './private-route';
import { Layout } from '@/widgets';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Routes>
        <Route
          element={
            <PrivateRoute>
              <Layout>
                <Outlet />
              </Layout>
            </PrivateRoute>
          }
        >
          <Route index path={ROUTES.CHAT} element={<Chat />} />
        </Route>
        <Route path={ROUTES.LOGIN} element={<Login />} />
        <Route path={ROUTES.REGISTER} element={<Register />} />
        <Route path="*" element={<Navigate to={ROUTES.LOGIN} />} />
      </Routes>
      <Toaster richColors />
    </QueryClientProvider>
  );
}

export default App;
