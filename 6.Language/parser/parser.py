import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | VP NP 
AdjP -> Adj | Adj AdjP
NP -> N | Det N | Det AdjP NP | NP PP | NP Conj S
PP -> P NP
VP -> V | V NP | V PP | Adv VP | VP Adv | VP Conj S
"""

"""
1. N V -- N V
2. N V Det N -- N V Det N
3. N V Det N P N -- N V Det N P N
4. N V P Det Adj N Conj N V -- N V P Det Adj N Conj N V
5. Det N V Det Adj N -- Det N V Det Adj N
6. N V P N -- N V P N
7. N Adv V Det N Conj N V P Det N Adv -- N Adv V Det N Conj N V P Det N Adv
8. N V Adv Conj V Det N -- 
9. N V Det Adj N P N Conj V N P Det Adj N
10. N V Det Adj Adj Adj N P Det N P Det N
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    tokenized = nltk.word_tokenize(sentence.lower())
    words = [word for word in tokenized if word.isalpha()]

    return words


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    # Empty NPs list
    nps = []
    # Convert to tree which maintains pointer to parent subtree
    ptree = nltk.tree.ParentedTree.convert(tree)
    # The only NP grammar logic that does not contain a nested NP tree is N or Det N
    # Find the subtrees which consist only of N phrase
    for subtree in ptree.subtrees(lambda t: t.label() == 'N'):
        # Append the NP parent of N
        nps.append(subtree.parent())

    return nps
    



if __name__ == "__main__":
    main()
