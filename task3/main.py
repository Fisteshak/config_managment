import sys
from pathlib import Path
from tomlkit import parse, TOMLDocument
from tomlkit.items import Comment, Table, Array, Whitespace

def convert_value(value, indent=0):
    if isinstance(value, (str)):
        # Escape quotes and use @ for raw strings
        escaped = value.replace('"', '""')
        return f'@"{escaped}"'
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (dict, Table)):
        items = []
        next_indent = indent + 4
        indent_str = " " * indent
        next_indent_str = " " * next_indent
        for k, v in dict(value).items():
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

def convert_toml(toml_doc: TOMLDocument) -> str:
    result = []
    sections = {}
    current_section = "root"

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
                result.append(f"var {key} = {convert_value(value)};")

    # Process other sections
    for section, items in sections.items():
        if section == "root":
            continue

        section_items = []
        for item in items:
            if isinstance(item, str):  # Comment
                section_items.append(item)
            else:  # Key-value pair
                key, value = item
                if isinstance(value, Table):
                    section_items.append(f"    {key} = {convert_value(value)}")
                else:
                    section_items.append(f"    {key} = {convert_value(value)}")

        if section_items:
            result.append(f"var {section} = {{")
            result.extend(section_items)
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
