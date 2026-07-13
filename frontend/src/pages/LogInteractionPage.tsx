import { useCallback, useEffect, useRef, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate, useParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  Calendar,
  Clock,
  FileText,
  Mic,
  MicOff,
  Pencil,
  Save,
  Sparkles,
  Stethoscope,
  Trash2,
  Users,
  X,
} from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Textarea } from '@/components/ui/Textarea';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { useAppDispatch, useAppSelector } from '@/hooks/redux';
import {
  clearCurrent,
  createInteraction,
  deleteInteraction,
  fetchInteraction,
  fetchInteractions,
  summarizeVoiceNote,
  updateInteraction,
} from '@/store/slices/interactionsSlice';
import { INTERACTION_TYPES, SENTIMENT_OPTIONS } from '@/utils';
import type { Interaction, InteractionType, Sentiment } from '@/types';

const logInteractionSchema = z.object({
  doctor_name: z.string().min(2, 'Doctor name is required'),
  interaction_type: z.enum([
    'in_person',
    'phone_call',
    'video_call',
    'email',
    'conference',
    'other',
  ]),
  interaction_date: z.string().min(1, 'Date is required'),
  interaction_time: z.string().min(1, 'Time is required'),
  attendees: z.string().optional(),
  topics: z.string().optional(),
  materials_shared: z.string().optional(),
  samples: z.string().optional(),
  sentiment: z
    .enum(['positive', 'neutral', 'negative', 'mixed'])
    .optional()
    .or(z.literal('')),
  outcome: z.string().optional(),
  follow_up: z.string().optional(),
  voice_note: z.string().optional(),
});

type LogInteractionForm = z.infer<typeof logInteractionSchema>;

function getDefaultValues(): LogInteractionForm {
  const today = new Date().toISOString().split('T')[0];
  const now = new Date().toTimeString().slice(0, 5);
  return {
    doctor_name: '',
    interaction_type: 'in_person',
    interaction_date: today,
    interaction_time: now,
    attendees: '',
    topics: '',
    materials_shared: '',
    samples: '',
    sentiment: '',
    outcome: '',
    follow_up: '',
    voice_note: '',
  };
}

function interactionToFormValues(interaction: Interaction): LogInteractionForm {
  return {
    doctor_name: interaction.doctor_name,
    interaction_type: interaction.interaction_type,
    interaction_date: interaction.interaction_date,
    interaction_time: interaction.interaction_time.slice(0, 5),
    attendees: interaction.attendees ?? '',
    topics: interaction.topics?.join(', ') ?? '',
    materials_shared: interaction.materials_shared ?? '',
    samples: interaction.samples ?? '',
    sentiment: interaction.sentiment ?? '',
    outcome: interaction.outcome ?? '',
    follow_up: interaction.follow_up ?? '',
    voice_note: '',
  };
}

function formToPayload(data: LogInteractionForm) {
  const timeFormatted =
    data.interaction_time.length === 5 ? `${data.interaction_time}:00` : data.interaction_time;

  return {
    doctor_name: data.doctor_name,
    interaction_type: data.interaction_type as InteractionType,
    interaction_date: data.interaction_date,
    interaction_time: timeFormatted,
    attendees: data.attendees || null,
    topics: data.topics
      ? data.topics.split(',').map((t) => t.trim()).filter(Boolean)
      : [],
    materials_shared: data.materials_shared || null,
    sentiment: (data.sentiment || null) as Sentiment | null,
    outcome: data.outcome || null,
    samples: data.samples || null,
    follow_up: data.follow_up || null,
  };
}

