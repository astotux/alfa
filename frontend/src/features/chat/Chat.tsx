import { cn } from '@/shared/utils/cn';
import { useState, useRef, useEffect } from 'react';

type MessageType = {
  type: 'user' | 'bot';
  text: string;
};

export default function Chat() {
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [input, setInput] = useState('');
  const esRef = useRef<EventSource | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const scrollToBottom = () => {
    if (!messagesEndRef.current) return;

    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const startStream = (prompt: string) => {
    if (esRef.current) {
      esRef.current.close();
    }

    setMessages((prev) => [...prev, { type: 'user', text: prompt }]);

    setMessages((prev) => [...prev, { type: 'bot', text: '' }]);

    const url = `http://127.0.0.1:8000/api/stream?prompt=${encodeURIComponent(
      prompt
    )}`;
    const es = new EventSource(url);
    esRef.current = es;

    es.onmessage = (e) => {
      try {
        const obj = JSON.parse(e.data);

        const text = obj?.choices?.[0]?.delta?.content;

        if (text) {
          setMessages((prev) => {
            const newMessages = [...prev];
            const lastMessage = newMessages[newMessages.length - 1];
            if (lastMessage && lastMessage.type === 'bot') {
              newMessages[newMessages.length - 1] = {
                ...lastMessage,
                text: lastMessage.text + text,
              };
            }
            return newMessages;
          });
        }
      } catch (err) {
        console.log('raw data:', e.data);
      }
    };

    es.addEventListener('done', (e) => {
      console.log('stream done');
      es.close();
    });

    es.onerror = (err) => {
      console.error('EventSource error', err);
      es.close();
    };
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      startStream(input);
      setInput('');
    }
  };

  return (
    <div className="flex flex-col h-screen w-[60%] py-5 ml-auto mr-auto rounded-lg overflow-hidden">
      <div className="flex-1 overflow-y-auto p-5 flex flex-col gap-4 bg-white">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-[#999]">
            Начните диалог, отправив сообщение
          </div>
        ) : (
          messages.map((msg, index) => (
            <div
              key={index}
              className={cn('flex max-w-[75%]', {
                'self-end justify-end': msg.type === 'user',
                'self-start justify-start': msg.type === 'bot',
              })}
            >
              <div
                className={cn(
                  'py-3 px-4 rounded-lg wrap-break-word whitespace-pre-wrap ',
                  {
                    'bg-red-700 text-white rounded-br-sm': msg.type === 'user',
                    'bg-[#e8e8e8] text-[#333] rounded-bl-sm':
                      msg.type === 'bot',
                  }
                )}
              >
                {msg.text || '...'}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>
      <form
        className="flex p-4 bg-white border-t border-[#e0e0e0]"
        onSubmit={handleSubmit}
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Введите сообщение..."
          className="flex-1 px-4 py-3 border-2 border-gray-300 rounded-full text-sm outline-none transition-border duration-300"
        />
        <button
          type="submit"
          className="px-6 py-3 bg-[#EF3124] text-white border-none rounded-full text-sm font-semibold cursor-pointer transition-all duration-200"
        >
          Отправить
        </button>
      </form>
    </div>
  );
}
