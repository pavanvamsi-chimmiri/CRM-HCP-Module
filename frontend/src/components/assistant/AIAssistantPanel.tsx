import { useRef, useState } from 'react';
import { Bot, Loader2, Send, Sparkles } from 'lucide-react';
import toast from 'react-hot-toast';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { assistantApi } from '@/services/api/assistant';
import { getErrorMessage } from '@/services/api/client';
import type { AssistantFormFields, AssistantMessage } from '@/types/assistant';

interface AIAssistantPanelProps {
  onApplyFields: (fields: AssistantFormFields) => void;
  disabled?: boolean;
}

const FIELD_LABELS: Record<string, string> = {
  doctor_name: 'Doctor',
  topics: 'Topics',
  outcome: 'Outcome',
  sentiment: 'Sentiment',
  follow_up: 'Follow-up',
  interaction_type: 'Type',
  interaction_date: 'Date',
  interaction_time: 'Time',
  materials_shared: 'Materials',
  samples: 'Samples',
};

const EXAMPLE_TEXT = `I met Dr Sharma today.

Discussed diabetes.

Shared brochure.

Doctor interested.

Call after two weeks.`;

function formatExtractedPreview(fields: AssistantFormFields): { label: string; value: string }[] {
  const items: { label: string; value: string }[] = [];

  if (fields.doctor_name) {
    items.push({ label: 'Doctor', value: fields.doctor_name });
  }
  if (fields.topics?.length) {
    items.push({ label: 'Topics', value: fields.topics.join(', ') });
  }
  if (fields.outcome) {
    items.push({ label: 'Outcome', value: fields.outcome });
  }
  if (fields.sentiment) {
    items.push({ label: 'Sentiment', value: fields.sentiment });
  }
  if (fields.follow_up) {
    items.push({ label: 'Follow-up', value: fields.follow_up });
  }
  if (fields.materials_shared) {
    items.push({ label: 'Materials', value: fields.materials_shared });
  }

  return items;
}

export function AIAssistantPanel({ onApplyFields, disabled }: AIAssistantPanelProps) {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<AssistantMessage[]>([
    {
      role: 'assistant',
      content:
        'Describe your HCP visit in plain language and I\'ll extract the doctor, topics, outcome, sentiment, and follow-up — then fill the form for you.',
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async (text?: string) => {
    const message = (text ?? input).trim();
    if (!message || isLoading || disabled) return;

    const userMessage: AssistantMessage = { role: 'user', content: message };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const history = [...messages, userMessage].filter((m) => m.role === 'user' || m.role === 'assistant');
      const response = await assistantApi.parse(
        message,
        history.slice(0, -1).map((m) => ({ role: m.role, content: m.content }))
      );

      onApplyFields(response.form_fields);

      const assistantMessage: AssistantMessage = {
        role: 'assistant',
        content: response.message,
        extractedFields: response.form_fields,
        missingFields: response.missing_fields,
        followUpQuestions: response.follow_up_questions,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      if (response.is_complete) {
        toast.success('All key fields extracted — form updated');
      } else {
        toast.success('Form updated — please answer the follow-up questions');
      }
    } catch (error) {
      toast.error(getErrorMessage(error));
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I couldn\'t process that message. Please try again or fill the form manually.',
        },
      ]);
    } finally {
      setIsLoading(false);
      setTimeout(scrollToBottom, 100);
    }
  };

  return (
    <Card
      className="flex h-full flex-col overflow-hidden border-brand-200"
      title="AI Assistant"
      description="Powered by LangGraph"
      action={
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600">
          <Bot className="h-4 w-4 text-white" />
        </div>
      }
    >
      <div className="flex min-h-[320px] flex-1 flex-col">
        <div className="mb-4 max-h-80 flex-1 space-y-3 overflow-y-auto rounded-lg bg-slate-50 p-3">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[92%] rounded-xl px-3.5 py-2.5 text-sm leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-brand-600 text-white'
                    : 'border border-brand-100 bg-white text-slate-700 shadow-sm'
                }`}
              >
                {msg.role === 'assistant' && (
                  <div className="mb-1.5 flex items-center gap-1.5 text-xs font-medium text-brand-600">
                    <Sparkles className="h-3 w-3" />
                    Assistant
                  </div>
                )}
                <p className="whitespace-pre-wrap">{msg.content}</p>

                {msg.extractedFields && (
                  <div className="mt-3 space-y-2 border-t border-slate-100 pt-2">
                    <p className="text-xs font-medium text-slate-500">Extracted</p>
                    <div className="flex flex-wrap gap-1.5">
                      {formatExtractedPreview(msg.extractedFields).map((item) => (
                        <span
                          key={item.label}
                          className="inline-flex items-center gap-1 rounded-md bg-brand-50 px-2 py-0.5 text-xs text-brand-700"
                        >
                          <span className="font-medium">{item.label}:</span>
                          <span className="max-w-[140px] truncate">{item.value}</span>
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {msg.followUpQuestions && msg.followUpQuestions.length > 0 && (
                  <div className="mt-3 space-y-1.5 border-t border-amber-100 pt-2">
                    <p className="text-xs font-medium text-amber-700">Follow-up needed</p>
                    {msg.followUpQuestions.map((q, qi) => (
                      <button
                        key={qi}
                        type="button"
                        onClick={() => handleSend(q)}
                        className="block w-full rounded-lg border border-amber-200 bg-amber-50 px-2.5 py-1.5 text-left text-xs text-amber-800 transition-colors hover:bg-amber-100"
                      >
                        {q}
                      </button>
                    ))}
                  </div>
                )}

                {msg.missingFields && msg.missingFields.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {msg.missingFields.map((field) => (
                      <Badge key={field} variant="warning">
                        {FIELD_LABELS[field] ?? field}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <Loader2 className="h-4 w-4 animate-spin text-brand-600" />
              Extracting fields…
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        <div className="space-y-3">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder={EXAMPLE_TEXT}
            rows={5}
            disabled={disabled || isLoading}
            className="medical-input resize-none text-sm"
          />

          <div className="flex items-center justify-between gap-2">
            <button
              type="button"
              onClick={() => setInput(EXAMPLE_TEXT)}
              disabled={disabled || isLoading}
              className="text-xs text-brand-600 hover:text-brand-700 disabled:opacity-50"
            >
              Use example
            </button>
            <Button
              type="button"
              size="sm"
              onClick={() => handleSend()}
              disabled={disabled || isLoading || !input.trim()}
              isLoading={isLoading}
            >
              <Send className="h-4 w-4" />
              Send
            </Button>
          </div>
        </div>
      </div>
    </Card>
  );
}
