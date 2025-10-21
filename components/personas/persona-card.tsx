'use client';

import { Persona } from '@/lib/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { cn } from '@/lib/utils';

interface PersonaCardProps {
  persona: Persona;
  isActive?: boolean;
}

export function PersonaCard({ persona, isActive }: PersonaCardProps) {
  const colorClass = persona.color.replace('bg-', 'text-');

  return (
    <Card className={cn(
      'transition-all',
      isActive && 'ring-2 ring-primary shadow-lg'
    )}>
      <CardHeader className="pb-3">
        <div className="flex items-center gap-3">
          <Avatar className={cn('h-12 w-12', persona.color)}>
            <AvatarFallback className={cn('text-white font-semibold', persona.color)}>
              {persona.name.substring(0, 2).toUpperCase()}
            </AvatarFallback>
          </Avatar>
          <div className="flex-1">
            <CardTitle className={cn('text-lg', colorClass)}>{persona.name}</CardTitle>
            {persona.gender && (
              <CardDescription className="text-xs">
                {persona.gender === 'm' ? 'Male' : 'Female'}
              </CardDescription>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">{persona.description}</p>
      </CardContent>
    </Card>
  );
}
