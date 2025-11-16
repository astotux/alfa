import {
  SidebarContent,
  Sidebar as SidebarMain,
  SidebarMenuItem,
} from '@/shared/ui/sidebar';
import { sidebarConfig } from './sidebar.config';
import { Link } from 'react-router-dom';
import logo from '/logo.svg';
import logoRiskVision from '/logo_riskvision.svg';
import { SidebarCollapse } from './sidebar-collapse';
import { useGetChats } from '@/shared/hooks/queries/chat/use-get-chats';
import { useGetRiskAnalyses } from '@/shared/hooks/queries/chat/use-get-risk-analyses';

export const Sidebar = () => {
  const { data: chatsData = [], isLoading } = useGetChats();
  const { data: riskAnalysesData = [], isLoading: isRiskAnalysesLoading } = useGetRiskAnalyses();

  return (
    <SidebarMain>
      <SidebarContent className="py-4 px-2 flex flex-col gap-6 no-scrollbar">
        <div className="flex flex-col gap-2">
          {sidebarConfig.map((item) => (
            <Link to={item.link} key={item.link}>
              <SidebarMenuItem
                className="list-none p-2! rounded-xl  hover:bg-primary/10 "
              >
                <div className="flex items-center gap-2 justify-between w-full">
                  <div className="flex items-center gap-2">
                    {item.icon && <item.icon className="size-4" />}
                    <span className="text-sm">{item.title}</span>
                  </div>
                  {item.title === 'Новый чат' && (
                    <img src={logo} alt="Logo" className="w-7 h-6 opacity-70" />
                  )}
                  {item.title === 'Анализ рисков' && (
                    <img src={logoRiskVision} alt="RiskVision Logo" className="w-7 h-6 opacity-70" />
                  )}
                </div>
              </SidebarMenuItem>
            </Link>
          ))}
        </div>
        {!isLoading && chatsData.length > 0 && (
          <SidebarCollapse data={chatsData} title="Чаты" />
        )}
        {!isRiskAnalysesLoading && riskAnalysesData.length > 0 && (
          <SidebarCollapse data={riskAnalysesData} title="Анализы рисков" />
        )}
      </SidebarContent>
    </SidebarMain>
  );
};
