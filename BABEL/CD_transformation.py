from collections import defaultdict
import sys
from pathlib import Path


# Locate the parent directory of the current script
parent_dir = Path(__file__).resolve().parent.parent

# Add the parent directory to sys.path
sys.path.append(str(parent_dir))
from CA.Restaurant.restaurant_generalization import generalize, classify
from CA.conceptualAnalyzer import CDEvent, Story
from CA.pattern_recognition import maximal_patterns, story_to_sequences, EventSignature

VERB_TO_PRIMITIVE = {
    # physical transfer of location
    "PTRANS": "go", "leave": "PTRANS", "walk": "PTRANS",
    # abstract transfer of possession
    "pay": "ATRANS", "give": "ATRANS", "take": "ATRANS",
    "buy": "ATRANS", "receive": "ATRANS", "tip": "ATRANS",
    "bring": "ATRANS",
    # ingestion
    "eat": "INGEST", "drink": "INGEST",
    # mental transfer / communication
    "order": "MTRANS", "ask": "MTRANS", "tell": "MTRANS",
    "say": "MTRANS", "read": "MTRANS", "request": "MTRANS",
    "greet": "MTRANS", "thank": "MTRANS",
    # applying force
    "push": "PROPEL", "pull": "PROPEL", "throw": "PROPEL",
    # grasping
    "grab": "GRASP", "hold": "GRASP", "pick": "GRASP",
}
 
TIME_WORDS = {"yesterday", "today", "tomorrow", "now", "then", "later",
              "afterward", "afterwards", "eventually", "finally"}

PAY_LIKE_VERBS = {"pay", "tip"}
IMPLICIT_TRANSFER_ITEM = "MONEY"


def babel_cd_transformation(event: EventSignature) -> str:
    #For making the main script more readable, we will convert the CD events back to natural language sentences.
    sentence = ""
    if event.cd == 'PTRANS':
        src = f" from {event.from_}" if event.from_ else ""
        dest = f" to {event.to}" if event.to else ""
        return f"{event.actor} goes{src}{dest}" 
    elif event.cd == 'ATRANS':
        if event.to:
            return f"{event.actor} gives {event.object} to {event.to}"
        elif event.from_:
            return f"{event.actor} takes {event.object} from {event.from_}"
        else:
            return f"{event.actor} transfers {event.object}"
    elif event.cd == 'MTRANS':
        if event.from_:
            return f"{event.actor} asks {event.from_} for {event.object}"
        elif event.to:
            return f"{event.actor} tells {event.to} about {event.object}"
        else:
            return f"{event.actor} requests {event.object}"
    elif event.cd == 'INGEST':
        sentence += f"{event.actor} eats {event.object}" if event.object else f"{event.actor} eats"
    elif event.cd == 'PROPEL':
        sentence += f"{event.actor} pushes {event.object}" if event.object else f"{event.actor} pushes"
    elif event.cd == 'GRASP':
        sentence += f"{event.actor} grabs {event.object}" if event.object else f"{event.actor} grabs"
    else:
        sentence += f"{event.actor} performs an action"
    
    return sentence

#Apply the babel_cd_transformation to a list of EventSignature objects to convert them back to natural language sentences.
def script_to_natural_language(input_data: dict) -> list[str]:
    main_script = input_data.get("main_script")
    if not main_script:
        return []
    return [babel_cd_transformation(event) for event in main_script]


def add_branch(input_data: dict) -> list[str]:
    main_script = input_data.get("main_script")
    if not main_script:
        return []

    branch_map = defaultdict(list)
    for key, pattern in input_data.items():
        if key.startswith("branch"):
            branch_point, alt_event = pattern
            branch_map[branch_point].append(alt_event)

    result = []
    for event in main_script:
        sentence = babel_cd_transformation(event)
        for alt_event in branch_map[event]:
            sentence += f" (Alternate continuation: {babel_cd_transformation(alt_event)})"
        result.append(sentence)
    return result



