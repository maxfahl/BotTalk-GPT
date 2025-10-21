'use client';

import { useState, useEffect } from 'react';
import { Persona } from '@/lib/types';
import { PersonaSetup } from '@/components/personas/persona-setup';
import { ChatInterface } from '@/components/chat/chat-interface';

export default function Home() {
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [topic, setTopic] = useState('');
  const [isSetupComplete, setIsSetupComplete] = useState(false);

  // Load saved settings from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('bottalk-settings');
    if (saved) {
      try {
        const { personas: savedPersonas, topic: savedTopic } = JSON.parse(saved);
        if (savedPersonas && Array.isArray(savedPersonas)) {
          setPersonas(savedPersonas);
        }
        if (savedTopic) {
          setTopic(savedTopic);
        }
      } catch (error) {
        console.error('Error loading saved settings:', error);
      }
    }
  }, []);

  // Save settings to localStorage
  useEffect(() => {
    if (personas.length > 0) {
      localStorage.setItem('bottalk-settings', JSON.stringify({ personas, topic }));
    }
  }, [personas, topic]);

  const handleStart = () => {
    setIsSetupComplete(true);
  };

  const handleReset = () => {
    setIsSetupComplete(false);
  };

  if (!isSetupComplete) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background to-muted/50 p-4">
        <div className="max-w-4xl mx-auto py-8">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold mb-2">BotTalk-GPT</h1>
            <p className="text-muted-foreground">
              Create AI personas and watch them have conversations powered by GPT-5-mini
            </p>
          </div>
          <PersonaSetup
            personas={personas}
            topic={topic}
            onPersonasChange={setPersonas}
            onTopicChange={setTopic}
            onStart={handleStart}
          />
        </div>
      </div>
    );
  }

  return <ChatInterface personas={personas} topic={topic} onReset={handleReset} />;
}
