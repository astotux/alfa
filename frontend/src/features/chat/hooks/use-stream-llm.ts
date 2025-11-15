import { useCreateMessage } from '@/shared/hooks/queries/chat/use-create-message';
import type { CreateMessageDto } from '@/shared/types/chat.type';
import { useCallback, useRef, type Dispatch, type SetStateAction } from 'react';

export const useStreamLlm = ({
  chatId,

  setAnswer,
}: {

  chatId: string;
  setAnswer: Dispatch<SetStateAction<string>>;
}) => {
  const esRef = useRef<EventSource | null>(null);

  const { mutate } = useCreateMessage();

  const startStream = useCallback(
    (prompt: string, skipUserMessage = false) => {
      let assistantText = '';
      setAnswer('');
      if (esRef.current) {
        esRef.current.close();
      }
      const url = `http://127.0.0.1:8000/api/stream?prompt=${encodeURIComponent(
        prompt
      )}`;
      const es = new EventSource(url);
      esRef.current = es;

      if (!skipUserMessage) {
        mutate({ chatId, content: prompt, role: 'user' });
      }

      es.onmessage = (e) => {
        const raw = e.data;

        if (raw === '[DONE]') {
          mutate({ chatId, content: assistantText, role: 'assistant' });
          es.close();
          return;
        }

        try {
          const obj = JSON.parse(raw);
          const text = obj?.delta;
          if (text) {
            assistantText += text;
            setAnswer((prev) => prev + text);
          }
        } catch (err) {
          console.error('Failed to parse SSE data:', raw, err);
        }
      };

      es.onerror = (err) => {
        console.error('EventSource error', err);
        es.close();
      };
    },
    [chatId, setAnswer, mutate]
  );

  const handleSubmit = async (prompt: string) => {
    startStream(prompt);
  };

  return { handleSubmit, startStream };
};
