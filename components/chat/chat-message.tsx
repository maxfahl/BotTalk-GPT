'use client';

import { ChatMessage as ChatMessageType, Persona } from '@/lib/types';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { cn } from '@/lib/utils';

interface ChatMessageProps {
  message: ChatMessageType;
  persona?: Persona;
}

export function ChatMessage({ message, persona }: ChatMessageProps) {
  if (!persona) return null;

  const colorClass = persona.color.replace('bg-', 'text-');

  return (
    <div className="flex gap-3 p-4 hover:bg-muted/50 transition-colors">
      <Avatar className={cn('h-10 w-10', persona.color)}>
        <AvatarFallback className={cn('text-white font-semibold', persona.color)}>
          {persona.name.substring(0, 2).toUpperCase()}
        </AvatarFallback>
      </Avatar>
      <div className="flex-1 space-y-1">
        <div className="flex items-baseline gap-2">
          <span className={cn('font-semibold', colorClass)}>{persona.name}</span>
        </div>
        <p className="text-sm text-foreground whitespace-pre-wrap">{message.content}</p>
      </div>
    </div>
  );
}