export function LogInteractionPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();

  const { isSubmitting, isSummarizing, isLoading, items } = useAppSelector((s) => s.interactions);

  const [editingId, setEditingId] = useState<string | null>(id ?? null);
  const [isReadOnly, setIsReadOnly] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [summaryPreview, setSummaryPreview] = useState<string | null>(null);
  const [showEditPicker, setShowEditPicker] = useState(false);

  const recognitionRef = useRef<SpeechRecognition | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    getValues,
    watch,
    formState: { errors, isDirty },
  } = useForm<LogInteractionForm>({
    resolver: zodResolver(logInteractionSchema),
    defaultValues: getDefaultValues(),
  });

  const voiceNote = watch('voice_note');

  const loadInteraction = useCallback(
    async (interactionId: string, readOnly = false) => {
      try {
        const interaction = await dispatch(fetchInteraction(interactionId)).unwrap();
        reset(interactionToFormValues(interaction));
        setEditingId(interactionId);
        setIsReadOnly(readOnly);
        setSummaryPreview(null);
        navigate(`/log-interaction/${interactionId}`, { replace: true });
      } catch (error) {
        toast.error(typeof error === 'string' ? error : 'Failed to load interaction');
      }
    },
    [dispatch, navigate, reset]
  );

  useEffect(() => {
    if (id) {
      loadInteraction(id, false);
    } else {
      dispatch(clearCurrent());
      setEditingId(null);
      setIsReadOnly(false);
    }
  }, [id, loadInteraction, dispatch]);

  useEffect(() => {
    dispatch(fetchInteractions({ limit: 20 }));
  }, [dispatch]);

  const handleSave = async (data: LogInteractionForm) => {
    const payload = formToPayload(data);

    try {
      if (editingId) {
        await dispatch(updateInteraction({ id: editingId, payload })).unwrap();
        toast.success('Interaction updated successfully');
      } else {
        const created = await dispatch(createInteraction(payload)).unwrap();
        setEditingId(created.id);
        navigate(`/log-interaction/${created.id}`, { replace: true });
        toast.success('Interaction saved successfully');
      }
      setIsReadOnly(false);
    } catch (error) {
      toast.error(typeof error === 'string' ? error : 'Failed to save interaction');
    }
  };

  const handleDelete = async () => {
    if (!editingId) return;
    if (!confirm('Delete this interaction? This action cannot be undone.')) return;

    try {
      await dispatch(deleteInteraction(editingId)).unwrap();
      toast.success('Interaction deleted');
      handleClear();
      navigate('/log-interaction');
    } catch (error) {
      toast.error(typeof error === 'string' ? error : 'Failed to delete interaction');
    }
  };

  const handleClear = () => {
    reset(getDefaultValues());
    setEditingId(null);
    setIsReadOnly(false);
    setSummaryPreview(null);
    setShowEditPicker(false);
    dispatch(clearCurrent());
    if (id) {
      navigate('/log-interaction', { replace: true });
    }
  };

  const handleEdit = () => {
    if (editingId) {
      setIsReadOnly(false);
      toast.success('Edit mode enabled');
      return;
    }
    setShowEditPicker((prev) => !prev);
  };

  const handleSummarize = async () => {
    const note = getValues('voice_note')?.trim();
    if (!note) {
      toast.error('Add a voice note or transcript before summarizing');
      return;
    }

    try {
      const result = await dispatch(
        summarizeVoiceNote({ text: note, doctorName: getValues('doctor_name') || undefined })
      ).unwrap();

      setSummaryPreview(result.summary);

      if (result.outcome_highlight) {
        setValue('outcome', result.outcome_highlight, { shouldDirty: true });
      }
      if (result.key_points.length > 0) {
        const existing = getValues('topics')?.trim();
        const points = result.key_points.join(', ');
        setValue('topics', existing ? `${existing}, ${points}` : points, { shouldDirty: true });
      }

      toast.success('Voice note summarized');
    } catch (error) {
      toast.error(typeof error === 'string' ? error : 'Failed to summarize voice note');
    }
  };

  const toggleRecording = () => {
    const win = window as Window & {
      webkitSpeechRecognition?: new () => SpeechRecognition;
    };
    const SpeechRecognitionCtor = win.SpeechRecognition ?? win.webkitSpeechRecognition;

    if (!SpeechRecognitionCtor) {
      toast.error('Speech recognition is not supported in this browser');
      return;
    }

    if (isRecording && recognitionRef.current) {
      recognitionRef.current.stop();
      setIsRecording(false);
      return;
    }

    const recognition = new SpeechRecognitionCtor();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    let transcript = getValues('voice_note') || '';

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let interim = '';
      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        const chunk = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          transcript += `${chunk} `;
        } else {
          interim += chunk;
        }
      }
      setValue('voice_note', `${transcript}${interim}`.trim(), { shouldDirty: true });
    };

    recognition.onerror = () => {
      setIsRecording(false);
      toast.error('Voice capture failed. Type your note instead.');
    };

    recognition.onend = () => {
      setIsRecording(false);
    };

    recognitionRef.current = recognition;
    recognition.start();
    setIsRecording(true);
    toast.success('Listening… speak your visit notes');
  };

  if (isLoading && id) {
    return <LoadingSpinner label="Loading interaction..." />;
  }

  const isEditing = Boolean(editingId);
  const formDisabled = isReadOnly;

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-50">
              <Stethoscope className="h-5 w-5 text-brand-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Log Interaction</h1>
              <p className="text-sm text-slate-500">
                Record HCP visits, calls, and follow-up details
              </p>
            </div>
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            <Badge variant={isEditing ? 'info' : 'default'}>
              {isEditing ? (isReadOnly ? 'Viewing' : 'Editing') : 'New Entry'}
            </Badge>
            {isDirty && !isReadOnly && <Badge variant="warning">Unsaved changes</Badge>}
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit(handleSave)} className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <Card
            title="Healthcare Professional"
            description="Doctor and attendee information"
          >
            <div className="grid gap-5 sm:grid-cols-2">
              <Input
                label="Doctor Name *"
                placeholder="Dr. Jane Smith"
                error={errors.doctor_name?.message}
                disabled={formDisabled}
                {...register('doctor_name')}
              />
              <Input
                label="Attendees"
                placeholder="Nurse, PA, office staff..."
                disabled={formDisabled}
                {...register('attendees')}
              />
            </div>
          </Card>

          <Card title="Visit Details" description="When and how the interaction occurred">
            <div className="grid gap-5 sm:grid-cols-2">
              <Select
                label="Interaction Type *"
                options={INTERACTION_TYPES.map((t) => ({ value: t.value, label: t.label }))}
                error={errors.interaction_type?.message}
                disabled={formDisabled}
                {...register('interaction_type')}
              />
              <Select
                label="Sentiment"
                options={[
                  { value: '', label: 'Select sentiment' },
                  ...SENTIMENT_OPTIONS.map((s) => ({ value: s.value, label: s.label })),
                ]}
                disabled={formDisabled}
                {...register('sentiment')}
              />
              <div className="relative">
                <Calendar className="pointer-events-none absolute left-3 top-[38px] h-4 w-4 text-slate-400" />
                <Input
                  label="Date *"
                  type="date"
                  className="pl-9"
                  error={errors.interaction_date?.message}
                  disabled={formDisabled}
                  {...register('interaction_date')}
                />
              </div>
              <div className="relative">
                <Clock className="pointer-events-none absolute left-3 top-[38px] h-4 w-4 text-slate-400" />
                <Input
                  label="Time *"
                  type="time"
                  className="pl-9"
                  error={errors.interaction_time?.message}
                  disabled={formDisabled}
                  {...register('interaction_time')}
                />
              </div>
            </div>
          </Card>

          <Card title="Discussion & Materials" description="Topics covered and resources shared">
            <div className="space-y-5">
              <Input
                label="Topics"
                placeholder="Efficacy, Safety, Dosing, Patient adherence (comma-separated)"
                disabled={formDisabled}
                {...register('topics')}
              />
              <div className="grid gap-5 sm:grid-cols-2">
                <Textarea
                  label="Materials Shared"
                  placeholder="Brochures, clinical data, digital resources..."
                  rows={3}
                  disabled={formDisabled}
                  {...register('materials_shared')}
                />
                <Textarea
                  label="Samples Distributed"
                  placeholder="Product samples, starter kits, vouchers..."
                  rows={3}
                  disabled={formDisabled}
                  {...register('samples')}
                />
              </div>
            </div>
          </Card>

          <Card title="Outcome & Follow-up" description="Results and next steps">
            <div className="space-y-5">
              <Textarea
                label="Outcome"
                placeholder="Summary of interaction results, commitments, and physician feedback..."
                rows={4}
                disabled={formDisabled}
                {...register('outcome')}
              />
              <Textarea
                label="Follow-up"
                placeholder="Scheduled callbacks, sample requests, meeting dates..."
                rows={3}
                disabled={formDisabled}
                {...register('follow_up')}
              />
            </div>
          </Card>
        </div>

        <div className="space-y-6">
          <Card
            title="Voice Note"
            description="Dictate or paste visit notes for AI summarization"
            action={
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={toggleRecording}
                disabled={formDisabled}
                className={isRecording ? 'text-red-600' : ''}
              >
                {isRecording ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                {isRecording ? 'Stop' : 'Record'}
              </Button>
            }
          >
            <Textarea
              label="Voice Note Transcript"
              placeholder="Tap Record to dictate, or type your raw visit notes here..."
              rows={8}
              disabled={formDisabled}
              {...register('voice_note')}
            />
            <p className="mt-2 text-xs text-slate-400">
              {voiceNote?.length ?? 0} characters
            </p>

            {summaryPreview && (
              <div className="mt-4 rounded-lg border border-brand-100 bg-brand-50/50 p-4">
                <div className="mb-2 flex items-center gap-2 text-sm font-medium text-brand-700">
                  <Sparkles className="h-4 w-4" />
                  AI Summary
                </div>
                <p className="text-sm leading-relaxed text-slate-700">{summaryPreview}</p>
              </div>
            )}
          </Card>

          {showEditPicker && (
            <Card title="Load Interaction" description="Select a record to edit">
              <div className="max-h-64 space-y-2 overflow-y-auto">
                {items.length === 0 ? (
                  <p className="text-sm text-slate-500">No interactions found</p>
                ) : (
                  items.map((item) => (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => {
                        loadInteraction(item.id, false);
                        setShowEditPicker(false);
                      }}
                      className="flex w-full items-center justify-between rounded-lg border border-slate-100 px-3 py-2.5 text-left text-sm transition-colors hover:border-brand-200 hover:bg-brand-50"
                    >
                      <div>
                        <p className="font-medium text-slate-900">{item.doctor_name}</p>
                        <p className="text-xs text-slate-500">{item.interaction_date}</p>
                      </div>
                      <Pencil className="h-4 w-4 text-slate-400" />
                    </button>
                  ))
                )}
              </div>
            </Card>
          )}

          <Card>
            <div className="space-y-3">
              <Button
                type="submit"
                className="w-full"
                size="lg"
                isLoading={isSubmitting}
                disabled={formDisabled}
              >
                <Save className="h-4 w-4" />
                {isEditing ? 'Save Changes' : 'Save'}
              </Button>

              <Button
                type="button"
                variant="secondary"
                className="w-full"
                onClick={handleEdit}
              >
                <Pencil className="h-4 w-4" />
                {isReadOnly ? 'Enable Edit' : 'Edit'}
              </Button>

              <Button
                type="button"
                variant="secondary"
                className="w-full"
                onClick={handleSummarize}
                isLoading={isSummarizing}
                disabled={formDisabled || !voiceNote?.trim()}
              >
                <Sparkles className="h-4 w-4" />
                Summarize Voice Note
              </Button>

              <div className="grid grid-cols-2 gap-3 pt-1">
                <Button type="button" variant="ghost" onClick={handleClear}>
                  <X className="h-4 w-4" />
                  Clear
                </Button>
                <Button
                  type="button"
                  variant="danger"
                  onClick={handleDelete}
                  disabled={!editingId}
                >
                  <Trash2 className="h-4 w-4" />
                  Delete
                </Button>
              </div>
            </div>

            <div className="mt-5 space-y-2 border-t border-slate-100 pt-4">
              <div className="flex items-center gap-2 text-xs text-slate-500">
                <Users className="h-3.5 w-3.5" />
                Attendees, materials, and follow-ups are saved with each record
              </div>
              <div className="flex items-center gap-2 text-xs text-slate-500">
                <FileText className="h-3.5 w-3.5" />
                Use Summarize to auto-fill outcome and topics from voice notes
              </div>
            </div>
          </Card>
        </div>
      </form>
    </div>
  );
}
