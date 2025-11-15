import type { Message } from '@/shared/types/message.type';
import { Button } from '@/shared/ui/button';
import { Input } from '@/shared/ui/input';
import { Send } from 'lucide-react';
import { useState } from 'react';
import { useStreamLlm } from './hooks/use-stream-llm';
import { useCreateMessage } from '@/shared/hooks/queries/chat/use-create-message';
import Markdown from 'react-markdown';

type Props = {
  messages: Message[];
  chatId: string;
};

export const PromptInput = ({ messages, chatId }: Props) => {
  const [prompt, setPrompt] = useState<string>('');
  const [answer, setAnswer] = useState<string>('');

  const { mutate } = useCreateMessage();

  const { handleSubmit: startStream } = useStreamLlm({
    firstMessage: messages[messages.length - 1]?.content || '',
    chatId,
    setAnswer,
    answer,
    createMessage: mutate,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    startStream(prompt);
    mutate({ content: prompt, role: 'user', chatId });
    setPrompt('');
  };

  return (
    <div className="flex flex-col gap-10">
      {answer && (
        <div className="message">
          <Markdown>{answer}</Markdown>
        </div>
      )}
      <div className="m-auto w-[50vw]">
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
