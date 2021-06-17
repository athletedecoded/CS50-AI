from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
knowledge0 = And(
# XOr : Can be a Knight or Knave, but not both
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
# A says "I am both a knight and a knave."
    # If A is a Knight, the statement is True
    Implication(AKnight, And(AKnight,AKnave)),
    # If A in a Knave, the statement is False
    Implication(AKnave, Not(And(AKnight, AKnave))) 
)

# Puzzle 1
knowledge1 = And(
# XOr : A Can be a Knight or Knave, but not both
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
# XOr : B Can be a Knight or Knave, but not both
    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),
# A says "We are both knaves."
    # If AKnight => T
    Implication(AKnight, And(AKnave, BKnave)),
    # If AKnave => F
    Implication(AKnave, Not(And(AKnave, BKnave)))
# B says nothing.
)

# Puzzle 2
knowledge2 = And(
# XOr : A Can be a Knight or Knave, but not both
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
# XOr : B Can be a Knight or Knave, but not both
    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),
# A says "We are the same kind."
    # If AKnight => T
    Implication(AKnight, Or(And(AKnave, BKnave), And(AKnight, BKnight))),
    # If AKnave => F
    Implication(AKnave, Not(Or(And(AKnave, BKnave), And(AKnight, BKnight)))),
# B says "We are of different kinds."
    # If BKnight => T
    Implication(BKnight, Or(And(AKnave, BKnight), And(AKnight, BKnave))),
    # If BKnave => F
    Implication(BKnave, Not(Or(And(AKnave, BKnight), And(AKnight, BKnave))))
)

# Puzzle 3
knowledge3 = And(
# XOr : A Can be a Knight or Knave, but not both
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
# XOr : B Can be a Knight or Knave, but not both
    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),
# XOr : C Can be a Knight or Knave, but not both
    Or(CKnight, CKnave),
    Not(And(CKnight, CKnave)),
# A says either "I am a knight." or "I am a knave.", but you don't know which.
    # If AKnight => T
    Implication(AKnight, Or(AKnight, AKnave)),
    # If AKnave => F
    Implication(AKnave, Not(Or(AKnight, AKnave))),
# B says "A said 'I am a knave'."
    # "A said 'I am a knave'" => Implication(AKnight, AKnave) ^ Implication(AKnave, Not(AKnave))
    #                         == Implication(AKnight, AKnave) ^ Implication(AKnave, AKnight)
    #                         == Biconditional(AKnight, AKnave)
    # If BKnight => T
    Implication(BKnight, Biconditional(AKnight, AKnave)),
    # If BKnave => F
    Implication(BKnave, Not(Biconditional(AKnight, AKnave))),
# B says "C is a knave."
    # If BKnight => T
    Implication(BKnight, CKnave),
    # If BKnave => F
    Implication(BKnave, Not(CKnave)),
# C says "A is a knight."
    # If CKnight => T
    Implication(CKnight, AKnight),
    # If CKnave => F
    Implication(CKnave, Not(AKnight))
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
