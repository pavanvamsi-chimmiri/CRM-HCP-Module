import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Stethoscope } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { authApi } from '@/services/api/auth';
import { getErrorMessage } from '@/services/api/client';
import { useAppDispatch } from '@/hooks/redux';
import { setUser } from '@/store/slices/authSlice';

const loginSchema = z.object({
  email: z.string().email('Enter a valid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

type LoginForm = z.infer<typeof loginSchema>;

export function LoginPage() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginForm) => {
    try {
      const tokens = await authApi.login(data);
      localStorage.setItem('access_token', tokens.access_token);
      localStorage.setItem('refresh_token', tokens.refresh_token);
      const user = await authApi.getMe();
      dispatch(setUser(user));
      toast.success('Welcome back!');
      navigate('/dashboard');
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  return (
    <div className="flex min-h-screen">
      <div className="hidden w-1/2 bg-gradient-to-br from-brand-700 to-brand-900 lg:flex lg:flex-col lg:justify-center lg:px-16">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-white/10">
            <Stethoscope className="h-7 w-7 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">HCP CRM</h1>
            <p className="text-brand-200">Healthcare Professional Management</p>
          </div>
        </div>
        <p className="mt-8 max-w-md text-lg text-brand-100">
          Track doctor interactions, manage follow-ups, and grow your medical sales relationships.
        </p>
      </div>

      <div className="flex flex-1 items-center justify-center px-6">
        <div className="w-full max-w-md">
          <div className="mb-8 lg:hidden">
            <div className="flex items-center gap-2">
              <Stethoscope className="h-8 w-8 text-brand-600" />
              <h1 className="text-xl font-bold text-brand-900">HCP CRM</h1>
            </div>
          </div>

          <h2 className="text-2xl font-bold text-slate-900">Sign in</h2>
          <p className="mt-1 text-sm text-slate-500">Enter your credentials to access your account</p>

          <form onSubmit={handleSubmit(onSubmit)} className="mt-8 space-y-5">
            <Input
              label="Email"
              type="email"
              placeholder="you@company.com"
              error={errors.email?.message}
              {...register('email')}
            />
            <Input
              label="Password"
              type="password"
              placeholder="••••••••"
              error={errors.password?.message}
              {...register('password')}
            />
            <Button type="submit" className="w-full" size="lg" isLoading={isSubmitting}>
              Sign In
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-500">
            Don&apos;t have an account?{' '}
            <Link to="/register" className="font-medium text-brand-600 hover:text-brand-700">
              Register
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export function RegisterPage() {
  const navigate = useNavigate();

  const registerSchema = z
    .object({
      full_name: z.string().min(2, 'Name must be at least 2 characters'),
      email: z.string().min(1, 'Email is required').email('Enter a valid email'),
      password: z.string().min(8, 'Password must be at least 8 characters'),
      confirmPassword: z.string().min(1, 'Please confirm your password'),
    })
    .refine((d) => d.password === d.confirmPassword, {
      message: 'Passwords do not match',
      path: ['confirmPassword'],
    });

  type RegisterForm = z.infer<typeof registerSchema>;

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterForm>({ resolver: zodResolver(registerSchema) });

  const onSubmit = async (data: RegisterForm) => {
    try {
      await authApi.register({
        email: data.email,
        password: data.password,
        full_name: data.full_name,
      });
      toast.success('Account created! Please sign in.');
      navigate('/login');
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center px-6">
      <div className="w-full max-w-md">
        <h2 className="text-2xl font-bold text-slate-900">Create account</h2>
        <p className="mt-1 text-sm text-slate-500">Register for HCP CRM access</p>

        <form onSubmit={handleSubmit(onSubmit)} className="mt-8 space-y-5">
          <Input label="Full Name" error={errors.full_name?.message} {...register('full_name')} />
          <Input label="Email" type="email" error={errors.email?.message} {...register('email')} />
          <Input label="Password" type="password" error={errors.password?.message} {...register('password')} />
          <Input label="Confirm Password" type="password" error={errors.confirmPassword?.message} {...register('confirmPassword')} />
          <Button type="submit" className="w-full" size="lg" isLoading={isSubmitting}>
            Register
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-slate-500">
          Already have an account?{' '}
          <Link to="/login" className="font-medium text-brand-600 hover:text-brand-700">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
