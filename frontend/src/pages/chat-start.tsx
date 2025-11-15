import { useCreateChat } from '@/shared/hooks/queries/chat/use-create-chat';
import { Button } from '@/shared/ui/button';
import { Input } from '@/shared/ui/input';
import { Send } from 'lucide-react';
import { useState } from 'react';

export const ChatStartPage = () => {
  const [prompt, setPrompt] = useState('');

  const { mutate } = useCreateChat();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    mutate({ question: prompt });
    setPrompt('');
  };

  return (
    <div className="h-full flex flex-col items-center justify-center pb-5">
      <div className="flex flex-col items-center pt-40">
        <h1 className="text-6xl font-bold text-primary/10">Logo AI</h1>
      </div>

      <div className="mt-auto w-[50vw]">
        <form onSubmit={handleSubmit}>
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
