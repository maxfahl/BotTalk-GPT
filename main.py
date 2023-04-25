import openai
from decouple import config
from termcolor import cprint
import json
import os

OPENAI_API_KEY = config('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    print('OpenAI API key not defined in .env.')
    quit()
openai.api_key = OPENAI_API_KEY

class Person:
    def __init__(self, name, personality):
        self.name = name
        self.personality = personality
        self.messages = []

print_magenta = lambda text: cprint(text, "magenta")
print_cyan = lambda text: cprint(text, "cyan")

def create_person(name, personality):
    return Person(name, personality)


def generate_message(person, conversation):
    prompt = [
        {"role": "system", "content": f"You are {person.name}, {person.personality}."},
    ]

    if len(conversation) == 0:
        prompt[0]['content'] += f" Come up with a short to medium sized text message that ends with question or a statement."
    else:
        prompt[0]['content'] += f" Come up with a short to medium sized text message that answers the previous message."

    prompt[0]['content'] += f" Do not type name name of the person in the beginning of the response."

    for msg in conversation:
        role, content = msg
        prompt.append({"role": role, "content": content})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=prompt
    )

    return response.choices[0].message['content']


def chat_simulation(person1, person2, iterations):
    conversation = []

    for i in range(iterations):
        if i % 2 == 0:
            sender = person1
            receiver = person2
        else:
            sender = person2
            receiver = person1

        message = generate_message(sender, conversation)
        conversation.append(("user", f"{sender.name}: {message}"))

        printer = print_cyan if sender == person1 else print_magenta
        printer(f"\n{sender.name}: {message}")


def get_person_input(person_number):
    name = input(f"Enter the name for person {person_number}: ")
    personality = input(f"Enter the personality for person {person_number}: ")
    return name, personality


def create_and_save_people():
    name1, personality1 = get_person_input(1)
    name2, personality2 = get_person_input(2)
    save_to_json(name1, personality1, name2, personality2)
    return create_person(name1, personality1), create_person(name2, personality2)


def save_to_json(name1, personality1, name2, personality2):
    data = {
        "person1": {
            "name": name1,
            "personality": personality1
        },
        "person2": {
            "name": name2,
            "personality": personality2
        }
    }
    with open("names_and_personalities.json", "w") as f:
        json.dump(data, f)


def load_from_json():
    with open("names_and_personalities.json", "r") as f:
        data = json.load(f)
    return data["person1"]["name"], data["person1"]["personality"], data["person2"]["name"], data["person2"]["personality"]


def main_logic(person1, person2):
    chat_simulation(person1, person2, 20)


def main():
    if os.path.exists("names_and_personalities.json"):
        use_previous = input("Would you like to use the previous names and personalities? (y/n): ").lower()
        if use_previous == 'y':
            name1, personality1, name2, personality2 = load_from_json()
            person1, person2 = create_person(name1, personality1), create_person(name2, personality2)
        else:
            person1, person2 = create_and_save_people()
    else:
        person1, person2 = create_and_save_people()

    main_logic(person1, person2)


if __name__ == "__main__":
    main()
