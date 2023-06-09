### BotTalk-GPT

An experiment of mine that lets you define two or more personalities, giving each of them a name and a description. Optionally you can enter a topic of discussion for the conversation. The script will then generate the conversation between the participants using OpenAI ChatGPT.

I've only tried it using 3.5-turbo so far since I don't have access to 4.0 through the API as of now. The results can sometimes be a bit weird, but it's still pretty fun to play around with. I bet 4.0 would be leaps and bounds better for this. I've engineered the prompts as good as I can, but since I'm no pro, there's definitely room for improvement. If anyone has any ideas on how to improve them, feel free to open an issue or a pull request. Also, if you try it out with 4.0, let me know how it goes!

**Instructions:**
- Rename `.env.example` to `.env`
- Enter your `OPENAI_API_KEY`. 
- Optionally enter an `ELEVENLABS_API_KEY` to have the messages read out loud.
- `pip install -r requirements.txt`
- `python ./main.py`

The conversation will go on for 20 iterations per default, but you can adjust that by changing the iteration count using the argument `-i` (example: `python ./main.py -i 50`),

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
