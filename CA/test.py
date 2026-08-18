"""
neural_ontology.py

A genuinely trained neural network classifier for ontology types,
as a comparison point to the nearest-centroid approach in
embedding_ontology.py.

The difference that matters:
- embedding_ontology.py: NO training happens. It borrows someone
  else's pretrained word vectors and just measures distance to an
  average. Zero learning on your end.
- this file: an actual training loop runs. The MLP's internal
  weights start random and get adjusted via backpropagation to
  reduce classification error on your labeled seed words.

Given you only have ~30-40 labeled words total across 6 categories,
expect this to be LESS reliable than nearest-centroid, not more --
that's the point of building both: it's a concrete demonstration of
why data volume matters for neural approaches, worth reporting in
your writeup as a deliberate comparison rather than treating whichever
one "wins" as the final answer.

Install:
    pip install spacy scikit-learn
    python -m spacy download en_core_web_md
"""

import numpy as np
import spacy
from sklearn.neural_network import MLPClassifier

nlp = spacy.load("en_core_web_md")

# Same seed words as embedding_ontology.py -- here they're TRAINING
# DATA (word, label pairs), not just centroid anchors.
SEED_WORDS = {
    "STAFF":   ["waiter", "waitress", "server", "host", "chef",
                "manager", "bartender", "hostess", "cook"],
    "MENU":    ["menu", "specials", "list"],
    "FOOD":    ["burger", "salad", "soup", "pizza", "sandwich",
                "pasta", "steak", "fries", "dessert"],
    "DRINK":   ["coffee", "tea", "water", "wine", "soda", "juice"],
    "PAYMENT": ["bill", "check", "money", "cash", "card", "tip"],
    "PLACE":   ["restaurant", "table", "kitchen", "door", "booth", "counter"],
}


def build_training_data():
    """Turn SEED_WORDS into (X, y): a matrix of word vectors and
    their labels, ready to hand to a classifier's .fit()."""
    X, y = [], []
    for label, words in SEED_WORDS.items():
        for word in words:
            token = nlp(word)[0]
            if token.has_vector and token.vector_norm > 0:
                X.append(token.vector)
                y.append(label)
    return np.array(X), np.array(y)


def train_classifier() -> MLPClassifier:
    """
    Train a small multi-layer perceptron: one hidden layer of 16
    units. This IS the "learning" step -- max_iter=2000 means it runs
    up to 2000 passes over the training data, each time nudging every
    weight in the network to reduce prediction error (backpropagation
    + gradient descent), until it converges or hits the iteration cap.
    """
    X, y = build_training_data()
    clf = MLPClassifier(hidden_layer_sizes=(16,), max_iter=2000, random_state=0)
    clf.fit(X, y)
    return clf


def classify_word_nn(clf: MLPClassifier, word: str, confidence_threshold: float = 0.5):
    """
    Classify a new word using the TRAINED network. predict_proba gives
    a probability for every category; we take the highest one, and
    reject it (return None) if the network itself isn't confident,
    mirroring the threshold behavior in embedding_ontology.py.
    """
    token = nlp(word)[0]
    if not token.has_vector or token.vector_norm == 0:
        return None, 0.0
    probs = clf.predict_proba([token.vector])[0]
    best_idx = np.argmax(probs)
    best_label = clf.classes_[best_idx]
    best_prob = probs[best_idx]
    if best_prob < confidence_threshold:
        return None, best_prob
    return best_label, best_prob


if __name__ == "__main__":
    clf = train_classifier()

    test_words = [
        # near seed words -- should classify confidently either way
        "bartender", "hostess", "fries", "steak", "espresso",
        # plausible synonyms NOT in any seed list -- the real test
        "receipt", "patio", "lemonade", "noodles",
        # should NOT match any type well
        "guitar", "purple", "thunderstorm",
        # proper names -- neither approach should confidently claim these
        "John", "Mary",
    ]

    print(f"{'word':14s} {'NN prediction':16s} confidence")
    for w in test_words:
        label, conf = classify_word_nn(clf, w)
        print(f"{w:14s} {str(label):16s} {conf:.2f}")