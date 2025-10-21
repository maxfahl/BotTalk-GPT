import { openai } from '@ai-sdk/openai';
import { generateText, convertToCoreMessages } from 'ai';

export const runtime = 'edge';

interface Persona {
  id: string;
  name: string;
  description: string;
  color: string;
}

export async function POST(req: Request) {
  try {
    const { messages, personas, topic, lastPersonaId } = await req.json();

    if (!personas || personas.length === 0) {
      return Response.json({ error: 'Personas are required' }, { status: 400 });
    }

    // If only 2 personas, alternate between them
    if (personas.length === 2 && lastPersonaId) {
      const nextPersona = personas.find((p: Persona) => p.id !== lastPersonaId);
      return Response.json({ personaId: nextPersona.id });
    }

    // Filter out the last persona who spoke
    const availablePersonas = lastPersonaId
      ? personas.filter((p: Persona) => p.id !== lastPersonaId)
      : personas;

    const personasList = availablePersonas
      .map((p: Persona, idx: number) => `${idx + 1}. ${p.name} - ${p.description}`)
      .join('\n');

    let systemContent = '';

    if (messages.length === 0) {
      const topicInsert = topic ? ` based on the topic "${topic}"` : '';
      systemContent = `Choose the best person to start the conversation${topicInsert}.`;
    } else {
      const topicInsert = topic ? ` and the topic "${topic}"` : '';
      systemContent = `Choose the best person to respond to the latest message${topicInsert}, but also consider the message history as a whole. Do not select the person who wrote the latest message.`;
    }

    systemContent += ` Only respond with an integer representing the number of a person in the list below (example response: 1). Here's the list of the people to choose from:\n${personasList}`;

    const result = await generateText({
      model: openai('gpt-5-mini'),
      system: systemContent,
      messages: convertToCoreMessages(messages),
      maxOutputTokens: 10,
      temperature: 0.3,
    });

    // Parse the response to get the index
    const responseText = result.text.trim();
    const index = parseInt(responseText, 10) - 1;

    if (isNaN(index) || index < 0 || index >= availablePersonas.length) {
      // Fallback to random selection
      const randomIndex = Math.floor(Math.random() * availablePersonas.length);
      return Response.json({ personaId: availablePersonas[randomIndex].id });
    }

    return Response.json({ personaId: availablePersonas[index].id });
  } catch (error) {
    console.error('Select Next API Error:', error);
    return Response.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
