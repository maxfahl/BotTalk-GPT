'use client';

import { useState, useEffect, useRef } from 'react';
import { Persona, ChatMessage as ChatMessageType } from '@/lib/types';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { ChatMessage } from './chat-message';
import { PersonaCard } from '../personas/persona-card';
import { Loader2, Play, Pause, RotateCcw } from 'lucide-react';

interface ChatInterfaceProps {
  personas: Persona[];
  topic: string;
  onReset: () => void;
}

export function ChatInterface({ personas, topic, onReset }: ChatInterfaceProps) {
  const [chatMessages, setChatMessages] = useState<ChatMessageType[]>([]);
  const [currentPersonaId, setCurrentPersonaId] = useState<string | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [iterationCount, setIterationCount] = useState(0);
  const maxIterations = 20;
  const scrollRef = useRef<HTMLDivElement>(null);

  const selectNextPersona = async () => {
    try {
      const response = await fetch('/api/select-next', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: chatMessages.map(m => ({ role: m.role, content: m.content })),
          personas,
          topic,
          lastPersonaId: currentPersonaId,
        }),
      });

      const data = await response.json();
      return data.personaId;
    } catch (error) {
      console.error('Error selecting next persona:', error);
      // Fallback to random selection
      const availablePersonas = currentPersonaId
        ? personas.filter(p => p.id !== currentPersonaId)
        : personas;
      return availablePersonas[Math.floor(Math.random() * availablePersonas.length)].id;
    }
  };

  const simulateNextMessage = async () => {
    if (iterationCount >= maxIterations || isLoading) return;

    const nextPersonaId = await selectNextPersona();
    setCurrentPersonaId(nextPersonaId);
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: chatMessages.map(m => ({ role: m.role, content: m.content })),
          personas,
          topic,
          currentPersonaId: nextPersonaId,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate message');
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let messageContent = '';

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('0:')) {
              // Text delta
              const jsonStr = line.slice(2);
              try {
                const parsed = JSON.parse(jsonStr);
                if (parsed) {
                  messageContent += parsed;
                }
              } catch (e) {
                // Skip invalid JSON
              }
            }
          }
        }
      }

      const newMessage: ChatMessageType = {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: messageContent,
        personaId: nextPersonaId,
        personaName: personas.find(p => p.id === nextPersonaId)?.name,
      };

      setChatMessages(prev => [...prev, newMessage]);
      setIterationCount(prev => prev + 1);
    } catch (error) {
      console.error('Error generating message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const startSimulation = () => {
    setIsSimulating(true);
  };

  const pauseSimulation = () => {
    setIsSimulating(false);
  };

  useEffect(() => {
    if (isSimulating && !isLoading && iterationCount < maxIterations) {
      const timer = setTimeout(() => {
        simulateNextMessage();
      }, 1000);
      return () => clearTimeout(timer);
    } else if (iterationCount >= maxIterations) {
      setIsSimulating(false);
    }
  }, [isSimulating, isLoading, iterationCount]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [chatMessages]);

  return (
    <div className="h-screen flex flex-col">
      <div className="border-b p-4 bg-background">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div>
            <h1 className="text-2xl font-bold">BotTalk-GPT</h1>
            {topic && <p className="text-sm text-muted-foreground">Topic: {topic}</p>}
            <p className="text-sm text-muted-foreground">
              Iteration: {iterationCount} / {maxIterations}
            </p>
          </div>
          <div className="flex gap-2">
            {!isSimulating ? (
              <Button onClick={startSimulation} disabled={iterationCount >= maxIterations}>
                <Play className="mr-2 h-4 w-4" />
                {iterationCount === 0 ? 'Start' : 'Resume'}
              </Button>
            ) : (
              <Button onClick={pauseSimulation} variant="secondary">
                <Pause className="mr-2 h-4 w-4" />
                Pause
              </Button>
            )}
            <Button onClick={onReset} variant="outline">
              <RotateCcw className="mr-2 h-4 w-4" />
              Reset
            </Button>
          </div>
        </div>
      </div>

      <div className="flex-1 flex gap-4 p-4 max-w-7xl mx-auto w-full overflow-hidden">
        <div className="w-80 space-y-3 overflow-auto">
          <h2 className="font-semibold text-lg">Personas</h2>
          {personas.map((persona) => (
            <PersonaCard
              key={persona.id}
              persona={persona}
              isActive={persona.id === currentPersonaId}
            />
          ))}
        </div>

        <Card className="flex-1 flex flex-col">
          <ScrollArea className="flex-1 p-4" ref={scrollRef}>
            {chatMessages.length === 0 && !isLoading && (
              <div className="flex items-center justify-center h-full text-muted-foreground">
                <p>Click &quot;Start&quot; to begin the conversation simulation</p>
              </div>
            )}
            {chatMessages.map((msg) => {
              const persona = personas.find(p => p.id === msg.personaId);
              return <ChatMessage key={msg.id} message={msg} persona={persona} />;
            })}
            {isLoading && (
              <div className="flex items-center gap-2 p-4 text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Thinking...</span>
              </div>
            )}
          </ScrollArea>
        </Card>
      </div>
    </div>
  );
}
