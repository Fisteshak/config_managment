import sys
from pathlib import Path
from tomlkit import parse, TOMLDocument, items

def convert_value(value):
    if callable(value):  # Add check for callable objects
        return str(value)
    if isinstance(value, str):
        return f'@"{value}"'
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, dict):
        items = [f"{k} : {convert_value(v)}" for k, v in value.items()]
        return "{\n    " + ",\n    ".join(items) + "\n}"
    else:
        raise ValueError(f"Unsupported type: {type(value)}")

def convert_comments(comment):
    if not comment or callable(comment):  # Add check for callable
        return ""
    lines = str(comment).split('\n')  # Convert to string first
    if len(lines) == 1:
        return f"%{lines[0]}\n"
    return "<!--\n" + "\n".join(line.strip('# ') for line in lines if line.strip()) + "\n-->\n"

def convert_toml(toml_doc: TOMLDocument) -> str:
    result = []

    def process_table(table, prefix=""):
        for key, value in table.items():
            full_key = f"{prefix}_{key}" if prefix else key
            if hasattr(value, "comment"):
                comment = convert_comments(value.comment)
                if comment:
                    result.append(comment)
            if hasattr(value, "value"):
                val = value.value
            else:
                val = value

            if isinstance(val, dict):
                process_table(val, full_key)
            else:
                result.append(f"var {full_key} = {convert_value(val)};")

    process_table(toml_doc)
    return "\n".join(result)

def main():
    if len(sys.argv) != 3:
        print("Usage: python main.py input.toml output.conf")
        return 1

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    try:
        with open(input_path, 'r') as f:
            toml_content = f.read()

        toml_doc = parse(toml_content)
        converted = convert_toml(toml_doc)

        with open(output_path, 'w') as f:
            f.write(converted)

        return 0
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
