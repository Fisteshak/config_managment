import sys
from pathlib import Path
import re
from tomlkit import parse, TOMLDocument
from tomlkit.items import Comment, Table, Array, Whitespace
from typing import Dict, Any

def convert_value(value, indent=0):
    if isinstance(value, (str)):
        # Validate string literal
        try:
            # Check if string is properly terminated
            if value.count('"') % 2 != 0:
                raise ValueError("Unterminated string literal")
            # Escape quotes and use @ for raw strings
            escaped = value.replace('"', '""')
            return f'@"{escaped}"'
        except Exception as e:
            raise ValueError(f"Invalid string literal: {str(e)}")
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (dict, Table)):
        items = []
        next_indent = indent + 4
        indent_str = " " * indent
        next_indent_str = " " * next_indent
        dict_items = list(dict(value).items())
        for k, v in dict_items:
            converted = convert_value(v, next_indent)
            items.append(f"{next_indent_str}{k} : {converted}")
        return "{\n" + ",\n".join(items) + f"\n{indent_str}}}"
    if isinstance(value, (list, tuple, Array)):
        items = [convert_value(v, indent) for v in value]
        return f"[{', '.join(items)}]"
    return str(value)

def convert_comments(comment):
    if not comment:
        return ""
    comment_str = str(comment).strip()
    if not comment_str:
        return ""
    lines = [line.strip('# ') for line in comment_str.split('\n') if line.strip()]
    return "".join(f"% {line}\n" for line in lines).rstrip('\n')  # Remove trailing newline

def validate_name(name: str) -> bool:
    if not name or not isinstance(name, str):
        return False
    pattern = re.compile(r'^[_a-zA-Z][_a-zA-Z0-9]*$')
    return bool(pattern.match(name))

def validate_table_recursively(table: Table, path=""):
    for key, value in table.items():
        if not validate_name(str(key)):
            full_path = f"{path}.{key}" if path else key
            raise ValueError(f"Invalid key name: {full_path}. Names must start with a letter or underscore and contain only alphanumeric characters and underscores.")

        if isinstance(value, Table):
            validate_table_recursively(value, f"{path}.{key}" if path else key)
        elif isinstance(value, dict):
            for k in value.keys():
                if not validate_name(k):
                    full_path = f"{path}.{key}.{k}" if path else f"{key}.{k}"
                    raise ValueError(f"Invalid key name: {full_path}. Names must start with a letter or underscore and contain only alphanumeric characters and underscores.")

def evaluate_expression(expr: str, variables: Dict[str, Any]) -> Any:
    if not expr.startswith("?(") or not expr.endswith(")"):
        return expr

    # Remove "?(" and ")" and split into tokens
    tokens = expr[2:-1].strip().split()
    if len(tokens) < 3:
        raise ValueError(f"Invalid expression: {expr}")

    stack = []
    for token in tokens:
        if token in {"+", "-", "*", "\\", "max", "mod"}:
            if len(stack) < 2:
                raise ValueError(f"Invalid expression: not enough operands for {token}")
            b = stack.pop()
            a = stack.pop()

            if isinstance(a, str) and a in variables:
                a = variables[a]
            if isinstance(b, str) and b in variables:
                b = variables[b]

            try:
                a, b = float(a), float(b)
                if token == "+":
                    stack.append(a + b)
                elif token == "-":
                    stack.append(a - b)
                elif token == "*":
                    stack.append(a * b)
                elif token == "\\":
                    if b == 0:
                        raise ValueError("Division by zero")
                    stack.append(a / b)
                elif token == "max":
                    stack.append(max(a, b))
                elif token == "mod":
                    if b == 0:
                        raise ValueError("Modulo by zero")
                    stack.append(a % b)
            except ValueError as e:
                raise ValueError(f"Invalid operands for {token}: {a}, {b}")
        else:
            stack.append(token)

    if len(stack) != 1:
        raise ValueError(f"Invalid expression: too many operands")
    return stack[0]

