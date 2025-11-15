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
import { useLogin } from '@/shared/hooks/queries/auth/use-login';

const loginSchema = z.object({
  username: z.string({ error: 'Введите логин' }),

  password: z
    .string({ error: 'Введите пароль' })
    .min(6, { error: 'Пароль должен быть не менее 6 символов' }),
});

type LoginFormData = z.infer<typeof loginSchema>;

export const LoginForm = () => {
  const form = useForm({
    mode: 'onSubmit',
    resolver: zodResolver(loginSchema),
  });

  const { mutate } = useLogin();

  const onSubmit = (data: LoginFormData) => {
    console.log(data);
    mutate(data);
  };

  return (
    <div className="h-screen flex items-center justify-center">
      <FormCard
        title="Войти"
        description=""
        footer={
          <div className="">
            Нет аккаунта?{' '}
            <Link className="text-primary" to={ROUTES.REGISTER}>
              Зарегистрироваться
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
              Войти
            </Button>
          </form>
        </Form>
      </FormCard>
    </div>
  );
};
