import os
import random
import pandas as pd

# Get operand values based on range pattern
def get_operands(pattern):
    if any(op in pattern for op in "+-*/"):
        for op in "+-*/":
            if op in pattern:
                parts = pattern.split(op)
                a_range, b_range = parts[0], parts[1]
                break
    else:
        raise ValueError(f"Unsupported pattern format: {pattern}")

    def parse_range(r):
        r = r.split("===")[0].strip()
        if ":" in r:
            start, end = map(float, r.split(":"))
            return round(random.uniform(start, end), 2) if '.' in r else random.randint(int(start), int(end))
        else:
            return float(r) if '.' in r else int(r)

    a = parse_range(a_range)
    b = parse_range(b_range)
    return a, b, op

# Create real sentence for story mode
def generate_story_sentence(a, op, b):
    names = ["Ravi", "Maya", "Ayaan", "Zara", "Kabir"]
    items = ["balloons", "toffees", "stickers", "shells", "books"]
    friend = random.choice(["his friend", "her cousin", "a neighbor", "his classmate"])

    name = random.choice(names)
    item = random.choice(items)

    if op == "+":
        return f"{name} had {a} {item}. Later, {name} got {b} more from {friend}. How many does {name} have now?"
    elif op == "-":
        return f"{name} had {a} {item}. {name} gave {b} to {friend}. How many are left with {name}?"
    elif op == "*":
        return f"{name} has {a} boxes with {b} {item} in each. How many {item} does {name} have in total?"
    elif op == "/":
        return f"{name} had {a} {item} and shared them equally with {b} friends. How many did each get?"
    else:
        return f"{a} {op} {b}"

# Generate equation in variable form
def generate_equation(op):
    if op == "+": return "a + b"
    if op == "-": return "a - b"
    if op == "*": return "a * b"
    if op == "/": return "a / b"
    return "a ? b"

# Main processor
def process_all_files_to_excel(folder_path, output_file):
    rows = []
    difficulty_map = {"simple": 1, "easy": 2, "medium": 3, "hard": 4, "challenging": 5}

    for filename in os.listdir(folder_path):
        if not filename.endswith(".txt"): continue

        mode_difficulty = filename.replace(".txt", "").split("_")
        if len(mode_difficulty) != 2: continue

        type_name, diff = mode_difficulty
        difficulty_number = difficulty_map.get(diff, 0)
        filepath = os.path.join(folder_path, filename)

        with open(filepath, "r") as f:
            patterns = [line.strip() for line in f if line.strip()]

        for pattern in patterns:
            try:
                clean_pattern = pattern.split("===")[0].strip()
                a, b, op = get_operands(clean_pattern)
                equation = generate_equation(op)

                if type_name == "story":
                    question = generate_story_sentence(a, op, b)
                else:
                    question = f"{a} {op} {b}"

                pattern_with_vars = f"a{clean_pattern[0:clean_pattern.index(op)]}{op}b{clean_pattern[clean_pattern.index(op)+1:]}"
                rows.append({
                    "question": question,
                    "type": type_name,
                    "operand_pattern": pattern_with_vars,
                    "difficulty": difficulty_number,
                    "equation": equation
                })

            except Exception as e:
                rows.append({
                    "question": f"Error in pattern: {pattern}",
                    "type": type_name,
                    "operand_pattern": pattern,
                    "difficulty": difficulty_number,
                    "equation": str(e)
                })

    df = pd.DataFrame(rows)
    df.to_excel(output_file, index=False)
    print(f"\n✅ Questions written to {output_file}")

# Run
if __name__ == "__main__":
    folder = input("Enter folder path with operand pattern files: ").strip()
    output_excel = "generated_questions.xlsx"
    process_all_files_to_excel(folder, output_excel)
