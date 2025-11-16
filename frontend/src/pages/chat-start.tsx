import { useCreateChat } from '@/shared/hooks/queries/chat/use-create-chat';
import { Button } from '@/shared/ui/button';
import { Input } from '@/shared/ui/input';
import { Send } from 'lucide-react';
import { useState } from 'react';
import logo from '/logo.svg';
import { SuggestionCards } from '@/features/chat/suggestion-cards';

export const ChatStartPage = () => {
  const [prompt, setPrompt] = useState('');
  const [isChatCreated, setIsChatCreated] = useState(false);

  const { mutate } = useCreateChat();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    setIsChatCreated(true);
    mutate({ question: prompt });
    setPrompt('');
  };

  const handleSuggestionSelect = (suggestion: string) => {
    setIsChatCreated(true);
    mutate({ question: suggestion });
  };

  return (
    <div className="h-full flex flex-col items-center justify-center pb-5">
      <div className="flex flex-col items-center pt-40">
        <img src={logo} alt="Logo AI" className="w-48 h-48 mb-4 opacity-50" />
        <div className="text-center max-w-xl px-6">
          <p className="text-foreground/60 text-sm leading-relaxed">
            Добро пожаловать!<br/> Я ваш AI-помощник для малого бизнеса.<br/>
            Помогу составить бизнес-план, рассчитать финансовые показатели, 
            оформить документы и ответить на вопросы по ведению бизнеса.
          </p>
        </div>
      </div>

      <div className="mt-auto w-[50vw] flex flex-col items-center">
        <SuggestionCards
          onSelect={handleSuggestionSelect}
          isVisible={!isChatCreated}
        />
        <form onSubmit={handleSubmit} className="w-full">
          <div className="flex items-center gap-3">
            <Input
              className="rounded-xl h-10"
              onChange={(e) => setPrompt(e.target.value)}
              value={prompt}
            />
            <Button
              className="bg-secondary/40 rounded-full w-10 h-10 flex items-center justify-center"
              type="submit"
            >
              <Send className="size-4 relative -left-[1px] -bottom-[1px]" />
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
