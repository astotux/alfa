import { useCreateMessage } from '@/shared/hooks/queries/chat/use-create-message';
import { useCallback, useRef, useState, type Dispatch, type SetStateAction } from 'react';
import { getAccessToken } from '@/shared/api/services/auth/token.service';

export const useStreamLlm = ({
  chatId,

  setAnswer,
}: {

  chatId: string;
  setAnswer: Dispatch<SetStateAction<string>>;
}) => {
  const abortControllerRef = useRef<AbortController | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const { mutate } = useCreateMessage();

  const startStream = useCallback(
    async (prompt: string, skipUserMessage = false) => {
      let assistantText = '';
      setAnswer('');
      setIsLoading(true);
      
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      
      const abortController = new AbortController();
      abortControllerRef.current = abortController;

      if (!skipUserMessage && chatId) {
        mutate({ chatId, content: prompt, role: 'user' });
      }

      const token = getAccessToken();
      const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
      const url = new URL(`${baseUrl}/api/stream`);
      url.searchParams.append('prompt', prompt);
      if (chatId) {
        url.searchParams.append('chat_id', chatId);
      }

      try {
        console.log('Starting stream request to:', url.toString());
        const response = await fetch(url.toString(), {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
          credentials: 'include',
          signal: abortController.signal,
        });

        console.log('Response status:', response.status, response.statusText);

        if (!response.ok) {
          const errorText = await response.text();
          console.error('HTTP error response:', errorText);
          throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (!reader) {
          throw new Error('No reader available');
        }

        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          
          if (done) {
            console.log('Stream done, final text length:', assistantText.length);
            if (chatId && assistantText) {
              mutate({ chatId, content: assistantText, role: 'assistant' });
            }
            setIsLoading(false);
            break;
          }

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          
          buffer = lines.pop() || '';

          for (const line of lines) {
            const trimmedLine = line.trim();
            if (!trimmedLine) {
              continue;
            }

            if (!trimmedLine.startsWith('data: ')) {
              console.log('Skipping non-data line:', trimmedLine);
              continue;
            }

            const data = trimmedLine.slice(6).trim();

            if (data === '[DONE]') {
              console.log('Received [DONE] signal');
              if (chatId && assistantText) {
                mutate({ chatId, content: assistantText, role: 'assistant' });
              }
              setIsLoading(false);
              return;
            }

            try {
              const obj = JSON.parse(data);
              console.log('Parsed SSE data:', obj);
              
              if (obj.error) {
                console.error('Error from server:', obj.error);
                continue;
              }
              
              const text = obj?.delta;
              if (text) {
                assistantText += text;
                setAnswer((prev) => prev + text);
              }
            } catch (err) {
              console.error('Failed to parse SSE data:', data, err);
            }
          }
        }
      } catch (err: any) {
        if (err.name === 'AbortError') {
          console.log('Stream aborted');
          setIsLoading(false);
          return;
        }
        console.error('Stream error', err);
        setIsLoading(false);
      }
    },
    [chatId, setAnswer, mutate]
  );

  const handleSubmit = async (prompt: string) => {
    if (isLoading) return;
    startStream(prompt);
  };

  return { handleSubmit, startStream, isLoading };
};
