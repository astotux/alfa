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

const getRiskSeverity = (text: string): 'high' | 'medium' | 'low' | null => {
  const textLower = text.toLowerCase();
  if (text.includes('🔴') || textLower.includes('высокий')) {
    return 'high';
  }
  if (text.includes('🟡') || textLower.includes('средний')) {
    return 'medium';
  }
  if (text.includes('🟢') || textLower.includes('низкий')) {
    return 'low';
  }
  return null;
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
    <div className="flex-1 max-h-[83vh] overflow-y-auto flex flex-col gap-6 p-6 no-scrollbar w-[80vw] md:w-[50vw] lg:w-[50vw] mx-auto">
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
              'rounded-xl leading-normal break-words',
              message.role === 'user'
                ? 'bg-accent/40 px-4 py-2'
                : 'max-w-[80%] md:max-w-[70%] bg-gradient-to-br from-background to-secondary/30 border border-primary/20 shadow-lg px-6 py-4'
            )}
          >
            <div className="risk-content-wrapper">
              <Markdown
                components={{
                  p: ({ children, ...props }) => {
                    const extractText = (node: any): string => {
                      if (typeof node === 'string') return node;
                      if (typeof node === 'number') return String(node);
                      if (Array.isArray(node)) return node.map(extractText).join('');
                      if (node?.props?.children) return extractText(node.props.children);
                      return '';
                    };
                    const text = extractText(children);
                    const severity = getRiskSeverity(text);
                    if (severity) {
                      return (
                        <div
                          className={cn(
                            'risk-block p-4 my-4 rounded-lg',
                            severity === 'high' && 'bg-red-500/10 border-l-4 border-red-500',
                            severity === 'medium' && 'bg-yellow-500/10 border-l-4 border-yellow-500',
                            severity === 'low' && 'bg-green-500/10 border-l-4 border-green-500'
                          )}
                        >
                          <p {...props} className="m-0 leading-relaxed">
                            {children}
                          </p>
                        </div>
                      );
                    }
                    return <p {...props} className="leading-relaxed">{children}</p>;
                  },
                  h1: ({ children, ...props }) => {
                    return <h1 {...props} className="text-2xl font-bold mb-4 mt-4 leading-tight">{children}</h1>;
                  },
                  h2: ({ children, ...props }) => {
                    return <h2 {...props} className="text-xl font-semibold mb-3 mt-3 leading-tight">{children}</h2>;
                  },
                  h3: ({ children, ...props }) => {
                    const extractText = (node: any): string => {
                      if (typeof node === 'string') return node;
                      if (typeof node === 'number') return String(node);
                      if (Array.isArray(node)) return node.map(extractText).join('');
                      if (node?.props?.children) return extractText(node.props.children);
                      return '';
                    };
                    const text = extractText(children);
                    const severity = getRiskSeverity(text);
                    if (severity) {
                      return (
                        <h3
                          {...props}
                          className={cn(
                            'risk-heading font-semibold mb-3 mt-2',
                            severity === 'high' && 'text-red-600 dark:text-red-400',
                            severity === 'medium' && 'text-yellow-600 dark:text-yellow-400',
                            severity === 'low' && 'text-green-600 dark:text-green-400'
                          )}
                        >
                          {children}
                        </h3>
                      );
                    }
                    return <h3 {...props} className="text-xl mb-3 mt-2">{children}</h3>;
                  },
                  h4: ({ children, ...props }) => {
                    return <h2 {...props} className="text-xl font-semibold mb-3 mt-3 leading-tight">{children}</h2>;
                  },
                  li: ({ children, ...props }) => {
                    const extractText = (node: any): string => {
                      if (typeof node === 'string') return node;
                      if (typeof node === 'number') return String(node);
                      if (Array.isArray(node)) return node.map(extractText).join('');
                      if (node?.props?.children) return extractText(node.props.children);
                      return '';
                    };
                    const text = extractText(children);
                    const severity = getRiskSeverity(text);
                    if (severity) {
                      return (
                        <li
                          {...props}
                          className={cn(
                            'risk-list-item my-3 p-3 rounded',
                            severity === 'high' && 'bg-red-500/10 border-l-3 border-red-500',
                            severity === 'medium' && 'bg-yellow-500/10 border-l-3 border-yellow-500',
                            severity === 'low' && 'bg-green-500/10 border-l-3 border-green-500'
                          )}
                        >
                          {children}
                        </li>
                      );
                    }
                    return <li {...props} className="my-2">{children}</li>;
                  },
                }}
              >
                {message.content}
              </Markdown>
            </div>
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
        <div className="relative self-start max-w-[70%] flex items-end gap-2">
          <div className="px-6 py-4 rounded-xl leading-normal break-words max-w-[80%] md:max-w-[70%] bg-gradient-to-br from-background to-secondary/30 border border-primary/20 shadow-lg">
            <div className="risk-content-wrapper">
              <Markdown
                components={{
                  p: ({ children, ...props }) => {
                    const extractText = (node: any): string => {
                      if (typeof node === 'string') return node;
                      if (typeof node === 'number') return String(node);
                      if (Array.isArray(node)) return node.map(extractText).join('');
                      if (node?.props?.children) return extractText(node.props.children);
                      return '';
                    };
                    const text = extractText(children);
                    const severity = getRiskSeverity(text);
                    if (severity) {
                      return (
                        <div
                          className={cn(
                            'risk-block p-4 my-4 rounded-lg',
                            severity === 'high' && 'bg-red-500/10 border-l-4 border-red-500',
                            severity === 'medium' && 'bg-yellow-500/10 border-l-4 border-yellow-500',
                            severity === 'low' && 'bg-green-500/10 border-l-4 border-green-500'
                          )}
                        >
                          <p {...props} className="m-0 leading-relaxed">
                            {children}
                          </p>
                        </div>
                      );
                    }
                    return <p {...props} className="mb-3 leading-relaxed">{children}</p>;
                  },
                  h1: ({ children, ...props }) => {
                    return <h1 {...props} className="text-2xl font-bold mb-4 mt-4 leading-tight">{children}</h1>;
                  },
                  h2: ({ children, ...props }) => {
                    return <h2 {...props} className="text-xl font-semibold mb-3 mt-3 leading-tight">{children}</h2>;
                  },
                  li: ({ children, ...props }) => {
                    const extractText = (node: any): string => {
                      if (typeof node === 'string') return node;
                      if (typeof node === 'number') return String(node);
                      if (Array.isArray(node)) return node.map(extractText).join('');
                      if (node?.props?.children) return extractText(node.props.children);
                      return '';
                    };
                    const text = extractText(children);
                    const severity = getRiskSeverity(text);
                    if (severity) {
                      return (
                        <li
                          {...props}
                          className={cn(
                            'risk-list-item my-3 p-3 rounded',
                            severity === 'high' && 'bg-red-500/10 border-l-4 border-red-500',
                            severity === 'medium' && 'bg-yellow-500/10 border-l-4 border-yellow-500',
                            severity === 'low' && 'bg-green-500/10 border-l-4 border-green-500'
                          )}
                        >
                          {children}
                        </li>
                      );
                    }
                    return <li {...props} className="my-2">{children}</li>;
                  },
                }}
              >
                {answer}
              </Markdown>
            </div>
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
