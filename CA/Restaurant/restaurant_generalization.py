import sys
from pathlib import Path

# Locate the parent directory of the current script
parent_dir = Path(__file__).resolve().parent.parent

# Add the parent directory to sys.path
sys.path.append(str(parent_dir))

from conceptualAnalyzer import Story
import string
ONTOLOGY = {
    "PATRON": {"john", "mary","alex", "sara", "tom", "linda", "peter", "anna", "mike", "emma"}, 
    "STAFF":   {"waiter", "waitress", "server", "host", "hostess",
                "chef", "cook", "manager", "bartender"},
    "MENU":    {"menu"},
    "FOOD":    {"burger", "salad", "soup", "pizza", "sandwich",
                "steak", "pasta", "dessert", "fries"},
    "DRINK":   {"coffee", "tea", "water", "wine", "soda", "juice"},
    "PAYMENT": {"bill", "check", "money", "cash", "card", "tip"},
    "RESTAURANT":   {"restaurant", "table", "kitchen", "door", "entrance",
                "booth", "counter", "seat"},
}

ROLE_FIELDS_TO_TYPE = ("ACTOR", "OBJECT", "LOCATION", "INSTRUMENT")


def classify(story: list[str]) -> list[str]:
    
    def transform(sentence: str) -> str:
        components = sentence.split()
        for i, word in enumerate(components):
            stripped = word.strip(string.punctuation)
            suffix = word[len(stripped):] 
            for role, words in ONTOLOGY.items():
                if stripped.lower() in words:
                    components[i] = role.lower() + suffix
                    break
        return " ".join(components)
        
    new_story = []
    for sentence in story:
        new_story.append(transform(sentence))

    return new_story

def generalize(events: list[str]) -> Story:
    processed_story =  classify(events)

    return Story(processed_story)



if __name__ == "__main__":
    main_path = [
        "John entered the restaurant yesterday.",
        "The waiter gave John a menu.",
        "John ordered a burger.",
        "John ate the burger.",
    ]

    story = generalize(main_path)
        # walk to the last node in the main chain (the "ate" event) and
        # attach two alternate continuations from there
    last = story
    while last.proceed:
        last = last.proceed[0]

    print(story)



