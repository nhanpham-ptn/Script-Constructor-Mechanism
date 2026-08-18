import sys
from pathlib import Path

# Locate the parent directory of the current script
parent_dir = Path(__file__).resolve().parent.parent

# Add the parent directory to sys.path
sys.path.append(str(parent_dir))
from prefixspan import PrefixSpan
from collections import defaultdict, Counter
from typing import Optional, NamedTuple
from conceptualAnalyzer import CDEvent, Story
from Restaurant.restaurant_generalization import generalize, classify

import pattern_recognition
print("Loaded from:", pattern_recognition.__file__)

class EventSignature(NamedTuple):
    """
    A structured, hashable stand-in for a raw tuple. Still works
    everywhere a tuple worked (PrefixSpan, set/list operations,
    equality checks) since NamedTuple IS a tuple -- but sig.actor
    reads a lot better than sig[1], and there's no more embedding
    labels inside string values just to keep track of what's what.
    ("from" is a Python keyword, hence from_.)
    """
    cd: Optional[str]
    actor: Optional[str]
    object: Optional[str]
    location: Optional[str]
    to: Optional[str]
    from_: Optional[str]
 
 
def event_signature(cd: dict) -> EventSignature:
    return EventSignature(
        cd=cd.get("CD"),
        actor=cd.get("ACTOR"),
        object=cd.get("OBJECT"),
        location=cd.get("LOCATION"),
        to=cd.get("TO"),
        from_=cd.get("FROM"),
    )


def story_to_sequences(story: Story) -> list[list[EventSignature]]:
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

def bigrams(pattern) -> set:
    """Consecutive pairs within a sequence -- the 'edges' a sequence implies."""
    return {(pattern[i], pattern[i + 1]) for i in range(len(pattern) - 1)}


def maximal_patterns(db: list[list[EventSignature]], min_support: int = 2):
    ps = PrefixSpan(db)
    all_patterns = ps.frequent(min_support)
    script = {}
    
    #For the main script, we want to find the longest patterns that are not subsequences of any other pattern.
    if all_patterns:
        max_len = max(len(pattern) for _, pattern in all_patterns)
        potential_main = [(support, pattern) for support, pattern in all_patterns if len(pattern) == max_len]
    else:
        potential_main = []
        
    max_support = max((support for support, _ in potential_main), default=0)
    script["main_script"] = [pattern for support, pattern in potential_main if support == max_support][0] 
    
    #For each pattern, check if it is maximal (not a subsequence of any other pattern)
    edge_length = 2
    edge_events = [(support, pattern) for support, pattern in all_patterns if len(pattern) == edge_length and support >= min_support]
    
    main_script_edge = set()
    for ms in script["main_script"]:
        main_script_edge |= bigrams(ms)
        
    
    branch_num = 1
    for support, pattern in edge_events:
        pattern_edge = bigrams(pattern)
        if not pattern_edge.issubset(main_script_edge):
            script[f"branch_{branch_num}"] = pattern
            branch_num += 1
    
    return script