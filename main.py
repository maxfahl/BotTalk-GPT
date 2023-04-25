import openai
from decouple import config
from termcolor import colored, cprint
import argparse
import json
import os
import random

OPENAI_API_KEY = config('OPENAI_API_KEY')
MODEL = config('MODEL', default="gpt-3.5-turbo")

if not OPENAI_API_KEY:
    print('OpenAI API key not defined in .env.')
    quit()
openai.api_key = OPENAI_API_KEY


# Available colors in termcolor, ignore gray and white.
COLORS = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan']


class Person:
    def __init__(self, name, description, color):
        self.name = name
        self.description = description
        self.color = color
        self.messages = []


def log_prompt(prompt):
    with open("prompt_log.txt", "a") as f:
        f.write(json.dumps(prompt, indent=2))
        f.write("\n\n")


def create_person(name, description, color):
    return Person(name, description, color)


def get_chat_gpt_response(prompt):
    log_prompt(prompt)
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=prompt
    )
    return response.choices[0].message['content'].strip()


def generate_message(person, conversation):
    prompt = [
        {"role": "system", "content": f"You are {person.name}, {person.description}."},
    ]

    if len(conversation) == 0:
        prompt[0]['content'] += f" Come up with a short to medium sized text message that ends with question or a statement."
    else:
        prompt[0]['content'] += f" Come up with a short to medium sized text message that answers the previous message."

    prompt[0]['content'] += f" Answer as if you know the other person well, do not be formal or apolagetic unless the description of yourself says that you are. keep track of the names in the beginning of each message to identify what person wrote what answer. Do not type the name of the person in the beginning of your response. "

    for msg in conversation:
        role, content = msg
        prompt.append({"role": role, "content": content})

    response_message = get_chat_gpt_response(prompt)
    return response_message


def get_best_fit_person_index(people, conversation, latest_writer_index):
    roles = [{"role": "system", "content": f"{i+1}: {person.name}, {person.description}"} for i, person in enumerate(people)]

    prompt = [
                 {"role": "system", "content": "Choose the best person to respond to the latest message based on the content and the message history as a whole. Only respond with an integer representing the number of the person in the list (example response: 1). Here's the list of the people involved:\n"},
             ] + roles

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
        best_fit_person_index = get_best_fit_person_index(people, conversation, latest_writer_index)
        message = generate_message(people[best_fit_person_index], conversation)
        conversation.append(("user", f"{people[best_fit_person_index].name}: {message}"))
        cprint(f"\n{people[best_fit_person_index].name}: {message}", people[best_fit_person_index].color)

        latest_writer_index = best_fit_person_index


def get_person_input(person_number):
    name = input(f"Enter the name for person {person_number}: ")
    description = input(f"Enter a description for person {person_number} (example: 'a computer nerd who loves coffee'): ")
    return name, description


def create_and_save_people(num_people):
    people = []
    for i in range(num_people):
        name, description = get_person_input(i + 1)
        color = COLORS[i % len(COLORS)]  # Assign color to each person
        people.append(create_person(name, description, color))
    save_to_json(people)
    return people


def save_to_json(people):
    data = {f"person{i + 1}": {"name": person.name, "description": person.description} for i, person in enumerate(people)}
    with open("names_and_personalities.json", "w") as f:
        json.dump(data, f)


def load_from_json():
    with open("names_and_personalities.json", "r") as f:
        data = json.load(f)
    people = [create_person(person_data["name"], person_data["description"], person_data["color"]) for person_data in data.values()]
    return people


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

        if os.path.exists("names_and_personalities.json"):
            people = load_from_json()
            print("Previous names and descriptions:")
            for i, person in enumerate(people):
                print(f"{i + 1}. {person.name}, {person.description}")

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
