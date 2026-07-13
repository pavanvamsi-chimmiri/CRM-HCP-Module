import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Activity, ClipboardList, SmilePlus, Users } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { useAppDispatch, useAppSelector } from '@/hooks/redux';
import { fetchInteractions, fetchStats } from '@/store/slices/interactionsSlice';
import { formatDate, formatInteractionType } from '@/utils';

export function DashboardPage() {
  const dispatch = useAppDispatch();
  const { stats, items, isLoading } = useAppSelector((s) => s.interactions);
  const user = useAppSelector((s) => s.auth.user);

  useEffect(() => {
    dispatch(fetchStats());
    dispatch(fetchInteractions({ limit: 5 }));
  }, [dispatch]);

  if (isLoading && !stats) {
    return <LoadingSpinner label="Loading dashboard..." />;
  }

  const statCards = [
    {
      label: 'Total Interactions',
      value: stats?.total_interactions ?? 0,
      icon: ClipboardList,
      color: 'bg-brand-50 text-brand-600',
    },
    {
      label: 'Positive Sentiment',
      value: stats?.positive_sentiment ?? 0,
      icon: SmilePlus,
      color: 'bg-emerald-50 text-emerald-600',
    },
    {
      label: 'This Month',
      value: stats?.this_month ?? 0,
      icon: Activity,
      color: 'bg-blue-50 text-blue-600',
    },
    {
      label: 'Pending Follow-ups',
      value: stats?.pending_followups ?? 0,
      icon: Users,
      color: 'bg-amber-50 text-amber-600',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          Welcome back, {user?.full_name?.split(' ')[0]}
        </h1>
        <p className="mt-1 text-slate-500">Here&apos;s your HCP interaction overview</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {statCards.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="medical-card p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-500">{label}</p>
                <p className="mt-1 text-3xl font-bold text-slate-900">{value}</p>
              </div>
              <div className={`rounded-lg p-3 ${color}`}>
                <Icon className="h-6 w-6" />
              </div>
            </div>
          </div>
        ))}
      </div>

      <Card
        title="Recent Interactions"
        description="Your latest HCP visits and calls"
        action={
          <Link to="/log-interaction">
            <Button size="sm">Log New</Button>
          </Link>
        }
      >
        {items.length === 0 ? (
          <p className="py-8 text-center text-sm text-slate-500">
            No interactions yet.{' '}
            <Link to="/log-interaction" className="text-brand-600 hover:underline">
              Log your first visit
            </Link>
          </p>
        ) : (
          <div className="divide-y divide-slate-100">
            {items.slice(0, 5).map((item) => (
              <div key={item.id} className="flex items-center justify-between py-3 first:pt-0 last:pb-0">
                <div>
                  <p className="font-medium text-slate-900">{item.doctor_name}</p>
                  <p className="text-sm text-slate-500">
                    {formatInteractionType(item.interaction_type)} · {formatDate(item.interaction_date)}
                  </p>
                </div>
                {item.sentiment && (
                  <Badge variant={item.sentiment === 'positive' ? 'success' : item.sentiment === 'negative' ? 'danger' : 'default'}>
                    {item.sentiment}
                  </Badge>
                )}
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
