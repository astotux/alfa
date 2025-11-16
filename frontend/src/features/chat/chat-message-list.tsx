import type { Message } from '@/shared/types/message.type';
import { cn } from '@/shared/utils/cn';
import { useEffect, useRef, useState } from 'react';
import Markdown from 'react-markdown';
import { Copy, Check } from 'lucide-react';
import { Button } from '@/shared/ui/button';
import { toast } from 'sonner';

type Props = {
  messages: Message[];
  answer: string;
};

export const ChatListMessage = ({ messages, answer }: Props) => {
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, answer]);

  const handleCopy = async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(id);
      toast.success('Текст скопирован в буфер обмена');
      setTimeout(() => setCopiedId(null), 2000);
    } catch (error) {
      toast.error('Не удалось скопировать текст');
    }
  };

  return (
    <div className="flex-1 max-h-[83vh] overflow-y-auto flex flex-col gap-10 p-4 no-scrollbar w-[80vw] md:w-[50vw] lg:w-[50vw] mx-auto">
      {messages.map((message) => (
        <div
          key={message.id}
          className={cn(
            'relative',
            message.role === 'user' ? 'self-end flex justify-end' : 'self-start flex items-end gap-2'
          )}
        >
          <div
            className={cn(
              'px-4 py-2 rounded-xl leading-normal break-words',
              message.role === 'user'
                ? 'bg-accent/40'
                : 'max-w-[80%] md:max-w-[70%] bg-secondary/20'
            )}
          >
            <Markdown>{message.content}</Markdown>
          </div>
          {message.role !== 'user' && (
            <Button
              variant="ghost"
              size="icon-sm"
              onClick={() => handleCopy(message.content, message.id)}
              className="h-7 w-7 bg-background border shadow-sm hover:bg-accent"
            >
              {copiedId === message.id ? (
                <Check className="h-4 w-4" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
            </Button>
          )}
        </div>
      ))}

      {answer && messages[messages.length - 1].role === 'user' && (
        <div className="relative self-start max-w-[70%]">
          <div className="px-4 py-2 rounded-xl break-words bg-secondary/20">
            <Markdown>{answer}</Markdown>
          </div>
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={() => handleCopy(answer, 'answer')}
            className="h-7 w-7 bg-background border shadow-sm hover:bg-accent"
          >
            {copiedId === 'answer' ? (
              <Check className="h-4 w-4" />
            ) : (
              <Copy className="h-4 w-4" />
            )}
          </Button>
        </div>
      )}
      <div ref={messagesEndRef} />
    </div>
  );
};
