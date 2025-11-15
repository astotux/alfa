import { axiosClassic } from '@/shared/api/api';
import type { CreateMessageDto } from '@/shared/types/chat.type';
import {
  useCallback,
  useEffect,
  useRef,
  type Dispatch,
  type SetStateAction,
} from 'react';

export const useStreamLlm = ({
  firstMessage,

  setAnswer,
}: {
  firstMessage: string;
  chatId: string;
  setAnswer: Dispatch<SetStateAction<string>>;
  answer: string;
  createMessage: (data: CreateMessageDto) => void;
}) => {
  const esRef = useRef<EventSource | null>(null);

  const startStream = useCallback(
    (prompt: string) => {
      if (esRef.current) {
        esRef.current.close();
      }
      const url = `http://127.0.0.1:8000/api/stream?prompt=${encodeURIComponent(
        prompt
      )}`;
      const es = new EventSource(url);
      esRef.current = es;

      es.onmessage = (e) => {
        try {
          const obj = JSON.parse(e.data);

          const text = obj?.choices?.[0]?.delta?.content;

          setAnswer((prev) => prev + text);
        } catch (err) {
          console.log('raw data:', e.data);
        }
      };

      es.addEventListener('done', (e) => {
        console.log('stream done');
        // createMessage({ chatId, content: answer, role: 'assistant' });
        es.close();
      });

      es.onerror = (err) => {
        console.error('EventSource error', err);
        es.close();
      };
    },
    [prompt]
  );

  const handleSubmit = async (prompt: string) => {
    startStream(prompt);
  };

 

  return { handleSubmit };
};
