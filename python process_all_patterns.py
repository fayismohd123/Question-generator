import os
import random
import re

def is_float_rule(rule):
    return any("." in x for x in re.split(r'[:,;]', rule))

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
                        # No operator: Treat as single operand generation
                        try:
                            value = generate_operand(pattern.strip())
                            out.write(f"{i}. Pattern: {pattern}\n")
                            out.write(f"   Random Value: {value}\n")
                        except Exception as e:
                            out.write(f"{i}. Error in single operand: {pattern} → {e}\n")
                        continue


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
