import sys
from pathlib import Path


# Locate the parent directory of the current script
parent_dir = Path(__file__).resolve().parent.parent

# Add the parent directory to sys.path
sys.path.append(str(parent_dir))
from prefixspan import PrefixSpan
from collections import defaultdict, Counter
from typing import Optional
from conceptualAnalyzer import CDEvent, Story
from restaurant_generalization import generalize, classify
from pattern_recognition import maximal_patterns, story_to_sequences
import inspect


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
         
    for pattern in output.get("main_script", []):
        print(pattern)
        
    print("\n\n\n")
    for i in range(1, len(output.keys() - {"main_script"})):
        print(f"Branch {i}: {output.get(f'branch_{i}', [])}")
