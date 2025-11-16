import { Button } from '@/shared/ui/button';
import { Input } from '@/shared/ui/input';
import { Send } from 'lucide-react';
import { useState, type Dispatch, type SetStateAction } from 'react';
import { useStreamLlm } from './hooks/use-stream-llm';

type Props = {
  chatId: string;
  setAnswer: Dispatch<SetStateAction<string>>;
};

export const PromptInput = ({ chatId, setAnswer }: Props) => {
  const [prompt, setPrompt] = useState<string>('');
  const { handleSubmit: startStream, isLoading } = useStreamLlm({
    chatId,
    setAnswer,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || isLoading) return;
    startStream(prompt);
    setPrompt('');
  };

  return (
    <div className="flex flex-col gap-10 ml-auto mr-auto mt-auto">
      <div className="w-[80vw] md:w-[50vw] lg:w-[50vw] absolute bottom-0 left-1/2 -translate-x-1/2">
        <form onSubmit={handleSubmit}>
          <div className="flex items-center gap-3">
            <Input
              className="rounded-xl h-10"
              onChange={(e) => setPrompt(e.target.value)}
              value={prompt}
              disabled={isLoading}
              placeholder={isLoading ? "Думаю над ответом..." : ""}
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
