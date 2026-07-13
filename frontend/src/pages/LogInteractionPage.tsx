import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Textarea } from '@/components/ui/Textarea';
import { Button } from '@/components/ui/Button';
import { useAppDispatch, useAppSelector } from '@/hooks/redux';
import { createInteraction } from '@/store/slices/interactionsSlice';
import { INTERACTION_TYPES, SENTIMENT_OPTIONS } from '@/utils';

const logInteractionSchema = z.object({
  doctor_name: z.string().min(2, 'Doctor name is required'),
  interaction_type: z.enum(['in_person', 'phone_call', 'video_call', 'email', 'conference', 'other']),
  interaction_date: z.string().min(1, 'Date is required'),
  interaction_time: z.string().min(1, 'Time is required'),
  topics: z.string().optional(),
  sentiment: z.enum(['positive', 'neutral', 'negative', 'mixed']).optional().or(z.literal('')),
  outcome: z.string().optional(),
  samples: z.string().optional(),
});

type LogInteractionForm = z.infer<typeof logInteractionSchema>;

export function LogInteractionPage() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const isSubmitting = useAppSelector((s) => s.interactions.isSubmitting);

  const today = new Date().toISOString().split('T')[0];
  const now = new Date().toTimeString().slice(0, 5);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<LogInteractionForm>({
    resolver: zodResolver(logInteractionSchema),
    defaultValues: {
      interaction_date: today,
      interaction_time: now,
      interaction_type: 'in_person',
    },
  });

  const onSubmit = async (data: LogInteractionForm) => {
    const timeFormatted = data.interaction_time.length === 5
      ? `${data.interaction_time}:00`
      : data.interaction_time;

    try {
      await dispatch(
        createInteraction({
          doctor_name: data.doctor_name,
          interaction_type: data.interaction_type,
          interaction_date: data.interaction_date,
          interaction_time: timeFormatted,
          topics: data.topics
            ? data.topics.split(',').map((t) => t.trim()).filter(Boolean)
            : [],
          sentiment: data.sentiment || null,
          outcome: data.outcome || null,
          samples: data.samples || null,
        })
      ).unwrap();

      toast.success('Interaction logged successfully!');
      reset();
      navigate('/history');
    } catch (error) {
      toast.error(typeof error === 'string' ? error : 'Failed to log interaction');
    }
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Log Interaction</h1>
        <p className="mt-1 text-slate-500">Record a new HCP visit, call, or meeting</p>
      </div>

      <Card title="Interaction Details" description="Fill in the visit information below">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          <Input
            label="Doctor Name *"
            placeholder="Dr. Jane Smith"
            error={errors.doctor_name?.message}
            {...register('doctor_name')}
          />

          <div className="grid gap-5 sm:grid-cols-2">
            <Select
              label="Interaction Type *"
              options={INTERACTION_TYPES.map((t) => ({ value: t.value, label: t.label }))}
              error={errors.interaction_type?.message}
              {...register('interaction_type')}
            />
            <Select
              label="Sentiment"
              options={[
                { value: '', label: 'Select sentiment' },
                ...SENTIMENT_OPTIONS.map((s) => ({ value: s.value, label: s.label })),
              ]}
              {...register('sentiment')}
            />
          </div>

          <div className="grid gap-5 sm:grid-cols-2">
            <Input
              label="Date *"
              type="date"
              error={errors.interaction_date?.message}
              {...register('interaction_date')}
            />
            <Input
              label="Time *"
              type="time"
              error={errors.interaction_time?.message}
              {...register('interaction_time')}
            />
          </div>

          <Input
            label="Topics"
            placeholder="Efficacy, Safety, Dosing (comma-separated)"
            {...register('topics')}
          />

          <Textarea
            label="Outcome"
            placeholder="Summary of interaction outcome..."
            rows={3}
            {...register('outcome')}
          />

          <Textarea
            label="Samples Provided"
            placeholder="List samples or materials shared..."
            rows={2}
            {...register('samples')}
          />

          <div className="flex gap-3 pt-2">
            <Button type="submit" isLoading={isSubmitting}>
              Save Interaction
            </Button>
            <Button type="button" variant="secondary" onClick={() => reset()}>
              Clear Form
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
