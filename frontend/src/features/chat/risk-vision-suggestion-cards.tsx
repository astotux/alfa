import { Card } from '@/shared/ui/card';
import { cn } from '@/shared/utils/cn';
import { useMemo, useState } from 'react';
import { ChevronDown } from 'lucide-react';

type RiskVisionSuggestionCardProps = {
  text: string;
  onClick: () => void;
};

const RiskVisionSuggestionCard = ({ text, onClick }: RiskVisionSuggestionCardProps) => {
  return (
    <Card
      className={cn(
        'cursor-pointer transition-all gap-1 hover:bg-primary/5 hover:border-primary/50 hover:shadow-md',
        'px-4 py-3 min-h-[80px] flex flex-col items-center justify-center text-center relative',
        'active:scale-[0.98]'
      )}
      onClick={onClick}
    >
      <p className="text-sm text-foreground/70 leading-relaxed mb-2">{text}</p>
      <ChevronDown className="size-4 text-foreground/40 mt-1" />
    </Card>
  );
};

type Props = {
  onSelect: (text: string) => void;
  isVisible: boolean;
};

const allRiskVisionSuggestions = [
  'Хочу сделать резкий шаг в бизнесе: ',
  'Хочу попробовать стартап: ',
  'Планирую открыть новый бизнес: ',
  'Хочу расширить существующий бизнес: ',
  'Рассматриваю инвестиции в: ',
  'Хочу запустить новый продукт: ',
  'Планирую изменить бизнес-модель: ',
  'Хочу выйти на новый рынок: ',
  'Рассматриваю партнерство с: ',
  'Планирую масштабировать бизнес: ',
  'Хочу диверсифицировать деятельность: ',
  'Рассматриваю франшизу: ',
  'Планирую автоматизировать процессы: ',
  'Хочу изменить стратегию развития: ',
];

const getRandomSuggestions = (count: number, exclude: string[] = []): string[] => {
  const available = allRiskVisionSuggestions.filter(s => !exclude.includes(s));
  const shuffled = [...available].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, count);
};

export const RiskVisionSuggestionCards = ({ onSelect, isVisible }: Props) => {
  const suggestions = useMemo(() => {
    return getRandomSuggestions(3);
  }, [isVisible]);

  const handleSelect = (suggestion: string) => {
    onSelect(suggestion);
  };

  if (!isVisible || suggestions.length === 0) return null;

  return (
    <div className="w-[50vw] mb-8 flex gap-4">
      {suggestions.map((suggestion, index) => (
        <div key={`${suggestion}-${index}`} className="flex-1 min-w-0">
          <RiskVisionSuggestionCard
            text={suggestion}
            onClick={() => handleSelect(suggestion)}
          />
        </div>
      ))}
    </div>
  );
};

