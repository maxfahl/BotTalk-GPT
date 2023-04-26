### BotTalk-GPT

An experiment of mine that lets you define two or more personalities, giving each of them a name and description. The script will then generate a conversation between the participants using OpenAI ChatGPT.

I've only tried it using 3.5-turbo so far since I don't have access to 4.0 through the API as of now. The results can sometimes be a bit weird, but it's still pretty fun to play around with. I bet 4.0 would be leaps and bounds better for this. I've engineered the prompts as good as I can, but since I'm no pro, there's definitely room for improvement. If anyone has any ideas on how to improve them, feel free to open an issue or a pull request. Also, if you try it out with 4.0, let me know how it goes!

**Instructions:**
- Rename `.env.example` to `.env`
- Enter your `OPENAI_API_KEY`. 
- Optionally enter an `ELEVENLABS_API_KEY` to have the messages read out loud.
- `pip install -r requirements.txt`
- `python ./main.py`

The conversation will go on for 20 iterations per default, but you can adjust that by changing the iteration count using the argument `-i` (example: `python ./main.py -i 50`),

**Examples:**


