import time
import subprocess
import os
import re
import argparse
import json
import random
from tempfile import NamedTemporaryFile
import openai
from dotenv import load_dotenv
from termcolor import colored, cprint
from elevenlabs import generate, play, set_api_key
from elevenlabs import voices
from io import BytesIO
from pydub import AudioSegment

parser = argparse.ArgumentParser(description="Chat simulation using GPT-3.5 Turbo")
parser.add_argument(
    "-i",
    "--iterations",
    type=int,
    default=20,
    help="Number of iterations for the chat simulation (default: 20)"
)
parser.add_argument(
    "-d",
    "--debug",
    action="store_true",
    help="Enable debug help"
)
args = parser.parse_args()

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', default=None)
MODEL = os.getenv('MODEL', default="gpt-3.5-turbo")
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY', default=None)

if not OPENAI_API_KEY:
    cprint("OpenAI API key not defined in .env", "red")
    quit()

openai.api_key = OPENAI_API_KEY
if ELEVENLABS_API_KEY:
    set_api_key(ELEVENLABS_API_KEY)

# Available colors in termcolor, ignore gray and white.
COLORS = ['blue', 'yellow', 'green', 'magenta', 'cyan', 'red']
VOICES = {
    'f': ['Rachel', 'Domi', 'Bella', 'Elli'],
    'm': ['Antoni', 'Josh', 'Arnold', 'Adam', 'Sam']
}
DATA_JSON = 'previous_settings.json'
PROMPT_LOG = 'prompt_log.txt'

assigned_voices = {'f': [], 'm': []}


class Person:
    def __init__(self, name, description, color, gender=None, voice=None):
        self.name = name
        self.description = description
        self.color = color
        self.gender = gender
        self.voice = voice

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "gender": self.gender
        }


def log(message):
    if args.debug:
        with open(PROMPT_LOG, "a") as f:
            f.write(f"{message}\n\n")


def save_data_to_json(data):
    with open(DATA_JSON, "w") as f:
        json.dump({"topic": data["topic"], "people": [person for person in data["people"]]}, f, indent=4)


def format_people_to_list_str(people, prefix=None, exclude=None):
    items = [
        f"{prefix if prefix else str(i + 1) + '. '}{person.name}{' - ' + person.description if person.description else ''}"
        for i, person in enumerate(people)
    ]
    if exclude is not None:
        del items[exclude]
    return "\n".join(items)


def load_data_from_json():
    try:
        with open(DATA_JSON, "r") as f:
            data = json.load(f)
            people_data = data["people"]
            people = [
                Person(
                    person_data["name"],
                    person_data["description"],
                    COLORS[i % len(COLORS)],  # Assign color to each person
                    person_data.get("gender")
                )
                for i, person_data in enumerate(people_data)
            ]
            topic = data.get("topic", "")
            return people, topic
    except (FileNotFoundError, PermissionError, json.JSONDecodeError, KeyError):
        return [], ""


def play_audio(audio_segment):
    with NamedTemporaryFile(suffix=".wav", delete=True) as f:
        audio_segment.export(f.name, "wav")
        fnull = open(os.devnull, 'w')
        subprocess.call(["ffplay", "-nodisp", "-autoexit", f.name], stdout=fnull, stderr=subprocess.STDOUT)


def generate_audio(text, person):
    voice_name = person.voice

    voice = None
    available_voices = voices()
    for v in available_voices:
        if v.name == voice_name:
            voice = v
            break

    if not voice:
        cprint(f"Voice '{voice_name}' not found. Please check the available voices.", "red")
        return

    audio_data = generate(text, voice=voice)
    audio_segment = AudioSegment.from_file(BytesIO(audio_data), format="mp3")

    return audio_segment


def get_voice_for_gender(gender):
    global assigned_voices

    # If all available voices for the gender have been assigned, reset the list
    if len(assigned_voices[gender]) == len(VOICES[gender]):
        assigned_voices[gender] = []

    # Select a voice that hasn't been assigned yet
    available_voices = [voice for voice in VOICES[gender] if voice not in assigned_voices[gender]]
    voice = random.choice(available_voices)
    assigned_voices[gender].append(voice)

    return voice


def create_person(name, description, color, gender=None):
    voice = None
    if gender:
        voice = get_voice_for_gender(gender)
    return Person(name, description, color, gender, voice)


def do_request(prompt):
    log(prompt[0]['content'])
    try:
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=prompt
        )
        return response.choices[0].message['content'].strip()
    except openai.error.RateLimitError:
        cprint("The model is currently overloaded with other requests. Trying again in 10 seconds.", "red")
        time.sleep(10)
        return do_request(prompt)


