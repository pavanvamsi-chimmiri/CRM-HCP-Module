import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import toast from 'react-hot-toast';
import { Bell, Moon, Shield, User } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { useAppSelector } from '@/hooks/redux';

const profileSchema = z.object({
  full_name: z.string().min(2, 'Name is required'),
  email: z.string().email('Invalid email'),
});

type ProfileForm = z.infer<typeof profileSchema>;

export function SettingsPage() {
  const user = useAppSelector((s) => s.auth.user);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ProfileForm>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      full_name: user?.full_name || '',
      email: user?.email || '',
    },
  });

  const onSubmit = async (_data: ProfileForm) => {
    toast.success('Profile settings saved');
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Settings</h1>
        <p className="mt-1 text-slate-500">Manage your account and preferences</p>
      </div>

      <Card title="Profile" description="Your account information">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          <div className="flex items-center gap-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-brand-600 text-xl font-bold text-white">
              {user?.full_name?.charAt(0) || 'U'}
            </div>
            <div>
              <p className="font-medium text-slate-900">{user?.full_name}</p>
              <p className="text-sm text-slate-500">{user?.email}</p>
              {user?.is_superuser && <Badge variant="info" className="mt-1">Admin</Badge>}
            </div>
          </div>

          <Input
            label="Full Name"
            error={errors.full_name?.message}
            {...register('full_name')}
          />
          <Input
            label="Email"
            type="email"
            disabled
            error={errors.email?.message}
            {...register('email')}
          />

          <Button type="submit" isLoading={isSubmitting}>
            Save Changes
          </Button>
        </form>
      </Card>

      <Card title="Preferences">
        <div className="space-y-4">
          {[
            { icon: Bell, label: 'Email Notifications', desc: 'Receive follow-up reminders', enabled: true },
            { icon: Moon, label: 'Dark Mode', desc: 'Coming soon', enabled: false },
            { icon: Shield, label: 'Two-Factor Auth', desc: 'Coming soon', enabled: false },
            { icon: User, label: 'AI Assistant', desc: 'Groq-powered HCP insights', enabled: true },
          ].map(({ icon: Icon, label, desc, enabled }) => (
            <div key={label} className="flex items-center justify-between rounded-lg border border-slate-100 p-4">
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-brand-50 p-2">
                  <Icon className="h-5 w-5 text-brand-600" />
                </div>
                <div>
                  <p className="font-medium text-slate-900">{label}</p>
                  <p className="text-sm text-slate-500">{desc}</p>
                </div>
              </div>
              <Badge variant={enabled ? 'success' : 'default'}>
                {enabled ? 'Enabled' : 'Soon'}
              </Badge>
            </div>
          ))}
        </div>
      </Card>

      <Card title="Application">
        <dl className="grid gap-3 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-slate-500">Version</dt>
            <dd className="font-medium text-slate-900">0.1.0</dd>
          </div>
          <div>
            <dt className="text-slate-500">AI Model</dt>
            <dd className="font-medium text-slate-900">Gemma 2 9B</dd>
          </div>
          <div>
            <dt className="text-slate-500">API Endpoint</dt>
            <dd className="font-medium text-slate-900">
              {import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'}
            </dd>
          </div>
          <div>
            <dt className="text-slate-500">Environment</dt>
            <dd className="font-medium text-slate-900">Development</dd>
          </div>
        </dl>
      </Card>
    </div>
  );
}
