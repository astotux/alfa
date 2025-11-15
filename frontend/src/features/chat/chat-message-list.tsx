import type { Message } from '@/shared/types/message.type';

type Props = {
  messages: Message[];
};

export const ChatListMessage = ({ messages }: Props) => {
  return (
    <div className="flex-1 flex flex-col gap-2 w-[50vw] m-auto">
      {messages.map((message) => (
        <div key={message.id}>{message.content}</div>
      ))}
    </div>
  );
};
