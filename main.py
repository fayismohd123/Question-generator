import random
import re

def generate_operand_pattern(difficulty, operand_count):
    patterns = {
        "simple": {
            1: ["a1:10*"],
            2: ["a1:5*b1:5*", "a5,10*b2:4*"],
            3: ["a1:3*b2:4*c1:2*"]
        },
        "easy": {
            1: ["a10,20,30*"],
            2: ["a5:10*b2:6*", "a4;1;5*b1:3*"],
            3: ["a3;2;4*b1:5*c10,20*"]
        },
        "medium": {
            1: ["a50:100*"],
            2: ["a10;1;5*b10:20*", "a25,50*b5:10*"],
            3: ["a5;2;10*b20:30*c3;1;3*"]
        },
        "hard": {
            1: ["a100;2;200*"],
            2: ["a20;5;50*b50:100*", "a50,100*b10;2;5*"],
            3: ["a10;1;10*b1:12*c5;2;10*"]
        }
    }

    try:
        return random.choice(patterns[difficulty][operand_count]).strip().rstrip("*")
    except KeyError:
        raise ValueError(f"No pattern rule for difficulty={difficulty}, operand_count={operand_count}")

def get_operands(pattern):
    operands = {}
    for part in pattern.split("*"):
        if not part:
            continue
        name = part[0]
        rule = part[1:]
        try:
            if "," in rule:
                value = random.choice([int(x) for x in rule.split(",")])
            elif ":" in rule:
                start, end = map(int, rule.split(":"))
                if start > end:
                    start, end = end, start
                value = random.randint(start, end)
            elif ";" in rule:
                m, start, end = map(int, rule.split(";"))
                if start > end:
                    start, end = end, start
                value = m * random.randint(start, end)
            else:
                value = int(rule)
            operands[name] = value
        except Exception as e:
            raise ValueError(f"Invalid operand rule '{rule}' in pattern '{part}': {e}")
    return operands

def generate_question(mode, operands):
    a = operands.get("a", 0)
    b = operands.get("b", 0)
    c = operands.get("c", 0)

    if mode == "currency":
        if "c" in operands:
            return f"You spent ₹{a} and earned ₹{b}, then donated ₹{c}. What's your total money now?"
        return f"You had ₹{a} and earned ₹{b}. What's the total amount?"

    elif mode == "addition":
        if "c" in operands:
            return f"What is {a} plus {b} plus {c}?"
        return f"What is {a} plus {b}?"

    elif mode == "multiplication":
        if "c" in operands:
            return f"What is {a} times {b} times {c}?"
        return f"What is {a} times {b}?"

    return f"Operands used: {a}, {b}, {c}"

def build_equation(mode, operands):
    a = operands.get("a", 0)
    b = operands.get("b", 0)
    c = operands.get("c", 0)

    if mode == "currency":
        if "c" in operands:
            return f"{a} + {b} - {c} = {a + b - c}"
        return f"{a} + {b} = {a + b}"

    elif mode == "addition":
        if "c" in operands:
            return f"{a} + {b} + {c} = {a + b + c}"
        return f"{a} + {b} = {a + b}"

    elif mode == "multiplication":
        if "c" in operands:
            return f"{a} × {b} × {c} = {a * b * c}"
        return f"{a} × {b} = {a * b}"

    return f"Operands used: {a}, {b}, {c}"

def generate_questions(mode, difficulty, operand_count):
    print(f"\nGenerating pattern for: {difficulty}, {operand_count} operands")
    pattern = generate_operand_pattern(difficulty, operand_count)
    print(f"Pattern: {pattern}")

    questions = set()
    while len(questions) < 5:
        try:
            operands = get_operands(pattern)
            question = generate_question(mode, operands)
            equation = build_equation(mode, operands)
            output = f"{question}\n   → Equation: {equation}"
            if output not in questions:
                questions.add(output)
                print(f"\n{len(questions)}. {output}")
        except Exception as e:
            print("Error:", e)
            break

if __name__ == "__main__":
    mode = input("Enter mode (currency, addition, multiplication, etc.): ").strip().lower()
    difficulty = input("Enter difficulty (simple/easy/medium/hard): ").strip().lower()
    operand_count = int(input("Enter number of operands (1/2/3):"))
    generate_questions(mode, difficulty, operand_count)
