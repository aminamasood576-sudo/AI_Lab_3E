def choose_mode(temperature, occupied):
    # Empty room has the highest priority, so everything is switched off
    if not occupied:
        return "OFF"

    elif temperature > 26:
        return "COOL"

    elif temperature < 20:
        return "HEAT"

    else:
        return "IDLE"


def check_result(temperature, occupied):
    global previous_mode

    target = choose_mode(temperature, occupied)

    # Send a command only when the target mode has changed
    if target != previous_mode:
        send_command = True
    else:
        send_command = False

    old_mode = previous_mode
    previous_mode = target
    return old_mode, target, send_command


# Internal storage for the previous target mode
previous_mode = None


test_cases = [
    {
        "name": "Case 1",
        "temperature": 30,
        "occupied": True,
        "expected_target": "COOL",
        "expected_command": True
    },
    {
        "name": "Case 2",
        "temperature": 30,
        "occupied": True,
        "expected_target": "COOL",
        "expected_command": False
    },
    {
        "name": "Case 3",
        "temperature": 26,
        "occupied": True,
        "expected_target": "IDLE",
        "expected_command": True
    },
    {
        "name": "Case 4",
        "temperature": 20,
        "occupied": True,
        "expected_target": "IDLE",
        "expected_command": False
    },
    {
        "name": "Case 5",
        "temperature": 15,
        "occupied": True,
        "expected_target": "HEAT",
        "expected_command": True
    },
    {
        "name": "Case 6",
        "temperature": 15,
        "occupied": False,
        "expected_target": "OFF",
        "expected_command": True
    },
    {
        "name": "Case 7",
        "temperature": 30,
        "occupied": False,
        "expected_target": "OFF",
        "expected_command": False
    }
]

for case in test_cases:
    old_mode, target, send_command = check_result(
        case["temperature"],
        case["occupied"]
    )

    print(case["name"])
    print("Previous Mode:", old_mode)
    print("Percept:", case["temperature"], "C, occupied =", case["occupied"])
    print("Expected:", case["expected_target"],
          "| Command" if case["expected_command"] else "| No command")
    print("Actual Target:", target)
    print("Outcome:", "Command sent" if send_command else "No command")
    print("-" * 50)
