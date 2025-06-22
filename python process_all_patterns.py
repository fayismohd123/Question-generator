import os
import random
import re

def generate_operand(rule):
    if "," in rule:
        return random.choice([int(x) for x in rule.split(",")])
    elif ":" in rule:
        start, end = map(int, rule.split(":"))
        return random.randint(min(start, end), max(start, end))
    elif ";" in rule:
        m, start, end = map(int, rule.split(";"))
        return m * random.randint(min(start, end), max(start, end))
    else:
        return int(rule)

def evaluate_expression(a, op, b):
    try:
        if op == "+": return a + b
        if op == "-": return a - b
        if op == "*": return a * b
        if op == "/": return a // b if b != 0 else "undefined"
        if op == "%": return a % b if b != 0 else "undefined"
        return "unsupported"
    except:
        return "error"

def process_all_files_to_txt(folder, output_file):
    with open(output_file, "w", encoding="utf-8") as out:
        out.write(f"Generated Questions from folder: {folder}\n")
        out.write("-" * 60 + "\n")

        for file in os.listdir(folder):
            if not file.endswith(".txt"):
                continue

            filepath = os.path.join(folder, file)
            out.write(f"\nFile: {file}\n" + "-" * 50 + "\n")

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    lines = [line.split("===")[0].strip().rstrip("*") for line in f if line.strip()]
            except Exception as e:
                out.write(f"   Error reading file {file} → {e}\n")
                continue

            for i, pattern in enumerate(lines, 1):
                try:
                    match = re.search(r'([+\-*/%])', pattern)
                    if not match:
                        raise ValueError("No valid operator found in pattern")

                    op = match.group(1)
                    left, right = pattern.split(op)
                    a = generate_operand(left.strip())
                    b = generate_operand(right.strip())
                    result = evaluate_expression(a, op, b)

                    out.write(f"{i}. Pattern: {pattern}\n")
                    out.write(f"   Question: {a} {op} {b}\n")
                    out.write(f"   → Answer: {result}\n")
                except Exception as e:
                    out.write(f"{i}. Error in pattern: {pattern} → {str(e)}\n")

if __name__ == "__main__":
    folder = input("Enter folder path with operand pattern files: ").strip()
    output = "generated_questions.txt"
    process_all_files_to_txt(folder, output)
