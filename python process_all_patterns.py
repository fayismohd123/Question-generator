import os
import random
import re
import pandas as pd

def generate_operand(rule):
    try:
        if "," in rule:
            values = [float(x) if "." in x else int(x) for x in rule.split(",")]
            return random.choice(values)
        elif ":" in rule:
            start, end = rule.split(":")
            if "." in start or "." in end:
                return round(random.uniform(float(start), float(end)), 2)
            else:
                return random.randint(int(start), int(end))
        elif ";" in rule:
            m, start, end = rule.split(";")
            if "." in m or "." in start or "." in end:
                return round(float(m) * random.uniform(float(start), float(end)), 2)
            else:
                return int(m) * random.randint(int(start), int(end))
        else:
            return float(rule) if "." in rule else int(rule)
    except Exception as e:
        raise ValueError(f"Invalid rule '{rule}': {e}")

def evaluate_expression(a, op, b):
    try:
        if op == "+": return round(a + b, 2)
        if op == "-": return round(a - b, 2)
        if op == "*": return round(a * b, 2)
        if op == "/": return round(a / b, 2) if b != 0 else "undefined"
        if op == "%": return round(a % b, 2) if b != 0 else "undefined"
        return "unsupported"
    except:
        return "error"

def difficulty_to_number(d):
    return {
        "simple": 1,
        "easy": 2,
        "medium": 3,
        "hard": 4,
        "challenging": 5
    }.get(d.lower(), 0)

def process_all_files_to_excel(folder, output_excel):
    rows = []

    for file in os.listdir(folder):
        if not file.endswith(".txt"):
            continue

        filepath = os.path.join(folder, file)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = [line.split("===")[0].strip().rstrip("*") for line in f if line.strip()]
        except Exception as e:
            print(f"Error reading {file}: {e}")
            continue

        # Infer type and difficulty from filename
        parts = file.replace(".txt", "").split("_")
        type_name = parts[0] if len(parts) > 0 else "unknown"
        difficulty_name = parts[1] if len(parts) > 1 else "unknown"
        difficulty_number = difficulty_to_number(difficulty_name)

        for pattern in lines:
            try:
                match = re.search(r'([+\-*/%])', pattern)
                if not match:
                    # Single operand (e.g., 0:9)
                    a = generate_operand(pattern)
                    labeled = f"a{pattern}"
                    question = f"{a}"
                    rows.append({
                        "Question": question,
                        "Type": type_name,
                        "Pattern": labeled,
                        "Difficulty": difficulty_number
                    })
                    continue

                op = match.group(1)
                parts_raw = pattern.split(op)
                operands = []
                labeled_parts = []

                for i, rule in enumerate(parts_raw):
                    val = generate_operand(rule.strip())
                    label = chr(97 + i)  # a, b, c...
                    operands.append(val)
                    labeled_parts.append(f"{label}{rule.strip()}")

                labeled_pattern = op.join(labeled_parts)
                a = operands[0]
                b = operands[1] if len(operands) > 1 else None

                question = f"{a} {op} {b}" if b is not None else f"{a}"

                rows.append({
                    "Question": question,
                    "Type": type_name,
                    "Pattern": labeled_pattern,
                    "Difficulty": difficulty_number
                })

            except Exception as e:
                print(f"Error parsing pattern '{pattern}' in {file}: {e}")

    df = pd.DataFrame(rows)
    df.to_excel(output_excel, index=False)
    print(f"✅ Output written to: {output_excel}")

if __name__ == "__main__":
    folder = input("Enter folder path with operand pattern files: ").strip()
    output_excel = "generated_questions.xlsx"
    process_all_files_to_excel(folder, output_excel)