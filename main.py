import openai
from decouple import config
from termcolor import colored, cprint
import argparse
import json
import random
from elevenlabs import generate, play, set_api_key
from elevenlabs import voices
from io import BytesIO
from pydub import AudioSegment
import subprocess
import os
import re
from tempfile import NamedTemporaryFile

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

OPENAI_API_KEY = config('OPENAI_API_KEY', default=None)
MODEL = config('MODEL', default="gpt-3.5-turbo")
ELEVENLABS_API_KEY = config('ELEVENLABS_API_KEY', default=None)

if not OPENAI_API_KEY:
    print('OpenAI API key not defined in .env.')
    quit()

openai.api_key = OPENAI_API_KEY
if ELEVENLABS_API_KEY:
    set_api_key(ELEVENLABS_API_KEY)

# Available colors in termcolor, ignore gray and white.
COLORS = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan']
VOICES = {
    'f': ['Rachel', 'Domi', 'Bella', 'Elli'],
    'm': ['Antoni', 'Josh', 'Arnold', 'Adam', 'Sam']
}
PEOPLE_JSON = 'people.json'
PROMPT_LOG = 'prompt_log.txt'

assigned_voices = {'f': [], 'm': []}


class Person:
    def __init__(self, name, description, color, gender=None, voice=None):
        self.name = name
        self.description = description
        self.color = color
        self.gender = gender
        self.voice = voice


def log_prompt(prompt):
    if args.debug:
        with open(PROMPT_LOG, "a") as f:
            for message in prompt:
                f.write("---\n")
                f.write(f"role: {message['role']}\n")
                f.write(f"content: {message['content']}\n")
            f.write("\n")


def save_people_to_json(people):
    data = {"people": [{"name": person.name, "color": person.color, "description": person.description,
                        "gender": person.gender} for person in people]}
    with open(PEOPLE_JSON, "w") as f:
        json.dump(data, f, indent=4)


def load_people_from_json():
    try:
        with open(PEOPLE_JSON, "r") as f:
            data = json.load(f)
            people = [
                create_person(
                    person_data["name"],
                    person_data["description"],
                    person_data["color"],
                    person_data["gender"] if "gender" in person_data else None
                )
                for person_data in data["people"]
            ]

            return people
    except (FileNotFoundError, PermissionError, json.JSONDecodeError, KeyError):
        return []


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
        print(f"Voice '{voice_name}' not found. Please check the available voices.")
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
    log_prompt(prompt)
    try:
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=prompt
        )
        return response.choices[0].message['content'].strip()
    except openai.error.RateLimitError:
        print("The model is currently overloaded with other requests. Please try again later.")
        return ""


def generate_message(person_to_answer, previous_conversation, people, iterations_left):
    people_str_arr = [f"• {person.name}, {person.description}" for i, person in enumerate(people)]

    # Filter out the index of the person who is answering
    person_to_answer_index = people.index(person_to_answer)
    del people_str_arr[person_to_answer_index]

    people_str = "\n".join(people_str_arr)

    system_content = f"You are writing a message as {person_to_answer.name}."

    if len(previous_conversation) == 0:
        system_content += " Come up with a short to medium sized text message that ends with question or a statement."
    elif iterations_left == len(people):
        system_content += " Conclude the conversation based on the previous messages. Make up a reason to why you must end the chatting session. Say good-bye to the other participants."
    elif iterations_left < len(people):
        system_content += " The conversation is now over. Say any last words as a good-bye."
    else:
        system_content += " Come up with a short to medium sized text message that answers the previous message. Keep all the messages in mind to understand the context of the conversation. Keep track of the names in the beginning of each message to identify each writer. The message should keep the conversation going, do not say good-bye."

    system_content += f" You know the other {'people' if len(people) > 2 else 'person' } in the chat very well.{' There are only you and one other person in the chat. Only talk to the other person directly, do not include his or her name in the message.' if len(people) > 2 else ''} Answer as casually as possible unless the description contradicts it. Only send a message from yourself. The message should be in the form of a SMS message. Do not include any phrases containing another person's name such as \"(NAME)\" or \"Hey NAME\") in the beginning of the message. There are a total of {len(people_str_arr)} people involved in the conversation, here's the list of people (not including you) with their name and description:\n" + people_str

    prompt = [{"role": "system", "content": system_content}]
    for msg in previous_conversation:
        role, content = msg
        prompt.append({"role": role, "content": content})

    response_message = do_request(prompt)

    # Make sure to remove (NAME) from the beginning of the message since the model has a hard time not including it
    response_message = re.sub(r"^\([^)]*\)\s*", "", response_message)
    return response_message


def get_best_fit_person_to_respond(people, previous_conversation, latest_writer_index):
    people_str_arr = [f"{i + 1}. {person.name}, {person.description}" for i, person in enumerate(people)]

    # Exclude the latest writer from the list to decrease the risk of the model choosing the same person
    if latest_writer_index is not None:
        del people_str_arr[latest_writer_index]
    people_str = "\n".join(people_str_arr)

    content = ''
    if len(previous_conversation) == 0:
        content = "Choose the best person to start the conversation."
    else:
        content = "Choose the best person to respond to the latest message based its content, but also consider the message history as a whole."

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


def chat_simulation(people, iterations):
    conversation = []
    latest_writer_index = None

    for i in range(iterations):
        iterations_left = iterations - i
        person = get_best_fit_person_to_respond(people, conversation, latest_writer_index)
        message = generate_message(person, conversation, people, iterations_left)
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
                f'Can not convert message to speech since {person.name} does not have a gender assigned. Please restart and create people from scratch.')

        latest_writer_index = people.index(person)


def print_person_info(people):
    for i, person in enumerate(people):
        print(f"{i + 1}. {person.name}, {person.description}")


def get_person_details_from_user(person_number):
    name = input(f"Enter the name for person {person_number}: ").capitalize()
    description = input(
        f"Enter a description for person {person_number} (example: 'a computer nerd who loves coffee'): ")
    gender = None
    if ELEVENLABS_API_KEY:
        while gender not in ["m", "f"]:
            gender = input(
                f"Enter the gender for person {person_number} ('m' for male, 'f' for female, leave blank to skip): ").lower()
    color = COLORS[person_number % len(COLORS)]  # Assign color to each person
    return name, description, color, gender


def create_and_save_people(num_people):
    people = [Person(*get_person_details_from_user(i + 1)) for i in range(num_people)]
    save_people_to_json(people)
    return people


def main():
    # # Clear the log if debug mode is on
    # if args.debug:
    #     with open(PROMPT_LOG, "w") as f:
    #         pass

    try:
        people = load_people_from_json()
        if len(people):
            print("Previous names and descriptions:")
            print_person_info(people)

            use_previous = input("Would you like to use the previous names and descriptions? (y/n): ").lower()
            if use_previous != 'y':
                num_people = int(input("Enter the number of people chatting: "))
                people = create_and_save_people(num_people)
        else:
            num_people = int(input("Enter the number of people chatting: "))
            people = create_and_save_people(num_people)

        chat_simulation(people, args.iterations)
    except KeyboardInterrupt:
        print("\nBye-bye...")


if __name__ == "__main__":
    main()
