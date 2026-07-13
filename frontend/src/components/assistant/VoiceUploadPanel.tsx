import { useCallback, useRef, useState } from 'react';
import {
  CheckCircle2,
  FileAudio,
  Loader2,
  Mic,
  Sparkles,
  Upload,
  X,
} from 'lucide-react';
import toast from 'react-hot-toast';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { assistantApi } from '@/services/api/assistant';
import { getErrorMessage } from '@/services/api/client';
import type { AssistantFormFields, VoiceProcessingStage, VoiceUploadResponse } from '@/types/assistant';

interface VoiceUploadPanelProps {
  onApplyFields: (fields: AssistantFormFields) => void;
  onTranscript?: (transcript: string) => void;
  disabled?: boolean;
}

const ACCEPTED_TYPES = [
  'audio/mpeg',
  'audio/mp3',
  'audio/wav',
  'audio/x-wav',
  'audio/webm',
  'audio/ogg',
  'audio/mp4',
  'audio/x-m4a',
  'audio/m4a',
];

const ACCEPTED_EXTENSIONS = '.mp3,.wav,.m4a,.webm,.ogg';
const MAX_FILE_SIZE = 25 * 1024 * 1024;

const STAGE_LABELS: Record<VoiceProcessingStage, string> = {
  idle: 'Ready',
  uploading: 'Uploading audio…',
  transcribing: 'Transcribing with Groq Whisper…',
  extracting: 'Summarizing & extracting fields…',
  done: 'Complete',
  error: 'Failed',
};

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function isAcceptedFile(file: File): boolean {
  const ext = file.name.split('.').pop()?.toLowerCase();
  const validExt = ['mp3', 'wav', 'm4a', 'webm', 'ogg'].includes(ext ?? '');
  return ACCEPTED_TYPES.includes(file.type) || validExt;
}

