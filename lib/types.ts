export interface Persona {
  id: string;
  name: string;
  description: string;
  color: string;
  gender?: 'm' | 'f';
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  personaId?: string;
  personaName?: string;
}

export interface ConversationSettings {
  topic: string;
  personas: Persona[];
  iterations: number;
}

export const PERSONA_COLORS = [
  { name: 'Blue', value: 'bg-blue-500', text: 'text-blue-500' },
  { name: 'Yellow', value: 'bg-yellow-500', text: 'text-yellow-500' },
  { name: 'Green', value: 'bg-green-500', text: 'text-green-500' },
  { name: 'Purple', value: 'bg-purple-500', text: 'text-purple-500' },
  { name: 'Cyan', value: 'bg-cyan-500', text: 'text-cyan-500' },
  { name: 'Red', value: 'bg-red-500', text: 'text-red-500' },
  { name: 'Pink', value: 'bg-pink-500', text: 'text-pink-500' },
  { name: 'Orange', value: 'bg-orange-500', text: 'text-orange-500' },
];
