import { Card } from '@/shared/ui/card';
import { cn } from '@/shared/utils/cn';
import { useMemo } from 'react';

type SuggestionCardProps = {
  text: string;
  onClick: () => void;
};

const SuggestionCard = ({ text, onClick }: SuggestionCardProps) => {
  return (
    <Card
      className={cn(
        'cursor-pointer transition-all hover:bg-primary/5 hover:border-primary/50 hover:shadow-md',
        'px-4 py-3 min-h-[80px] flex items-center justify-center text-center',
        'active:scale-[0.98]'
      )}
      onClick={onClick}
    >
      <p className="text-sm text-foreground/70 leading-relaxed">{text}</p>
    </Card>
  );
};

type Props = {
  onSelect: (text: string) => void;
  isVisible: boolean;
};

const allSuggestions = [
  'Помоги составить бизнес-план для открытия кафе',
  'Нужно рассчитать себестоимость продукции для моего магазина',
  'Как правильно оформить договор с поставщиком?',
  'Помоги подобрать цветовую схему для логотипа компании',
  'Как составить маркетинговую стратегию для малого бизнеса?',
  'Нужна помощь в выборе системы налогообложения',
  'Помоги рассчитать рентабельность нового проекта',
  'Как правильно вести учет расходов и доходов?',
  'Помоги составить коммерческое предложение для клиентов',
  'Нужна помощь в выборе банка для бизнес-счета',
  'Как оформить сотрудника на работу правильно?',
  'Помоги составить техническое задание для разработки сайта',
  'Как рассчитать точку безубыточности для бизнеса?',
  'Помоги выбрать CRM-систему для малого бизнеса',
  'Как составить план продаж на следующий квартал?',
];

const getRandomSuggestions = (count: number): string[] => {
  const shuffled = [...allSuggestions].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, count);
};

export const SuggestionCards = ({ onSelect, isVisible }: Props) => {
  const suggestions = useMemo(() => getRandomSuggestions(3), []);

  if (!isVisible) return null;

  return (
    <div className="w-[50vw] mb-8 flex gap-4">
      {suggestions.map((suggestion, index) => (
        <div key={index} className="flex-1 min-w-0">
          <SuggestionCard
            text={suggestion}
            onClick={() => onSelect(suggestion)}
          />
        </div>
      ))}
    </div>
  );
};

