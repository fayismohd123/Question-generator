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
    parts = re.split(r"[+\-*/%]", clean)
    variables = iter("abcdefghijklmnopqrstuvwxyz")
    result = ""

    for part in parts:
        part = part.strip()
        if part:
            result += f"{next(variables)}{part}*"
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
    # Placeholder variables for curly-braced question and equation
    a = "{a}"
    b = "{b}"
    c = "{c}"

    # Characters, items, and context
    names = ["Mubees", "Uthara", "Sanit", "Devika", "Nayana", "Fayis", "Sara", "Arjun", "Lina", "Rahul", "Ayaan"]
    pronouns = {"he": ["Mubees", "Fayis", "Arjun", "Rahul", "Ayaan"], "she": ["Uthara", "Devika", "Nayana", "Sanit", "Lina", "Sara"]}
    items = ["pencil", "balloon", "sticker", "marble", "book", "shell", "toy", "eraser", "coin", "toffee"]

    intros = [
        "on the way home from school", "during a class activity", "while visiting grandma",
        "at a birthday party", "in the library", "during recess", "in the science fair",
        "on a picnic", "while helping a friend", "after finishing homework"
    ]

    action_phrases = {
        "+": ["was gifted", "won", "received", "got from a friend", "collected"],
        "-": ["lost", "gave away", "shared", "donated", "used up"],
        "*": ["grouped into sets of", "bundled together", "packed in groups of"],
        "/": ["divided evenly", "split among friends", "shared with classmates", "distributed among children"],
        "%": ["had some leftover", "found a remainder", "kept a part aside", "left some aside"]
    }

    midphrases = [
        "then", "after that", "later on", "following that", "and then"
    ]

    templates_two = [
        "{name} had {a} {item}s {intro}. {pronoun_cap} {verb1} {b}. How many {item}s does {pronoun} have now?",
        "It happened {intro} when {name} started with {a} {item}s. {pronoun_cap} {verb1} {b}. What's left now?",
        "{name} owned {a} {item}s {intro}. Later, {pronoun} {verb1} {b}. How many remain?"
    ]

    templates_three = [
        "{name} had {a} {item}s {intro}. {pronoun_cap} {verb1} {b}, {mid} {verb2} {c}. How many {item}s now?",
        "During the activity {intro}, {name} began with {a} {item}s. Then {pronoun} {verb1} {b} and {verb2} {c}. What's the total?",
        "It was {intro} when {name} collected {a} {item}s. {pronoun_cap} {verb1} {b}, {mid} {verb2} {c}. How many left?"
    ]

    # Decide random story components
    name = random.choice(names)
    pronoun = "he" if name in pronouns["he"] else "she"
    item = random.choice(items)
    intro = random.choice(intros)
    mid = random.choice(midphrases)

    ops = re.findall(r"[+\-*/%]", pattern.split("===")[0].strip())

    # Shuffle verbs for randomness
    for key in action_phrases:
        random.shuffle(action_phrases[key])

    if len(ops) == 1:
        op = ops[0]
        verb1 = action_phrases[op][0]
        equation = f"{{a}} {op} {{b}}"
        question = random.choice(templates_two).format(
            name=name, a=a, b=b, c=c,
            item=item, intro=" " + intro,
            pronoun=pronoun, pronoun_cap=pronoun.capitalize(),
            verb1=verb1
        )
    else:
        op1, op2 = ops[:2]
        verb1 = action_phrases[op1][0]
        verb2 = action_phrases[op2][1 % len(action_phrases[op2])]
        equation = f"{{a}} {op1} {{b}} {op2} {{c}}"
        question = random.choice(templates_three).format(
            name=name, a=a, b=b, c=c,
            item=item, intro=" " + intro,
            pronoun=pronoun, pronoun_cap=pronoun.capitalize(),
            verb1=verb1, verb2=verb2, mid=mid
        )

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
                    "operand": pattern_with_vars,
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
        # Replace short mode names with full operation names
    operation_map = {
        "add": "addition",
        "sub": "subtraction",
        "mul": "multiplication",
        "div": "division",
        "rem": "remainder",
        "per": "percentage",
        "story": "story",
        "time": "time",
        "currency": "currency",
        "distance": "distance",
        "bellring": "bellring"
    }
    df["type"] = df["type"].map(operation_map).fillna(df["type"])

    df.to_excel(output_file, index=False)
    print(f"✅ Excel file saved to: {output_file}")

if __name__ == "__main__":
    folder = input("Enter folder path with operand pattern files: ").strip()
    output_excel = "generated_questions.xlsx"
    process_all_files_to_excel(folder, output_excel)
