import { useEffect, useState } from 'react';
import { Search, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { Card } from '@/components/ui/Card';
import { Select } from '@/components/ui/Select';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { EmptyState } from '@/components/ui/EmptyState';
import { useAppDispatch, useAppSelector } from '@/hooks/redux';
import { deleteInteraction, fetchInteractions } from '@/store/slices/interactionsSlice';
import { formatDate, formatInteractionType, formatTime, INTERACTION_TYPES, SENTIMENT_OPTIONS } from '@/utils';
import { Link } from 'react-router-dom';
import type { InteractionType, Sentiment } from '@/types';

export function HistoryPage() {
  const dispatch = useAppDispatch();
  const { items, total, isLoading } = useAppSelector((s) => s.interactions);

  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState<InteractionType | ''>('');
  const [sentimentFilter, setSentimentFilter] = useState<Sentiment | ''>('');

  useEffect(() => {
    dispatch(
      fetchInteractions({
        doctor_name: search || undefined,
        interaction_type: typeFilter || undefined,
        sentiment: sentimentFilter || undefined,
        limit: 50,
      })
    );
  }, [dispatch, search, typeFilter, sentimentFilter]);

  const handleDelete = async (id: string, doctorName: string) => {
    if (!confirm(`Delete interaction with ${doctorName}?`)) return;
    try {
      await dispatch(deleteInteraction(id)).unwrap();
      toast.success('Interaction deleted');
    } catch (error) {
      toast.error(typeof error === 'string' ? error : 'Failed to delete');
    }
  };

  const sentimentVariant = (s: string | null) => {
    if (s === 'positive') return 'success' as const;
    if (s === 'negative') return 'danger' as const;
    if (s === 'mixed') return 'warning' as const;
    return 'default' as const;
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Interaction History</h1>
          <p className="mt-1 text-slate-500">{total} total interactions</p>
        </div>
        <Link to="/log-interaction">
          <Button>Log Interaction</Button>
        </Link>
      </div>

      <Card>
        <div className="mb-6 grid gap-4 sm:grid-cols-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search by doctor name..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="medical-input pl-9"
            />
          </div>
          <Select
            options={[
              { value: '', label: 'All types' },
              ...INTERACTION_TYPES.map((t) => ({ value: t.value, label: t.label })),
            ]}
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value as InteractionType | '')}
          />
          <Select
            options={[
              { value: '', label: 'All sentiments' },
              ...SENTIMENT_OPTIONS.map((s) => ({ value: s.value, label: s.label })),
            ]}
            value={sentimentFilter}
            onChange={(e) => setSentimentFilter(e.target.value as Sentiment | '')}
          />
        </div>

        {isLoading ? (
          <LoadingSpinner label="Loading interactions..." />
        ) : items.length === 0 ? (
          <EmptyState
            title="No interactions found"
            description="Start logging your HCP visits to build your history."
            action={
              <Link to="/log-interaction">
                <Button>Log First Interaction</Button>
              </Link>
            }
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-100 text-xs font-medium uppercase tracking-wider text-slate-500">
                  <th className="pb-3 pr-4">Doctor</th>
                  <th className="pb-3 pr-4">Type</th>
                  <th className="pb-3 pr-4">Date & Time</th>
                  <th className="pb-3 pr-4">Topics</th>
                  <th className="pb-3 pr-4">Sentiment</th>
                  <th className="pb-3">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {items.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-50">
                    <td className="py-4 pr-4">
                      <p className="font-medium text-slate-900">{item.doctor_name}</p>
                      {item.outcome && (
                        <p className="mt-0.5 max-w-xs truncate text-xs text-slate-500">{item.outcome}</p>
                      )}
                    </td>
                    <td className="py-4 pr-4 text-slate-600">
                      {formatInteractionType(item.interaction_type)}
                    </td>
                    <td className="py-4 pr-4 text-slate-600">
                      {formatDate(item.interaction_date)}
                      <br />
                      <span className="text-xs text-slate-400">{formatTime(item.interaction_time)}</span>
                    </td>
                    <td className="py-4 pr-4">
                      <div className="flex flex-wrap gap-1">
                        {item.topics?.slice(0, 2).map((t) => (
                          <Badge key={t} variant="info">{t}</Badge>
                        ))}
                        {(item.topics?.length ?? 0) > 2 && (
                          <Badge>+{item.topics!.length - 2}</Badge>
                        )}
                      </div>
                    </td>
                    <td className="py-4 pr-4">
                      {item.sentiment ? (
                        <Badge variant={sentimentVariant(item.sentiment)}>{item.sentiment}</Badge>
                      ) : (
                        <span className="text-slate-400">—</span>
                      )}
                    </td>
                    <td className="py-4">
                      <button
                        onClick={() => handleDelete(item.id, item.doctor_name)}
                        className="rounded-lg p-2 text-slate-400 transition-colors hover:bg-red-50 hover:text-red-600"
                        title="Delete"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
