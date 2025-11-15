import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/shared/ui/form';
import { Input } from '@/shared/ui/input';
import { Button } from '@/shared/ui/button';
import { FormCard } from './form-card';
import { Link } from 'react-router-dom';
import { ROUTES } from '@/shared/config/routes';
import { useRegister } from '@/shared/hooks/queries/auth/use-register';

const registerSchema = z.object({
  username: z.string({ error: 'Введите логин' }),
  email: z.email({ error: 'Введите почту' }),
  password: z
    .string({ error: 'Введите пароль' })
    .min(6, { error: 'Пароль должен быть не менее 6 символов' }),
});

type RegisterFormData = z.infer<typeof registerSchema>;

export const RegisterForm = () => {
  const form = useForm({
    mode: 'onSubmit',
    resolver: zodResolver(registerSchema),
  });

  const { mutate } = useRegister();

  const onSubmit = (data: RegisterFormData) => {
    mutate(data);
  };

  return (
    <div className="h-screen flex items-center justify-center">
      <FormCard
        title="Зарегистрироваться"
        description=""
        footer={
          <div className="">
            Уже есть аккаунт?{' '}
            <Link className="text-primary" to={ROUTES.LOGIN}>
              Вход
            </Link>
          </div>
        }
      >
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)}>
            <div className="flex flex-col gap-4 mb-3">
              <FormField
                control={form.control}
                name="username"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-[14px]!">Логин</FormLabel>
                    <FormControl>
                      <Input placeholder="Мой логин" {...field} />
                    </FormControl>
                    <FormMessage className="text-[14px]!" />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-[14px]!">Почта</FormLabel>
                    <FormControl>
                      <Input
                        type="email"
                        placeholder="example@mail.ru"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage className="text-[14px]!" />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-[14px]!">Пароль</FormLabel>
                    <FormControl>
                      <Input type="password" placeholder="*******" {...field} />
                    </FormControl>
                    <FormMessage className="text-[14px]!" />
                  </FormItem>
                )}
              />
            </div>
            <Button className="w-full" type="submit">
              Зарегистрироваться
            </Button>
          </form>
        </Form>
      </FormCard>
    </div>
  );
};
