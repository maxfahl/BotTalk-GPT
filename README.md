# BotTalk-GPT

Create and simulate conversations between AI personas with modern UI, powered by GPT-5-mini.

![Version](https://img.shields.io/badge/version-2.0-blue)
![License](https://img.shields.io/badge/license-ISC-green)

## Overview

BotTalk-GPT lets you define two or more AI personas, each with unique personalities and characteristics. Watch them engage in dynamic conversations on topics of your choice, powered by OpenAI's latest GPT-5-mini model.

## Features

✨ **Modern Web Interface** - Built with Next.js 15, React 19, and TypeScript
🎨 **Beautiful UI** - shadcn/ui components with Tailwind CSS
🤖 **GPT-5-mini** - Powered by OpenAI's latest model
💬 **Real-time Streaming** - Watch conversations unfold in real-time with Vercel AI SDK
👥 **Persona Management** - Create and customize multiple AI personas
🎯 **Topic-based Discussions** - Guide conversations with optional topics
💾 **Auto-save** - Settings persist automatically via localStorage
🎭 **Visual Personas** - Color-coded avatars for easy identification

## Quick Start

### Web Application (Recommended)

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.local.example .env.local
   ```

   Edit `.env.local` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Run the development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

5. **Create personas and start chatting!**

### Legacy Python CLI (Still Available)

The original terminal-based version is still included:

1. **Set up Python environment:**
   ```bash
   pip install -r requirements.txt
   cp .env.example .env
   ```

2. **Configure your API key in `.env`:**
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Run the script:**
   ```bash
   python main.py
   # Or with custom iterations:
   python main.py -i 50
   ```

## Technology Stack

### Modern Web Version
- **Framework:** Next.js 15 with App Router
- **Language:** TypeScript
- **UI Components:** shadcn/ui (Radix UI primitives)
- **Styling:** Tailwind CSS 4
- **AI:** Vercel AI SDK with OpenAI GPT-5-mini
- **State Management:** React hooks with localStorage persistence

### Legacy CLI Version
- **Language:** Python 3
- **AI:** OpenAI API (gpt-3.5-turbo/gpt-4)
- **TTS:** ElevenLabs (optional)

## Architecture

```
/app
  /api
    /chat         - Streaming chat endpoint
    /select-next  - Persona selection logic
  /page.tsx       - Main application page
  /layout.tsx     - Root layout
  /globals.css    - Global styles

/components
  /ui             - shadcn/ui base components
  /chat           - Chat interface components
  /personas       - Persona management components

/lib
  /types.ts       - TypeScript type definitions
  /utils.ts       - Utility functions
```

## How It Works

1. **Setup Phase:** Create 2+ personas with names, descriptions, and optional genders
2. **Topic Selection:** Optionally define a discussion topic
3. **Simulation:** The AI intelligently selects which persona should respond next
4. **Message Generation:** Each persona generates contextual responses based on:
   - Their personality description
   - The conversation history
   - The discussion topic (if provided)
   - The other personas in the conversation
5. **Streaming Display:** Responses stream in real-time to the UI

## API Routes

### `/api/chat`
Handles streaming message generation for the selected persona.

**Request:**
```typescript
{
  messages: ChatMessage[],
  personas: Persona[],
  topic: string,
  currentPersonaId: string
}
```

### `/api/select-next`
Determines which persona should respond next.

**Request:**
```typescript
{
  messages: ChatMessage[],
  personas: Persona[],
  topic: string,
  lastPersonaId: string
}
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |

### Customization

- **Max Iterations:** Default is 20 messages. Adjust in `components/chat/chat-interface.tsx`
- **Model:** Uses `gpt-5-mini`. Change in API routes if needed
- **Colors:** Customize persona colors in `lib/types.ts`

## Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Type checking
npx tsc --noEmit
```

#### Some conversation examples
These examples was generated using the 3.5-turbo model. I've since tried version 4 and it is a lot better in these kinds of applications, so I would really recommend that if you have access..

Satan having an identity crisis

![5](https://user-images.githubusercontent.com/19852554/234862040-2aa3c1e3-96dd-49d7-8487-f3f1b7aa2fa0.png)


Coffee vs. Tea

![1](https://user-images.githubusercontent.com/19852554/234594645-cadd8a1f-fe99-4bb5-b2a2-b88bde46594b.png)


Love is in the air

![2](https://user-images.githubusercontent.com/19852554/234594674-c311bd61-4c49-4ea7-b4e7-6b5a878a86e1.png)


Dad trying to get his sun away from the computer

![3](https://user-images.githubusercontent.com/19852554/234594682-72dfc590-c926-4767-99b8-add26f08046e.png)


And a favourite of mine so far, Steve Jobs and Bill Gates discussing news

![4](https://user-images.githubusercontent.com/19852554/234599980-b73af344-ee0c-40bb-a966-186ccc74022e.png)
