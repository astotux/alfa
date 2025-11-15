import { ChatListMessage } from '@/features/chat/chat-message-list';
import { PromptInput } from '@/features/chat/prompt-input';
import { useGetChat } from '@/shared/hooks/queries/chat/use-get-chat';
import { useState } from 'react';
import { useParams } from 'react-router-dom';

export const ChatPage = () => {
  const { id } = useParams();

  const { data } = useGetChat(id || '');

  const [answer, setAnswer] = useState<string>('');

  return (
    <div className="flex flex-col pt-2 h-full relative">
      <ChatListMessage answer={answer} messages={data?.messages || []} />
      <PromptInput setAnswer={setAnswer} chatId={id || ''} />
    </div>
  );
};