def convert_toml(toml_doc: TOMLDocument) -> str:
    result = []
    sections = {}
    current_section = "root"
    variables = {}

    # First pass: collect all variables
    for item in toml_doc.body:
        if isinstance(item[1], (Whitespace, Comment)):
            continue
        key, value = item
        if not isinstance(value, Table):
            if isinstance(value, str):
                variables[key.key] = value
            else:
                variables[key.key] = value

    # Second pass: evaluate expressions
    for item in toml_doc.body:
        if isinstance(item[1], (Whitespace, Comment)):
            continue
        key, value = item
        if isinstance(value, str) and value.startswith("?("):
            variables[key.key] = evaluate_expression(value, variables)

    # Validate section names and keys
    for item in toml_doc.body:
        if isinstance(item[1], (Whitespace, Comment)):
            continue

        key, value = item
        if not validate_name(key.key):
            raise ValueError(f"Invalid name: {key}. Names must start with a letter and contain only alphanumeric characters and underscores.")

        if isinstance(value, Table):
            if not validate_name(key.key):
                raise ValueError(f"Invalid section name: {key}. Section names must start with a letter and contain only alphanumeric characters and underscores.")
            validate_table_recursively(value, key)

    # Collect items in sections
    for item in toml_doc.body:
        if isinstance(item[1], Whitespace):
            continue
        if isinstance(item[1], Comment):
            comment = convert_comments(item[1])
            if comment:
                if current_section not in sections:
                    sections[current_section] = []
                sections[current_section].append(comment)
            continue

        key, value = item
        if isinstance(value, Table):
            current_section = key
            if "." in key:
                parent, child = key.split(".", 1)
                if parent not in sections:
                    sections[parent] = []
                sections[parent].append((child, value))
            else:
                if key not in sections:
                    sections[key] = []
                sections[key].extend([(k, v) for k, v in dict(value).items()])
        else:
            if current_section not in sections:
                sections[current_section] = []
            sections[current_section].append((key, value))

    # Process comments to merge sequential ones
    for section in sections:
        merged_items = []
        comment_buffer = []

        for item in sections[section]:
            if isinstance(item, str) and item.startswith('%'):  # Is comment
                comment_buffer.append(item.strip('% \n'))
            else:
                if comment_buffer:  # Flush comment buffer
                    if len(comment_buffer) > 1:
                        merged_comment = "<!--\n" + "\n".join(comment_buffer) + "\n-->"
                    else:
                        merged_comment = f"% {comment_buffer[0]}"
                    merged_items.append(merged_comment)
                    comment_buffer = []
                merged_items.append(item)

        if comment_buffer:  # Don't forget remaining comments
            if len(comment_buffer) > 1:
                merged_comment = "<!--\n" + "\n".join(comment_buffer) + "\n-->"
            else:
                merged_comment = f"% {comment_buffer[0]}"
            merged_items.append(merged_comment)

        sections[section] = merged_items

    # Process root section first
    if "root" in sections:
        for item in sections["root"]:
            if isinstance(item, str):  # Comment
                result.append(item)
            else:  # Key-value pair
                key, value = item
                if isinstance(value, str) and value.startswith("?("):
                    value = variables[key]
                result.append(f"{key} = {convert_value(value)};")

    # Process other sections
    for section, items in sections.items():
        if section == "root":
            continue

        if items:
            result.append(f"{section} = {{")
            for item in items:
                if isinstance(item, str):  # Comment
                    result.append(f"    {item}")
                else:  # Key-value pair
                    key, value = item
                    if isinstance(value, Table):
                        result.append(f"    {key} : {convert_value(value, 4)}")
                    else:
                        result.append(f"    {key} : {convert_value(value)}")
            result.append("};")

    return "\n".join(result)

def main():
    if len(sys.argv) != 3:
        input_path = "D:\\Projects\\config_managment\\task3\\example.toml"
        output_path = "output.conf"
    else:

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
    main()
