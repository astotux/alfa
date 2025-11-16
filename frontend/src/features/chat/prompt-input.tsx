import { Button } from '@/shared/ui/button';
import { Input } from '@/shared/ui/input';
import { Send } from 'lucide-react';
import { useState, type Dispatch, type SetStateAction } from 'react';
import { useStreamLlm } from './hooks/use-stream-llm';

type Props = {
  chatId: string;
  setAnswer: Dispatch<SetStateAction<string>>;
  isLoading?: boolean;
  externalStartStream?: (prompt: string) => void;
};

export const PromptInput = ({ chatId, setAnswer, isLoading: externalIsLoading, externalStartStream }: Props) => {
  const [prompt, setPrompt] = useState<string>('');
  const { handleSubmit: startStream, isLoading: internalIsLoading } = useStreamLlm({
    chatId,
    setAnswer,
  });

  const isLoading = externalIsLoading !== undefined ? externalIsLoading : internalIsLoading;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || isLoading) return;
    if (externalStartStream) {
      externalStartStream(prompt);
    } else {
      startStream(prompt);
    }
    setPrompt('');
  };

  const isDisabled = isLoading;

  return (
    <div className="flex flex-col gap-10 ml-auto mr-auto mt-auto">
      <div className="w-[80vw] md:w-[50vw] lg:w-[50vw] absolute bottom-0 left-1/2 -translate-x-1/2">
        <form onSubmit={handleSubmit}>
          <div className="flex items-center gap-3">
            <Input
              className="rounded-xl h-10"
              onChange={(e) => setPrompt(e.target.value)}
              value={prompt}
              disabled={isDisabled}
              readOnly={isDisabled}
              placeholder={isDisabled ? "Думаю над ответом..." : ""}
            />
            <Button
              className="bg-secondary/40 rounded-full w-10 h-10 flex items-center justify-center"
              type="submit"
              disabled={isDisabled}
            >
              <Send className="size-4 relative -left-[1px] -bottom-[1px]" />
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
