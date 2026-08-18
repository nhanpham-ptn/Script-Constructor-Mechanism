from __future__ import annotations
import spacy

'''
This is the 4th version of the conceptual analyzer. It is designed to extract the components of a sentence and represent them in a structured format. 
The main classes are CDEvent and Story, which represent individual events and sequences of events, respectively. 
The analyzer uses spaCy for natural language processing and includes a mapping of verbs to primitive actions (CDs) for classification.

However, there were some problems not with breaking down the sentences into components but rather transforming them back into a story. 
The previous version of the code was not able to specify the difference between "entering" and "leaving" a restaurant, because they were both classified as PTRANS.
The CD ATRANS was also so vague that it was not able to specify the difference between "paying" a staff and "giving" something, because they were both classified as ATRANS.

'''



# Load the small English model
nlp = spacy.load("en_core_web_sm")

VERB_TO_PRIMITIVE = {
    # physical transfer of location
    "enter": "PTRANS", "leave": "PTRANS", "walk": "PTRANS",
    "go": "PTRANS", "arrive": "PTRANS", "sit": "PTRANS",
    "stand": "PTRANS", "return": "PTRANS", "exit": "PTRANS",
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

ENTER_LIKE_VERBS = {"enter", "arrive"}
LEAVE_LIKE_VERBS = {"leave", "exit"}
 
#Making CDEvent class 
class CDEvent:
    sentence: str
    actor: str = None
    act: str = None
    CD: str = None
    instrument: str = None
    dobject: str = None
    to_role: str = None     # recipient -- who receives/is told/is given something
    from_role: str = None   # source -- who something came from
    location: str = None
    time: str = None

    additional_info: list = None
#Exteracting components from the sentence
    def conceptualAnalyzing(self, text: str):
        doc = nlp(text)
        for token in doc:
            if token.dep_ == "nsubj":
                self.actor = token.text
 
            elif token.dep_ == "dobj" and token.head.dep_ == "ROOT":
                self.dobject = token.text
 
            elif token.dep_ in ("dative", "iobj"):
                self.to_role = token.text
 
            elif token.dep_ == "pobj":
                prep = token.head.text.lower() if token.head.dep_ == "prep" else ""
                if prep in ("to", "into"):
                    self.to_role = token.text
                elif prep == "from":
                    self.from_role = token.text
                elif prep == "with":
                    self.instrument = token.text
                elif prep in ("at", "in"):
                    self.location = token.text
                else:
                    self.location = token.text
 
            elif token.dep_ == "ROOT":
                self.act = token.lemma_
                self.CD = VERB_TO_PRIMITIVE.get(token.lemma_)
 
            elif token.text.lower() in TIME_WORDS:
                self.time = token.text
 
        # --- Post-processing verb-specific role corrections ---
        # Run after the full loop: self.act needs to be reliably
        # known first, and word order doesn't guarantee ROOT is seen
        # before dobj.
 
        # pay/tip: dobj is the recipient, not a transferred item
        if self.act in PAY_LIKE_VERBS and self.dobject and not self.to_role:
            self.to_role = self.dobject
            self.dobject = IMPLICIT_TRANSFER_ITEM
 
        # enter/arrive: dobj is the GOAL of motion, not an object
        elif self.act in ENTER_LIKE_VERBS and self.dobject and not self.to_role:
            self.to_role = self.dobject
            self.dobject = None
 
        # leave/exit: dobj is the SOURCE being left, not an object
        elif self.act in LEAVE_LIKE_VERBS and self.dobject and not self.from_role:
            self.from_role = self.dobject
            self.dobject = None
            
#Initializing the CD objects
    def __init__(self, text: str):
        self.sentence = text
        self.conceptualAnalyzing(text)

#Transforming the CD objects into 
    def to_dict(self):
        d = {"ACT": self.act, "CD": self.CD}
        if self.actor:      d["ACTOR"] = self.actor
        if self.dobject:    d["OBJECT"] = self.dobject
        if self.to_role:    d["TO"] = self.to_role
        if self.from_role:  d["FROM"] = self.from_role
        if self.instrument: d["INSTRUMENT"] = self.instrument
        if self.location:   d["LOCATION"] = self.location
        if self.time:       d["TIME"] = self.time
        return d

    def __repr__(self):
        return f"{self.to_dict()}"
 


class Story:

    events : CDEvent
    proceed  : list[Story] = []

    def __init__(self, sentences: list[str]):
        self.events: CDEvent = None
        self.proceed: list[Story] = []

        if not sentences:
            return

        self.events = CDEvent(sentences[0])
        rest = sentences[1:]
        if rest:
            self.proceed = [Story(rest)]

    def __str__(self, indent: int = 0) -> str:
        pad = "  " * indent
        lines = [f"{pad}{self.events}"]
        for branch in self.proceed:
            lines.append(branch.__str__(indent + 1))
        return "\n".join(lines)


if __name__ == "__main__":
    main_path = [
        "John entered the restaurant yesterday.",
        "The waiter gave John a menu.",
        "John ordered a burger.",
        "John ate the burger.",
        "John paid the waiter.",
        "John left the restaurant.",
    ]
 
    story = Story(main_path)
 
    last = story
    while last.proceed:
        last = last.proceed[0]
    print(story)
