import clsx, { ClassValue } from 'clsx';

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

export function formatTime(timeStr: string): string {
  const [hours, minutes] = timeStr.split(':');
  const date = new Date();
  date.setHours(parseInt(hours, 10), parseInt(minutes, 10));
  return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
}

export function formatInteractionType(type: string): string {
  return type.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

export const INTERACTION_TYPES = [
  { value: 'in_person', label: 'In Person' },
  { value: 'phone_call', label: 'Phone Call' },
  { value: 'video_call', label: 'Video Call' },
  { value: 'email', label: 'Email' },
  { value: 'conference', label: 'Conference' },
  { value: 'other', label: 'Other' },
] as const;

export const SENTIMENT_OPTIONS = [
  { value: 'positive', label: 'Positive', color: 'bg-emerald-100 text-emerald-700' },
  { value: 'neutral', label: 'Neutral', color: 'bg-slate-100 text-slate-700' },
  { value: 'negative', label: 'Negative', color: 'bg-red-100 text-red-700' },
  { value: 'mixed', label: 'Mixed', color: 'bg-amber-100 text-amber-700' },
] as const;
