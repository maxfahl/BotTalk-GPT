'use client';

import { useState } from 'react';
import { Persona, PERSONA_COLORS } from '@/lib/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Plus, Trash2 } from 'lucide-react';
import { PersonaCard } from './persona-card';

interface PersonaSetupProps {
  personas: Persona[];
  topic: string;
  onPersonasChange: (personas: Persona[]) => void;
  onTopicChange: (topic: string) => void;
  onStart: () => void;
}

export function PersonaSetup({ personas, topic, onPersonasChange, onTopicChange, onStart }: PersonaSetupProps) {
  const [newPersona, setNewPersona] = useState({ name: '', description: '', gender: '' });

  const addPersona = () => {
    if (!newPersona.name || !newPersona.description) return;

    const colorIndex = personas.length % PERSONA_COLORS.length;
    const color = PERSONA_COLORS[colorIndex].value;

    const persona: Persona = {
      id: `persona-${Date.now()}`,
      name: newPersona.name,
      description: newPersona.description,
      color,
      gender: newPersona.gender === 'm' || newPersona.gender === 'f' ? newPersona.gender : undefined,
    };

    onPersonasChange([...personas, persona]);
    setNewPersona({ name: '', description: '', gender: '' });
  };

  const removePersona = (id: string) => {
    onPersonasChange(personas.filter(p => p.id !== id));
  };

  const canStart = personas.length >= 2;

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Conversation Settings</CardTitle>
          <CardDescription>
            Define the topic and create at least 2 personas for the conversation
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="topic">Discussion Topic (Optional)</Label>
            <Input
              id="topic"
              placeholder="e.g., The future of AI, Coffee vs Tea..."
              value={topic}
              onChange={(e) => onTopicChange(e.target.value)}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Add Persona</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                placeholder="e.g., Steve Jobs"
                value={newPersona.name}
                onChange={(e) => setNewPersona({ ...newPersona, name: e.target.value })}
                onKeyDown={(e) => e.key === 'Enter' && addPersona()}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="gender">Gender (Optional)</Label>
              <Input
                id="gender"
                placeholder="m or f"
                value={newPersona.gender}
                maxLength={1}
                onChange={(e) => setNewPersona({ ...newPersona, gender: e.target.value.toLowerCase() })}
                onKeyDown={(e) => e.key === 'Enter' && addPersona()}
              />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Input
              id="description"
              placeholder="e.g., A visionary tech entrepreneur who revolutionized personal computing"
              value={newPersona.description}
              onChange={(e) => setNewPersona({ ...newPersona, description: e.target.value })}
              onKeyDown={(e) => e.key === 'Enter' && addPersona()}
            />
          </div>
          <Button onClick={addPersona} className="w-full">
            <Plus className="mr-2 h-4 w-4" />
            Add Persona
          </Button>
        </CardContent>
      </Card>

      {personas.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-semibold">Personas ({personas.length})</h3>
          <div className="grid gap-3 md:grid-cols-2">
            {personas.map((persona) => (
              <div key={persona.id} className="relative">
                <PersonaCard persona={persona} />
                <Button
                  variant="destructive"
                  size="icon"
                  className="absolute top-2 right-2"
                  onClick={() => removePersona(persona.id)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        </div>
      )}

      <Button
        onClick={onStart}
        disabled={!canStart}
        size="lg"
        className="w-full"
      >
        {canStart ? 'Start Conversation' : `Add ${2 - personas.length} more persona${2 - personas.length === 1 ? '' : 's'} to start`}
      </Button>
    </div>
  );
}