export function VoiceUploadPanel({ onApplyFields, onTranscript, disabled }: VoiceUploadPanelProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [stage, setStage] = useState<VoiceProcessingStage>('idle');
  const [result, setResult] = useState<VoiceUploadResponse | null>(null);

  const reset = () => {
    setSelectedFile(null);
    setStage('idle');
    setResult(null);
    if (inputRef.current) inputRef.current.value = '';
  };

  const processFile = useCallback(
    async (file: File) => {
      if (!isAcceptedFile(file)) {
        toast.error('Please upload MP3, WAV, M4A, WebM, or OGG audio');
        return;
      }
      if (file.size > MAX_FILE_SIZE) {
        toast.error('Audio file must be under 25 MB');
        return;
      }

      setSelectedFile(file);
      setResult(null);
      setStage('uploading');

      try {
        setStage('transcribing');
        const response = await assistantApi.uploadVoice(file);

        setStage('extracting');
        setResult(response);
        onApplyFields(response.form_fields);
        onTranscript?.(response.transcript);
        setStage('done');

        if (response.is_complete) {
          toast.success('Voice note processed — form filled automatically');
        } else {
          toast.success('Form updated — some fields may need review');
        }
      } catch (error) {
        setStage('error');
        toast.error(getErrorMessage(error));
      }
    },
    [onApplyFields, onTranscript]
  );

  const handleFileSelect = (files: FileList | null) => {
    const file = files?.[0];
    if (file) processFile(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (disabled || stage === 'uploading' || stage === 'transcribing' || stage === 'extracting') return;
    handleFileSelect(e.dataTransfer.files);
  };

  const isProcessing = stage === 'uploading' || stage === 'transcribing' || stage === 'extracting';

  return (
    <Card
      title="Voice Upload"
      description="Upload audio → Whisper transcribe → summarize → auto-fill"
      action={
        selectedFile ? (
          <button
            type="button"
            onClick={reset}
            disabled={isProcessing}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
            title="Clear"
          >
            <X className="h-4 w-4" />
          </button>
        ) : (
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-50">
            <Mic className="h-4 w-4 text-brand-600" />
          </div>
        )
      }
    >
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED_EXTENSIONS}
        className="hidden"
        onChange={(e) => handleFileSelect(e.target.files)}
        disabled={disabled || isProcessing}
      />

      <div
        onDragOver={(e) => {
          e.preventDefault();
          if (!disabled && !isProcessing) setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => !disabled && !isProcessing && inputRef.current?.click()}
        className={`cursor-pointer rounded-xl border-2 border-dashed px-4 py-8 text-center transition-colors ${
          isDragging
            ? 'border-brand-400 bg-brand-50'
            : 'border-slate-200 bg-slate-50 hover:border-brand-300 hover:bg-brand-50/50'
        } ${disabled || isProcessing ? 'pointer-events-none opacity-60' : ''}`}
      >
        <Upload className="mx-auto h-8 w-8 text-brand-500" />
        <p className="mt-3 text-sm font-medium text-slate-700">
          Drop audio file or click to browse
        </p>
        <p className="mt-1 text-xs text-slate-500">MP3, WAV, M4A, WebM, OGG · Max 25 MB</p>
      </div>

      {selectedFile && (
        <div className="mt-4 flex items-center gap-3 rounded-lg border border-slate-100 bg-white px-3 py-2.5">
          <FileAudio className="h-5 w-5 shrink-0 text-brand-600" />
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium text-slate-900">{selectedFile.name}</p>
            <p className="text-xs text-slate-500">{formatFileSize(selectedFile.size)}</p>
          </div>
          {stage === 'done' && <CheckCircle2 className="h-5 w-5 text-emerald-500" />}
          {isProcessing && <Loader2 className="h-5 w-5 animate-spin text-brand-600" />}
        </div>
      )}

      {stage !== 'idle' && (
        <div className="mt-4 flex items-center gap-2 rounded-lg bg-brand-50 px-3 py-2">
          {isProcessing ? (
            <Loader2 className="h-4 w-4 animate-spin text-brand-600" />
          ) : stage === 'done' ? (
            <CheckCircle2 className="h-4 w-4 text-emerald-600" />
          ) : (
            <Sparkles className="h-4 w-4 text-brand-600" />
          )}
          <span className="text-sm text-brand-800">{STAGE_LABELS[stage]}</span>
        </div>
      )}

      {result && (
        <div className="mt-4 space-y-4">
          <div className="rounded-lg border border-slate-100 bg-slate-50 p-3">
            <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-slate-500">
              Transcript
            </p>
            <p className="text-sm leading-relaxed text-slate-700">{result.transcript}</p>
          </div>

          <div className="rounded-lg border border-brand-100 bg-brand-50/50 p-3">
            <div className="mb-1.5 flex items-center gap-1.5 text-xs font-medium uppercase tracking-wide text-brand-600">
              <Sparkles className="h-3.5 w-3.5" />
              Summary
            </div>
            <p className="text-sm leading-relaxed text-slate-700">{result.summary}</p>
            {result.key_points.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1.5">
                {result.key_points.map((point) => (
                  <Badge key={point} variant="info">
                    {point}
                  </Badge>
                ))}
              </div>
            )}
          </div>

          <div className="rounded-lg border border-emerald-100 bg-emerald-50/50 p-3">
            <p className="mb-2 text-xs font-medium uppercase tracking-wide text-emerald-700">
              Extracted & Applied
            </p>
            <div className="grid grid-cols-2 gap-2 text-xs">
              {result.form_fields.doctor_name && (
                <div>
                  <span className="text-slate-500">Doctor</span>
                  <p className="font-medium text-slate-800">{result.form_fields.doctor_name}</p>
                </div>
              )}
              {result.form_fields.topics?.length ? (
                <div>
                  <span className="text-slate-500">Topics</span>
                  <p className="font-medium text-slate-800">{result.form_fields.topics.join(', ')}</p>
                </div>
              ) : null}
              {result.form_fields.outcome && (
                <div className="col-span-2">
                  <span className="text-slate-500">Outcome</span>
                  <p className="font-medium text-slate-800">{result.form_fields.outcome}</p>
                </div>
              )}
              {result.form_fields.sentiment && (
                <div>
                  <span className="text-slate-500">Sentiment</span>
                  <p className="font-medium capitalize text-slate-800">{result.form_fields.sentiment}</p>
                </div>
              )}
              {result.form_fields.follow_up && (
                <div>
                  <span className="text-slate-500">Follow-up</span>
                  <p className="font-medium text-slate-800">{result.form_fields.follow_up}</p>
                </div>
              )}
            </div>
          </div>

          {result.follow_up_questions.length > 0 && (
            <div className="rounded-lg border border-amber-100 bg-amber-50 p-3">
              <p className="mb-2 text-xs font-medium text-amber-700">Missing information</p>
              <ul className="space-y-1 text-sm text-amber-800">
                {result.follow_up_questions.map((q) => (
                  <li key={q}>• {q}</li>
                ))}
              </ul>
            </div>
          )}

          <Button type="button" variant="secondary" size="sm" className="w-full" onClick={reset}>
            Upload another recording
          </Button>
        </div>
      )}
    </Card>
  );
}
