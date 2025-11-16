import { useCreateChat } from '@/shared/hooks/queries/chat/use-create-chat';
import { Button } from '@/shared/ui/button';
import { Input } from '@/shared/ui/input';
import { Send } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import logo from '/logo.svg';
import logoRiskVision from '/logo_riskvision.svg';
import { SuggestionCards } from '@/features/chat/suggestion-cards';
import { RiskVisionSuggestionCards } from '@/features/chat/risk-vision-suggestion-cards';
import { ROUTES } from '@/shared/config/routes';

export const ChatStartPage = () => {
  const [prompt, setPrompt] = useState('');
  const [isChatCreated, setIsChatCreated] = useState(false);
  const [showRiskVisionSuggestions, setShowRiskVisionSuggestions] = useState(true);
  const location = useLocation();
  
  const isRiskVision = location.pathname.startsWith(ROUTES.RISK_VISION);
  const { mutate, isPending: isLoading } = useCreateChat(isRiskVision ? ROUTES.RISK_VISION : ROUTES.CHAT);

  useEffect(() => {
    if (location.pathname === ROUTES.CHAT || location.pathname === ROUTES.RISK_VISION) {
      setPrompt('');
      setIsChatCreated(false);
      setShowRiskVisionSuggestions(true);
    }
  }, [location.pathname]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || isLoading) return;
    setIsChatCreated(true);
    mutate({ question: prompt, chat_type: isRiskVision ? 'risk_vision' : 'general' });
    setPrompt('');
  };

  const handleSuggestionSelect = (suggestion: string) => {
    if (isLoading) return;
    setIsChatCreated(true);
    mutate({ question: suggestion, chat_type: isRiskVision ? 'risk_vision' : 'general' });
  };

  const handleRiskVisionSuggestionSelect = (suggestion: string) => {
    setPrompt(suggestion);
    setShowRiskVisionSuggestions(false);
  };

  return (
    <div className="h-full flex flex-col items-center justify-center pb-5">
      <div className="flex flex-col items-center pt-40">
        <img src={isRiskVision ? logoRiskVision : logo} alt="Logo AI" className="w-48 h-48 mb-4 opacity-50" />
        <div className="text-center max-w-3xl">
          <p className="text-foreground/70 text-base leading-relaxed">
            {isRiskVision ? (
              <>
                Добро пожаловать в RiskVision!<br/> Я проведу глубокий анализ вашей бизнес-идеи, существующего бизнеса или плана действий.<br/>
                Выявлю все потенциальные риски и слабые точки по категориям: финансовые, рыночные, операционные, юридические и стратегические риски.
              </>
            ) : (
              <>
                Добро пожаловать!<br/> Я ваш AI-помощник для малого бизнеса.<br/>
                Помогу составить бизнес-план, рассчитать финансовые показатели,<br/>
                оформить документы и ответить на вопросы по ведению бизнеса.
              </>
            )}
          </p>
        </div>
      </div>

      <div className="mt-auto w-[50vw] flex flex-col items-center">
        {!isRiskVision && (
          <SuggestionCards
            onSelect={handleSuggestionSelect}
            isVisible={!isChatCreated}
          />
        )}
        {isRiskVision && (
          <RiskVisionSuggestionCards
            onSelect={handleRiskVisionSuggestionSelect}
            isVisible={showRiskVisionSuggestions && !isChatCreated}
          />
        )}
        <form onSubmit={handleSubmit} className="w-full">
          <div className="flex items-center gap-3">
            <Input
              className="rounded-xl h-10"
              onChange={(e) => setPrompt(e.target.value)}
              value={prompt}
              disabled={isLoading}
              readOnly={isLoading}
              placeholder={isLoading ? "Думаю над ответом..." : isRiskVision ? "Опишите вашу бизнес-идею, существующий бизнес или план действий..." : ""}
            />
            <Button
              className="bg-secondary/40 rounded-full w-10 h-10 flex items-center justify-center"
              type="submit"
              disabled={isLoading}
            >
              <Send className="size-4 relative -left-[1px] -bottom-[1px]" />
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