RESTAURANT_STORIES = [
    # 1. John -- the "canonical" path used in earlier demos
    [
        "John entered the restaurant.",
        "John sat at a table.",
        "The waiter gave John a menu.",
        "John ordered a burger.",
        "John ate the burger.",
        "John paid the waiter.",
        "John left the restaurant.",
    ],
    # 2. Mary -- orders dessert instead of stopping after the main course
    [
        "Mary entered the restaurant.",
        "The host gave Mary a menu.",
        "Mary ordered a salad.",
        "Mary ate the salad.",
        "Mary ordered dessert.",
        "Mary ate the dessert.",
        "Mary paid the host.",
    ],
    # 3. Alex -- drinks water before the food arrives
    [
        "Alex walked into the restaurant.",
        "Alex sat at the table.",
        "The waitress gave Alex a menu.",
        "Alex ordered pizza.",
        "Alex drank water.",
        "Alex ate the pizza.",
        "Alex paid the waitress.",
    ],
    # 4. Sara -- never pays on-screen; thanks the server instead
    [
        "Sara entered the restaurant.",
        "The server gave Sara a menu.",
        "Sara ordered soup.",
        "Sara ate the soup.",
        "Sara thanked the server.",
        "Sara left the restaurant.",
    ],
    # 5. Tom -- sits at a booth, not a table; bartender instead of waiter
    [
        "Tom entered the restaurant.",
        "Tom sat at the booth.",
        "The bartender gave Tom a menu.",
        "Tom ordered a sandwich.",
        "Tom drank coffee.",
        "Tom ate the sandwich.",
        "Tom paid the bartender.",
    ],
    # 6. Linda -- includes a deliberately messier sentence (two objects)
    [
        "Linda entered the restaurant.",
        "The waiter gave Linda a menu.",
        "Linda ordered pasta.",
        "Linda ate the pasta.",
        "Linda asked the waiter for the bill.",
        "Linda paid the waiter.",
        "Linda left the restaurant.",
    ],
    # 7. Peter -- sits at the counter; chef instead of waiter
    [
        "Peter entered the restaurant.",
        "Peter sat at the counter.",
        "The chef gave Peter a menu.",
        "Peter ordered steak.",
        "Peter ate the steak.",
        "Peter ordered dessert.",
        "Peter paid the chef.",
    ],
    # 8. Anna -- orders a drink alongside food, shorter story
    [
        "Anna entered the restaurant.",
        "The host gave Anna a menu.",
        "Anna ordered fries.",
        "Anna drank soda.",
        "Anna ate the fries.",
        "Anna paid the host.",
        "Anna left the restaurant.",
    ],
    # 9. Mike -- orders twice (drink, then food) before eating; tips instead of "pays"
    [
        "Mike walked into the restaurant.",
        "Mike sat at a table.",
        "The waiter gave Mike a menu.",
        "Mike ordered wine.",
        "Mike ordered a burger.",
        "Mike ate the burger.",
        "Mike tipped the waiter.",
        "Mike left the restaurant.",
    ],
    # 10. Emma -- orders drink and food together, thanks staff before paying
    [
        "Emma entered the restaurant.",
        "The waitress gave Emma a menu.",
        "Emma ordered tea.",
        "Emma ordered a sandwich.",
        "Emma ate the sandwich.",
        "Emma thanked the waitress.",
        "Emma paid the waitress.",
        "Emma left the restaurant.",
    ],
]
 
 
if __name__ == "__main__":
    # walk to the last node in the main chain (the "ate" event) and
    # attach two alternate continuations from there
    sequence: list = []
    for story in RESTAURANT_STORIES:
        generalization = generalize(story)
        sequence += story_to_sequences(generalization)
        
    #sequences_to_story(sequence)
        
    output = maximal_patterns(sequence,  (max(2, len(RESTAURANT_STORIES) // 5)))
         
    for sentence in add_branch(output):
        print(sentence)