from __future__ import annotations
import spacy

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
 
#Making CDEvent class 
class CDEvent:
    sentence: str
    actor:str = None
    act: str
    CD: str
    instrument:str = None
    dobject: str = None
    location: str = None
    time: str = None

    additional_info: list = None
#Exteracting components from the sentence
    def conceptualAnalyzing(self, text: str):
        doc = nlp(text)
        for token in doc:
            if token.dep_ == "nsubj":
                self.actor = token.text

            elif token.dep_ == "dobj"and token.head.dep_ == "ROOT":
                self.dobject = token.text

            elif token.dep_ == "pobj" or token.head.dep_ == "prep" or token.dep_ == "dative":
                self.location = token.text

            elif token.dep_ == "ROOT":
                self.act = token.head.lemma_
                self.CD = VERB_TO_PRIMITIVE.get(token.head.lemma_)

            elif token.text.lower() in TIME_WORDS:
                self.time = token.text

#Initializing the CD objects
    def __init__(self, text: str):
        self.sentence = text
        self.conceptualAnalyzing(text)

#Transforming the CD objects into 
    def to_dict(self):
        d = {"ACT": self.act}
        d["CD"] = self.CD
        if self.actor:      d["ACTOR"] = self.actor
        if self.dobject:     d["OBJECT"] = self.dobject
        if self.instrument: d["INSTRUMENT"] = self.instrument
        if self.location:      d["LOCATION"] = self.location
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
    ]
 
    story = Story(main_path)
 
    last = story
    while last.proceed:
        last = last.proceed[0]
    print(story)
