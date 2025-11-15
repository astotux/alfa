import { ChatListMessage } from '@/features/chat/chat-message-list';
import { PromptInput } from '@/features/chat/prompt-input';
import { useGetChat } from '@/shared/hooks/queries/chat/use-get-chat';
import { useParams } from 'react-router-dom';

export const ChatPage = () => {
  const { id } = useParams();

  const { data } = useGetChat(id || '');

  return (
    <div className="h-full flex flex-col pb-5">
      <ChatListMessage messages={data?.messages || []} />

      <PromptInput messages={data?.messages || []} chatId={id || ''} />
    </div>
  );
};
