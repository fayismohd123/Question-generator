import os
import re
import random
import pandas as pd

def get_operands(pattern):
    operands = {}
    clean_pattern = re.split(r"===+", pattern)[0].strip()
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
            current += ch
        elif ch == '-' and clean_pattern[i-1].isdigit():
            parts.append(current.strip())
            parts.append('-')
            current = ''
        else:
            current += ch
        i += 1
    if current:
        parts.append(current.strip())

    operand_parts = [part for part in parts if part not in '+-*/%']
    names = ["a", "b", "c", "d", "e", "f"]

    for i, part in enumerate(operand_parts):
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

def generate_question_and_equation(mode, operands, difficulty_number, pattern):
    if mode.startswith("story"):
        return generate_story_question_and_equation(operands, difficulty_number, pattern)
    
    symbols = {'add': '+', 'sub': '-', 'mul': '×', 'div': '÷', 'rem': '%'}
    eq_symbols = {'add': '+', 'sub': '-', 'mul': '*', 'div': '/', 'rem': '%'}

    names = list(operands.keys())  # ["a", "b", "c", ...]
    
    if mode.startswith("per"):
        question = f"{{b}}% of {{a}} ="
        equation = "({b} / 100) * {a}"
        return question, equation

    op_key = mode[:3]  # like 'add', 'sub', etc.
    op_symbol = symbols.get(op_key, '?')
    eq_symbol = eq_symbols.get(op_key, '?')

    # Construct question and equation using curly brackets
    question = f" {op_symbol} ".join([f"{{{n}}}" for n in names]) + " ="
    equation = f" {eq_symbol} ".join([f"{{{n}}}" for n in names])
    
    return question.strip(), equation.strip()

def generate_story_question_and_equation(operands, difficulty_number, pattern):
    a = "{a}"
    b = "{b}"
    c = "{c}"

    names = ["Mubees", "Uthara", "Sanit", "Devika", "Nayana", "Fayis", "Sara", "Arjun", "Lina", "Rahul", "Ayaan"]
    items = ["stickers", "pencils", "balloons", "toffees", "coins", "books", "shells", "toys", "marbles"]
    intros = [
        "While walking to the market", "During a school trip", "At the village fair",
        "In the summer camp", "While visiting grandma's house", "One fine day",
        "During class break", "On her birthday", "While helping a friend"
    ]
    pronouns = {"he": ["Mubees", "Fayis", "Arjun", "Rahul", "Ayaan"], "she": ["Uthara", "Devika", "Nayana", "Sanit", "Lina", "Sara"]}

    action_phrases = {
        "+": ["got", "received", "found", "added", "earned", "was given"],
        "-": ["gave away", "lost", "returned", "shared", "handed over"],
        "*": ["bundled into sets of", "collected in groups of", "arranged into packs of", "grouped by"],
        "/": ["shared equally with friends", "split into parts", "divided among classmates", "distributed into boxes"],
        "%": ["kept a few as leftover", "left some aside", "had a remainder of", "saved the extras"]
    }

    ops = re.findall(r"[+\-*/%]", pattern.split("===")[0].strip())

    name = random.choice(names)
    pronoun = "he" if name in pronouns["he"] else "she"
    item = random.choice(items)
    intro = random.choice(intros)

    def verb(op, index=0):
        return action_phrases[op][index % len(action_phrases[op])]

    if len(ops) == 1:
        op = ops[0]
        v = verb(op)
        question = (
            f"{intro}, {name} had {a} {item}. Later, {pronoun} {v} {b}. "
            f"How many {item} does {pronoun} have now?"
        )
        equation = f"{{a}} {op} {{b}}"
    else:
        op1, op2 = ops[:2]
        v1 = verb(op1, 0)
        v2 = verb(op2, 1)
        question = (
            f"{intro}, {name} had {a} {item}. Later, {pronoun} {v1} {b}, "
            f"then {v2} {c}. How many {item} does {pronoun} have now?"
        )
        equation = f"{{a}} {op1} {{b}} {op2} {{c}}"

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
                question, equation = generate_question_and_equation(mode, operands, difficulty_number, pattern)
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
