import { ROUTES } from '@/shared/config/routes';
import { SquarePen, AlertTriangle } from 'lucide-react';

export const sidebarConfig = [
  {
    title: 'Новый чат',
    link: ROUTES.CHAT,
    icon: SquarePen,
  },
  {
    title: 'Анализ рисков',
    link: ROUTES.RISK_VISION,
    icon: AlertTriangle,
  },
];