def generate_message(person_to_answer, previous_conversation, people, topic, iterations_left):
    people_str = format_people_to_list_str(people, '• ')

    system_content = f"You are writing a message as {person_to_answer.name}."

    if len(previous_conversation) == 0:
        topic_insert = f' based on the topic "{topic}"' if topic else ''
        system_content += f" Come up with a short to medium sized text message{topic_insert} that ends with question or a statement."
    elif iterations_left == len(people):
        system_content += " Conclude the conversation based on the previous messages. Make up a reason to why you must end the chatting session. Say good-bye to the other participants."
    elif iterations_left < len(people):
        system_content += " The conversation is now over. Say any last words as a good-bye."
    else:
        topic_insert = f' The discussion is around the topic "{topic}".' if topic else ''
        system_content += f" Answer the previous message with a short to medium sized message (about one paragraph). Analyze the message history to understand the context of the conversation.{topic_insert} Look at the name in the beginning of each message to identify each writer. The message should keep the conversation going, do not say good-bye."

    system_content += f" You know the {'people' if len(people) > 2 else 'other person'} in the chat very well.{' There are only you and one other person in the chat. Only talk to the other person directly. Avoid greeting the other people in the beginning of the message.' if len(people) == 2 else ' Include all participants in the chat as much as possible, but do not include their names in the message.'} Avoid greeting phrases. Avoid typing names if not absolutely necessary. Answer as casually as possible unless the description of yourself contradicts being casual. Don\'t be afraid including one or two emojis (maximum one emoji per sentence), but do not overdo it. Only send a message from yourself. The message should be in the form of a SMS message. Do not use phrases such as \"hey guys\" or \"hello everyone\" in the beginning of the message. Do not include any names in the beginning of the message, avoid for example \"([NAME])\" and \"Hey [NAME]\") etc. There are a total of {len(people)} people involved in the conversation. Here\'s a list of the participants (including yourself) together with names and a personal descriptions:\n" + people_str

    prompt = [{"role": "system", "content": system_content}]
    for msg in previous_conversation:
        role, content = msg
        prompt.append({"role": role, "content": content})

    response_message = do_request(prompt)

    # Make sure to remove (NAME) from the beginning of the message since the model has a hard time not including it
    response_message = re.sub(r"^\([^)]*\)\s*", "", response_message)
    return response_message


def get_best_fit_person_to_respond(people, topic, previous_conversation, latest_writer_index):
    # No need to ask ChatGPT if there are only two people in the chat
    if len(people) == 2 and not len(previous_conversation) == 0:
        return people[0] if latest_writer_index == 1 else people[1]

    people_str = format_people_to_list_str(people, None, latest_writer_index)

    content = ''
    if len(previous_conversation) == 0:
        topic_insert = f' based on the topic "{topic}"' if topic else ''
        content = f"Choose the best person to start the conversation{topic_insert}."
    else:
        topic_insert = f' and the topic "{topic}"' if topic else ''
        content = f"Choose the best person to respond to the latest message{topic_insert}, but also consider the message history as a whole. Do not select the person who wrote the latest message."

    content += " Only respond with an integer representing the number of a person in the list below (example response: 1). Here's the list of the people to choose from:\n" + people_str

    prompt = [{"role": "system", "content": content}]
    for msg in previous_conversation:
        role, content = msg
        prompt.append({"role": role, "content": content})
    response = do_request(prompt)

    try:
        index = int(response) - 1  # Convert to zero-based index
        if 0 <= index < len(people):
            return people[index]
        else:
            raise ValueError("Index out of range")
    except ValueError:
        # If the response is not a valid integer, choose a person at random, excluding the latest writer
        available_indices = [i for i in range(len(people)) if i != latest_writer_index]
        index = random.choice(available_indices)
        return people[index]


def chat_simulation(topic, people, iterations):
    conversation = []
    latest_writer_index = None

    for i in range(iterations):
        iterations_left = iterations - i
        person = get_best_fit_person_to_respond(people, topic, conversation, latest_writer_index)
        message = generate_message(person, conversation, people, topic, iterations_left)
        conversation.append(("user", f"({person.name}) {message}"))
        cprint(f"\n{person.name}: {message}", person.color)

        if ELEVENLABS_API_KEY and person.gender:
            if not not person.voice:
                voice = get_voice_for_gender(person.gender)
                person.voice = voice
            audio_file = generate_audio(message, person)
            if audio_file is not None:
                play_audio(audio_file)
        elif ELEVENLABS_API_KEY:
            print(
                f"Can not convert message to speech since {person.name} does not have a gender assigned. Please restart and create people from scratch.")

        latest_writer_index = people.index(person)


def get_person_details_for_user(person_number):
    name = input(f"Enter the name for person {person_number}: ").capitalize()
    description = input(
        f"Enter a description for person {person_number} (example: 'A computer nerd who loves coffee'): ")
    gender = None
    if ELEVENLABS_API_KEY:
        while gender not in ["m", "f"]:
            gender = input(
                f"Enter the gender for person {person_number} ('m' for male, 'f' for female, leave blank to skip): ").lower()
    color = COLORS[person_number % len(COLORS)]  # Assign color to each person
    return name, description, color, gender


def create_people(num_people):
    people = [Person(*get_person_details_for_user(i + 1)) for i in range(num_people)]
    return people


def main():
    try:
        people, topic = load_data_from_json()

        if len(people):
            cprint("Previous settings\n", "cyan", attrs=["bold"])
            saved_data_str = ''
            if topic:
                saved_data_str += f"Topic: \"{topic}\"\n"
            saved_data_str += "Names and descriptions:\n"
            saved_data_str += format_people_to_list_str(people, "    ")
            cprint(saved_data_str, "cyan")

            use_previous = None
            while use_previous not in ['y', 'n']:
                use_previous = input("Would you like to start using the previous settings? (y/n): ").lower()
                if use_previous == 'n':
                    people = None

        if not people:
            topic = input("Enter a topic for discussion (leave blank for free discussion): ")

            num_people = 0
            while num_people < 2:
                try:
                    num_people = int(input("Enter the number of people chatting: "))
                except ValueError:
                    print("Invalid input. Please enter a valid integer.")

            people = create_people(num_people)
            data = {
                "topic": topic,
                "people": [
                    person.to_dict() for person in people
                ]
            }
            save_data_to_json(data)
        chat_simulation(topic, people, args.iterations)
    except KeyboardInterrupt:
        print("\nBye-bye...")


if __name__ == "__main__":
    main()
