import os
import re
import random
import pandas as pd

def get_operands(pattern):
    operands = {}
    clean_pattern = re.split(r"===+", pattern)[0].strip()
    # Custom logic to split operands while handling negative values like *-50
    parts = []
    current = ''
    i = 0
    while i < len(clean_pattern):
        ch = clean_pattern[i]
        if ch in '+*/%':
            parts.append(current.strip())
            parts.append(ch)
            current = ''
        elif ch == '-' and (i == 0 or clean_pattern[i-1] in '+*/%'):
            current += ch  # it's a negative number
        elif ch == '-' and i > 0 and clean_pattern[i-1].isdigit():
            parts.append(current.strip())
            parts.append('-')
            current = ''
        else:
            current += ch
        i += 1
    if current:
        parts.append(current.strip())

    # Filter only operands (skip operator tokens)
    operand_parts = [part for part in parts if part not in '+-*/%']

    names = ["a", "b", "c", "d", "e", "f"]

    for i, part in enumerate(operand_parts):
        part = part.strip()
        name = names[i] if i < len(names) else f"x{i}"

        try:
            if "," in part:
                choices = [float(x) if '.' in x else int(x) for x in part.split(",")]
                value = random.choice(choices)
            elif ":" in part:
                start, end = map(float, part.split(":"))
                value = random.uniform(start, end) if '.' in part else random.randint(int(start), int(end))
                value = round(value, 2) if isinstance(value, float) else value
            elif ";" in part:
                m, start, end = map(float, part.split(";"))
                rnd = random.uniform(start, end) if '.' in part else random.randint(int(start), int(end))
                value = round(m * rnd, 2) if isinstance(rnd, float) else int(m * rnd)
            else:
                value = float(part) if '.' in part else int(part)
        except Exception as e:
            raise ValueError(f"Invalid operand rule '{part}': {e}")

        operands[name] = value
    return operands

def attach_variable_names_to_pattern(pattern):
    clean = pattern.split("===")[0].strip()
    tokens = re.split(r"([+\-*/%])", clean)
    variables = iter("abcdefghijklmnopqrstuvwxyz")
    result = ""

    for token in tokens:
        token = token.strip()
        if token in "+-*/%":
            result += token
        elif token:
            result += f"{next(variables)}{token}"
    return result

def generate_question_and_equation(mode, operands, difficulty_number):
    a = operands.get("a", 0)
    b = operands.get("b", 0)
    c = operands.get("c", 0)

    if mode.startswith("add"):
        return f"{a} + {b}", "a + b"
    elif mode.startswith("sub"):
        return f"{a} - {b}", "a - b"
    elif mode.startswith("mul"):
        return f"{a} × {b}", "a * b"
    elif mode.startswith("div"):
        return f"{a} ÷ {b}", "a / b"
    elif mode.startswith("rem"):
        return f"{a} % {b}", "a % b"
    elif mode.startswith("per"):
        return f"{b}% of {a}", "(b / 100) * a"
    elif mode.startswith("story"):
        return generate_story_question_and_equation(operands, difficulty_number)
    else:
        return f"{a}, {b}, {c}", ""

def generate_story_question_and_equation(operands, difficulty_number):
    a = operands.get("a", 0)
    b = operands.get("b", 0)
    c = operands.get("c", 0)

    names = ["Ravi", "Neha", "Ayaan", "Meera", "Zoya", "Kabir", "Sara", "Arjun", "Lina", "Rahul"]
    items = ["stickers", "pencils", "balloons", "toffees", "coins", "books", "shells", "toys", "marbles", "erasers"]
    places = ["school fair", "summer camp", "picnic spot", "grandma's house", "science class"]
    ops = ["+", "-", "*", "/", "%"]
    symbols = {
        "+": ("received", "+"),
        "-": ("gave", "-"),
        "*": ("multiplied with", "*"),
        "/": ("divided among", "/"),
        "%": ("found remainder of", "%")
    }

    name = random.choice(names)
    item = random.choice(items)
    place = random.choice(places)

    if difficulty_number <= 3:
        op = random.choice(ops)
        verb, eq_op = symbols[op]
        question = f"{name} had {a} {item}. Then, {name} {verb} {b}. How many {item} does {name} have now?"
        equation = f"a {eq_op} b"
    else:
        op1, op2 = random.sample(ops, 2)
        verb1, eq1 = symbols[op1]
        verb2, eq2 = symbols[op2]
        question = (
            f"At the {place}, {name} had {a} {item}. Then, {name} {verb1} {b} and later {verb2} {c}. "
            f"How many {item} does {name} have now?"
        )
        equation = f"a {eq1} b {eq2} c"

    return question, equation

def process_all_files_to_excel(folder_path, output_file):
    rows = []
    difficulty_map = {
        "simple": 1, "easy": 2, "medium": 3, "med": 3,
        "hard": 4, "challenging": 5, "chlg": 5
    }

    for filename in os.listdir(folder_path):
        if not filename.endswith(".txt"):
            continue

        try:
            mode, diff = filename.replace(".txt", "").split("_")
            difficulty_number = difficulty_map.get(diff.lower(), 0)
        except ValueError:
            mode, difficulty_number = filename.replace(".txt", ""), 0

        with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        for pattern in lines:
            try:
                clean_pattern = pattern.split("===")[0].strip()
                pattern_with_vars = attach_variable_names_to_pattern(clean_pattern)
                operands = get_operands(pattern)
                question, equation = generate_question_and_equation(mode, operands, difficulty_number)
                rows.append({
                    "question": question,
                    "type": mode,
                    "operand_pattern": pattern_with_vars,
                    "difficulty": difficulty_number,
                    "equation": equation
                })
            except Exception as e:
                rows.append({
                    "question": f"Error in pattern: {pattern}",
                    "type": mode,
                    "operand_pattern": pattern,
                    "difficulty": difficulty_number,
                    "equation": str(e)
                })

    df = pd.DataFrame(rows)
    df.to_excel(output_file, index=False)
    print(f"✅ Excel file saved to: {output_file}")

if __name__ == "__main__":
    folder = input("Enter folder path with operand pattern files: ").strip()
    output_excel = "generated_questions.xlsx"
    process_all_files_to_excel(folder, output_excel)
