import openai
from decouple import config
from termcolor import colored, cprint
import argparse
import json
import random
from elevenlabslib.helpers import *
from elevenlabslib import *
from pydub import AudioSegment
from pydub.playback import play

OPENAI_API_KEY = config('OPENAI_API_KEY')
MODEL = config('MODEL', default="gpt-3.5-turbo")
ELEVENLABS_API_KEY = config('ELEVENLABS_API_KEY')

if not OPENAI_API_KEY:
    print('OpenAI API key not defined in .env.')
    quit()

openai.api_key = OPENAI_API_KEY

# Available colors in termcolor, ignore gray and white.
COLORS = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan']
VOICES = {
    'female': ['Rachel', 'Domi', 'Bella', 'Elli'],
    'male': ['Antoni', 'Josh', 'Arnold', 'Adam', 'Sam']
}


assigned_voices = {'female': [], 'male': []}


class Person:
    def __init__(self, name, description, color, gender=None, voice=None):
        self.name = name
        self.description = description
        self.color = color
        self.gender = gender
        self.voice = voice


def log_prompt(prompt):
    with open("prompt_log.txt", "a") as f:
        for message in prompt:
            f.write(f"role: {message['role']}\n")
            f.write(f"content: {message['content']}\n")
        f.write("\n")


def play_audio(audio_file):
    audio = AudioSegment.from_file(audio_file, format="wav")
    play(audio)


def generate_audio(text, person):
    user = ElevenLabsUser(ELEVENLABS_API_KEY)
    voice_name = person.voice

    premade_voice = user.get_voices_by_name(voice_name)[0]
    audio_data = premade_voice.generate_audio_bytes(text)

    memory_file = io.BytesIO()
    save_bytes_to_file_object(memory_file, audio_data, "mp3")
    memory_file.seek(0)

    return memory_file


def create_person(name, description, color, gender):
    global assigned_voices

    # If all available voices for the gender have been assigned, reset the list
    if len(assigned_voices[gender]) == len(VOICES[gender]):
        assigned_voices[gender] = []

    # Select a voice that hasn't been assigned yet
    available_voices = [voice for voice in VOICES[gender] if voice not in assigned_voices[gender]]
    voice = random.choice(available_voices)
    assigned_voices[gender].append(voice)

    return Person(name, description, color, gender, voice)


def get_chat_gpt_response(prompt):
    log_prompt(prompt)
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=prompt
    )
    return response.choices[0].message['content'].strip()


def generate_message(person_to_answer, previous_conversation, people):
    prompt = [
        {"role": "system", "content": f"You are {person_to_answer.name}, {person_to_answer.description}."},
    ]

    if len(previous_conversation) == 0:
        prompt[0][
            'content'] += f" Come up with a short to medium sized text message that ends with question or a statement."
    else:
        prompt[0][
            'content'] += f" Come up with a short to medium sized text message that answers the previous message. Keep track of the names in the beginning of each message to identify what person wrote what answer."

    roles = [f"{i + 1}. {person.name.capitalize()}, {person.description}" for i, person in enumerate(people)]
    roles_str = "\n".join(roles)
    prompt[0][
        'content'] += f" You know the people in the chat very well. Do not be formal or apolagetic unless the description of yourself says that you are. Only answer from one person at a time, that is yourself. Do not type the name of yourself or another person in the beginning of the message. Here's a list of the people involved:\n" + roles_str

    for msg in previous_conversation:
        role, content = msg
        prompt.append({"role": role, "content": content})

    response_message = get_chat_gpt_response(prompt)
    return response_message


def get_best_fit_person_to_respond(people, conversation, latest_writer_index):
    roles = [f"{i + 1}. {person.name.capitalize()}, {person.description}" for i, person in enumerate(people)]
    roles_str = "\n".join(roles)

    content = ''
    if len(conversation) == 0:
        content = "Choose the best person to start the conversation."
    else:
        content = "Choose the best person to respond to the latest message based on the content and the message history as a whole."

    content += " Only respond with an integer representing the number of the person in the list (example response: 1). Here's the list of the people involved:\n" + roles_str

    prompt = [{"role": "system", "content": content}]
    response = get_chat_gpt_response(prompt)

    try:
        index = int(response) - 1  # Convert to zero-based index
        if 0 <= index < len(people):
            return index
        else:
            raise ValueError("Index out of range")
    except ValueError:
        # If the response is not a valid integer, choose a person at random, excluding the latest writer
        available_indices = [i for i in range(len(people)) if i != latest_writer_index]
        return random.choice(available_indices)


def chat_simulation(people, iterations):
    conversation = []
    latest_writer_index = None

    for i in range(iterations):
        best_fit_person_index = get_best_fit_person_to_respond(people, conversation, latest_writer_index)
        message = generate_message(people[best_fit_person_index], conversation, people)
        conversation.append(("user", f"{people[best_fit_person_index].name}: {message}"))
        cprint(f"\n{people[best_fit_person_index].name}: {message}", people[best_fit_person_index].color)

        if ELEVENLABS_API_KEY and people[best_fit_person_index].gender:
            audio_file = generate_audio(message, people[best_fit_person_index])
            play_audio(audio_file)

        latest_writer_index = best_fit_person_index


def print_person_info(people):
    for i, person in enumerate(people):
        print(f"{i + 1}. {person.name}, {person.description}")


def get_person_details_from_user(person_number):
    name = input(f"Enter the name for person {person_number}: ")
    description = input(
        f"Enter a description for person {person_number} (example: 'a computer nerd who loves coffee'): ")
    gender = None
    if ELEVENLABS_API_KEY:
        while gender not in ["m", "f", ""]:
            gender = input(
                f"Enter the gender for person {person_number} ('m' for male, 'f' for female, leave blank to skip): ").lower()
    color = COLORS[person_number % len(COLORS)]  # Assign color to each person
    return name, description, color, gender


def create_and_save_people(num_people):
    people = [Person(*get_person_details_from_user(i + 1)) for i in range(num_people)]
    save_to_json(people)
    return people


def save_to_json(people):
    data = {f"person{i + 1}": {"name": person.name, "color": person.color, "description": person.description,
                               "gender": person.gender} for i, person in
            enumerate(people)}
    with open("names_and_personalities.json", "w") as f:
        json.dump(data, f)


def load_from_json():
    try:
        with open("names_and_personalities.json", "r") as f:
            data = json.load(f)
            people = [
                create_person(person_data["name"], person_data["description"], person_data["color"], person_data["gender"]) if ELEVENLABS_API_KEY and person_data["gender"] else Person(person_data["name"], person_data["description"], person_data["color"], person_data["gender"]) for
                person_data in data.values()]
            return people
    except (FileNotFoundError, PermissionError, json.JSONDecodeError, KeyError):
        return []


def main():
    try:
        parser = argparse.ArgumentParser(description="Chat simulation using GPT-3.5 Turbo")
        parser.add_argument(
            "-i",
            "--iterations",
            type=int,
            default=20,
            help="Number of iterations for the chat simulation (default: 20)"
        )
        args = parser.parse_args()

        people = load_from_json()
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
