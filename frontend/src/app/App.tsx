import Chat from '@/features/chat/chat';
import { ROUTES } from '@/shared/config/routes';
import { Navigate, Route, Routes } from 'react-router-dom';

function App() {
  return (
    <Routes>
      <Route index path={ROUTES.CHAT} element={<Chat />} />
      <Route path={ROUTES.LOGIN} element={<div>Login</div>} />
      <Route path={ROUTES.REGISTER} element={<div>Register</div>} />
      <Route path="*" element={<Navigate to={ROUTES.CHAT} />} />
    </Routes>
  );
}

export default App;
