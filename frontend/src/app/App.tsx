import { ChatPage, ChatStartPage, RegisterPage } from '@/pages';
import { LoginPage } from '@/pages';
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
          <Route index path={ROUTES.CHAT} element={<ChatStartPage />} />
          <Route index path={ROUTES.CHAT_ID} element={<ChatPage />} />
          <Route path={ROUTES.RISK_VISION} element={<ChatStartPage />} />
          <Route path={ROUTES.RISK_VISION_ID} element={<ChatPage />} />
        </Route>
        <Route path={ROUTES.LOGIN} element={<LoginPage />} />
        <Route path={ROUTES.REGISTER} element={<RegisterPage />} />
        <Route path="*" element={<Navigate to={ROUTES.LOGIN} />} />
      </Routes>
      <Toaster richColors />
    </QueryClientProvider>
  );
}

export default App;
