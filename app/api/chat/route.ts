import { openai } from '@ai-sdk/openai';
import { streamText, convertToCoreMessages } from 'ai';

export const runtime = 'edge';

interface Persona {
  id: string;
  name: string;
  description: string;
  color: string;
}

export async function POST(req: Request) {
  try {
    const { messages, personas, topic, currentPersonaId } = await req.json();

    if (!personas || personas.length === 0) {
      return new Response('Personas are required', { status: 400 });
    }

    // Find the current persona
    const currentPersona = personas.find((p: Persona) => p.id === currentPersonaId);

    if (!currentPersona) {
      return new Response('Current persona not found', { status: 400 });
    }

    // Build the system prompt based on conversation state
    const conversationLength = messages.length;
    const personasList = personas.map((p: Persona) => `• ${p.name} - ${p.description}`).join('\n');

    let systemContent = `You are writing a message as ${currentPersona.name}.`;

    if (conversationLength === 0) {
      const topicInsert = topic ? ` based on the topic "${topic}"` : '';
      systemContent += ` Come up with a short to medium sized text message${topicInsert} that ends with a question or a statement.`;
    } else {
      const topicInsert = topic ? ` The discussion is around the topic "${topic}".` : '';
      systemContent += ` Answer the previous message with a short to medium sized message (about one paragraph). Analyze the message history to understand the context of the conversation.${topicInsert} Look at the name in the beginning of each message to identify each writer. The message should keep the conversation going, do not say good-bye.`;
    }

    systemContent += ` You know the ${personas.length > 2 ? 'people' : 'other person'} in the chat very well.`;

    if (personas.length === 2) {
      systemContent += ` There are only you and one other person in the chat. Only talk to the other person directly. Avoid greeting the other people in the beginning of the message.`;
    } else {
      systemContent += ` Include all participants in the chat as much as possible, but do not include their names in the message.`;
    }

    systemContent += ` Avoid greeting phrases. Avoid typing names if not absolutely necessary. Answer as casually as possible unless the description of yourself contradicts being casual. Don't be afraid including one or two emojis (maximum one emoji per sentence), but do not overdo it. Only send a message from yourself. The message should be in the form of a SMS message. Do not use phrases such as "hey guys" or "hello everyone" in the beginning of the message. Do not include any names in the beginning of the message, avoid for example "([NAME])" and "Hey [NAME]") etc. There are a total of ${personas.length} people involved in the conversation. Here's a list of the participants (including yourself) together with names and a personal descriptions:\n${personasList}`;

    const result = streamText({
      model: openai('gpt-5-mini'),
      system: systemContent,
      messages: convertToCoreMessages(messages),
      maxOutputTokens: 300,
      temperature: 0.8,
    });

    return result.toTextStreamResponse();
  } catch (error) {
    console.error('Chat API Error:', error);
    return new Response('Internal Server Error', { status: 500 });
  }
}
