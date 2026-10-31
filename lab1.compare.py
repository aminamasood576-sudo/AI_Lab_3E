def symbolic(score, complete):
    if complete and score >= 70:
        return "Review"
    else:
        return "Hold"


def threshold(probability):
    if probability >= 0.70:
        return "Review"
    else:
        return "Hold"


cases = [
    ("complete_high", 82, True, 0.81),
    ("complete_low", 68, True, 0.74),
    ("incomplete_high", 91, False, 0.88),
    ("boundary", 70, True, 0.70),
    ("score_69_only", 69, True, 0.70),
    ("prob_0.69_only", 70, True, 0.69)
]

print("case | symbolic | threshold | disagreement")

for name, score, complete, probability in cases:
    a = symbolic(score, complete)
    b = threshold(probability)
    print(name, a, b, a != b, sep=" | ")
