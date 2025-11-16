import { ChatListMessage } from '@/features';
import { PromptInput } from '@/features';
import { useGetChat } from '@/shared/hooks/queries/chat/use-get-chat';
import { useStreamLlm } from '@/features/chat/hooks/use-stream-llm';
import { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';

export const ChatPage = () => {
  const { id } = useParams();
  const hasAutoStartedRef = useRef(false);

  const { data } = useGetChat(id || '');

  const [answer, setAnswer] = useState<string>('');
  const { startStream, isLoading } = useStreamLlm({
    chatId: id || '',
    setAnswer,
  });

  useEffect(() => {
    if (
      data?.messages &&
      data.messages.length === 1 &&
      !hasAutoStartedRef.current
    ) {
      const userMessage = data.messages[0];

      if (userMessage.role === 'user') {
        hasAutoStartedRef.current = true;
        startStream(userMessage.content, true);
      }
    }
  }, [data, startStream]);

  return (
    <div className="flex flex-col pt-2 h-full relative">
      <ChatListMessage answer={answer} messages={data?.messages || []} />
      <PromptInput 
        setAnswer={setAnswer} 
        chatId={id || ''} 
        isLoading={isLoading}
        externalStartStream={startStream}
      />
    </div>
  );
};
