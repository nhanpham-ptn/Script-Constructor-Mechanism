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
from Restaurant.restaurant_generalization import generalize, classify

import pattern_recognition
print("Loaded from:", pattern_recognition.__file__)

def event_signature(cd: dict) -> tuple:
    if cd.get("LOCATION"):
        location = cd.get("LOCATION")
    else:
        location = None
    if cd.get("TO"):
        to_role = cd.get("TO")
    else:
        to_role = None
    if cd.get("FROM"):
        from_role = cd.get("FROM")
    else:
        from_role = None
    actor = cd.get("ACTOR")
    obj = cd.get("OBJECT")
    return (f"CD: {cd.get('CD')}", f"actor: {actor}", f"object: {obj}", f"location: {location}", f"to: {to_role}", f"from: {from_role}")


def story_to_sequences(story: Story) -> list[list[tuple]]:
    if story is None or story.events is None:
        return [[]]
 
    sig = event_signature(story.events.to_dict())
 
    if not story.proceed:
        return [[sig]]
 
    sequences = []
    for branch in story.proceed:
        for tail in story_to_sequences(branch):
            sequences.append([sig] + tail)
    return sequences


def maximal_patterns(db: list[list[tuple]],  min_support:int = 2):
    ps = PrefixSpan(db)
    all_patterns = ps.frequent(min_support)
    script = {}

    edge_length = 2
    if all_patterns:
        max_len = max(len(pattern) for _, pattern in all_patterns)
        potential_main = [(support, pattern) for support, pattern in all_patterns if len(pattern) == max_len]
    else:
        potential_main = []
    edge_chains = [(support, pattern) for support, pattern in all_patterns if len(pattern) == edge_length]


    #For the main script
    
    script["main scripts"] = []
    best_support = max((support for support, _ in potential_main), default=0)
    script["main scripts"] = [pattern for support, pattern in potential_main if support == best_support]
        


    #For individual edges
    max_support = max((support for support, _ in edge_chains), default=0)
    edge_chains = [(support, pattern) for support, pattern in edge_chains if support == max_support]
    branch_nums = 1
    for (frequency, pattern) in edge_chains:
        script[f"branch {branch_nums}"] = pattern
        branch_nums += 1
    return script









