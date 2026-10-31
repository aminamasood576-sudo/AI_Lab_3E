def rule_based(score, documents_complete, income_verified, attendance):
    if score < 70:
        return "Hold", "score is below 70"

    elif not documents_complete:
        return "Hold", "documents are incomplete"

    elif not income_verified:
        return "Hold", "income is not verified"

    elif attendance < 75:
        return "Hold", "attendance is below 75"

    else:
        return "Review", "all conditions are satisfied"


test_cases = [
    {
        "name": "Case 1 (pass)",
        "score": 85,
        "documents_complete": True,
        "income_verified": True,
        "attendance": 90,
        "expected": "Review"
    },
    {
        "name": "Case 2 (income fails)",
        "score": 85,
        "documents_complete": True,
        "income_verified": False,
        "attendance": 90,
        "expected": "Hold"
    },
    {
        "name": "Case 3 (attendance fails)",
        "score": 85,
        "documents_complete": True,
        "income_verified": True,
        "attendance": 70,
        "expected": "Hold"
    },
    {
        "name": "Case 4 (boundary)",
        "score": 70,
        "documents_complete": True,
        "income_verified": True,
        "attendance": 75,
        "expected": "Review"
    }
]

for case in test_cases:
    result, reason = rule_based(
        case["score"],
        case["documents_complete"],
        case["income_verified"],
        case["attendance"]
    )

    print(case["name"])
    print("Input: score =", case["score"],
          ", documents_complete =", case["documents_complete"],
          ", income_verified =", case["income_verified"],
          ", attendance =", case["attendance"])
    print("Expected:", case["expected"])
    print("Actual:", result)
    print("Reason:", reason)
    print("-" * 50)
