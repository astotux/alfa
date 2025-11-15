import type { Message } from '@/shared/types/message.type';
import { cn } from '@/shared/utils/cn';
import { useEffect, useRef } from 'react';
import Markdown from 'react-markdown';

type Props = {
  messages: Message[];
  answer: string;
};

export const ChatListMessage = ({ messages, answer }: Props) => {
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, answer]);

  return (
    <div className="flex-1 max-h-[83vh] overflow-y-auto flex flex-col gap-10 p-4 no-scrollbar w-[80vw] md:w-[50vw] lg:w-[50vw] mx-auto">
      {messages.map((message) => (
        <div
          key={message.id}
          className={cn(
            ' px-4 py-2 rounded-xl break-words',
            message.role === 'user'
              ? 'self-end bg-accent/40 max-w-[70%]'
              : 'self-start max-w-[80%] md:max-w-[70%] bg-secondary/20'
          )}
        >
          <Markdown>{message.content}</Markdown>
        </div>
      ))}

      {answer && messages[messages.length - 1].role === 'user' && (
        <div className="max-w-[70%] px-4 py-2 rounded-xl break-words self-start bg-secondary/20">
          <Markdown>{answer}</Markdown>
        </div>
      )}
      <div ref={messagesEndRef} />
    </div>
  );
};
