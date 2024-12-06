import tomllib
import argparse
import sys
from typing import Any, Dict

class ConfigConverter:
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.indent_level = 0
        self.indent_size = 4

    def indent(self) -> str:
        return " " * (self.indent_level * self.indent_size)

    def convert_value(self, value: Any) -> str:
        if isinstance(value, str):
            return f'@"{value}"'
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, dict):
            return self.convert_dict(value)
        else:
            raise ValueError(f"Unsupported value type: {type(value)}")

    def convert_dict(self, data: Dict[str, Any]) -> str:
        if not data:
            return "{}"
        items = []
        self.indent_level += 1
        for key, value in data.items():
            if not key.isidentifier():
                raise ValueError(f"Invalid identifier: {key}")
            items.append(f"{self.indent()}{key} : {self.convert_value(value)}")
        self.indent_level -= 1
        return "{\n" + ",\n".join(items) + f"\n{self.indent()}}}"

    def convert_top_level(self, data: Dict[str, Any]) -> list[str]:
        items = []
        for key, value in data.items():
            if not key.isidentifier():
                raise ValueError(f"Invalid identifier: {key}")
            items.append(f"{key} : {self.convert_value(value)}")
        return items



def main():
    parser = argparse.ArgumentParser(description='Convert TOML to custom config format')
    parser.add_argument('input', help='Input TOML file path')
    parser.add_argument('output', help='Output file path')
    args = parser.parse_args()

    try:
        with open(args.input, 'rb') as f:
            toml_data = tomllib.load(f)
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    except tomllib.TOMLDecodeError as e:
        print(f"Error parsing TOML: {e}", file=sys.stderr)
        sys.exit(1)

    converter = ConfigConverter()

    try:
        output = []
        if 'var' in toml_data:
            for var_name, value in toml_data['var'].items():
                if not var_name.isidentifier():
                    raise ValueError(f"Invalid variable name: {var_name}")
                converter.variables[var_name] = value
                output.append(f"var {var_name} = {converter.convert_value(value)};")

        if 'expr' in toml_data:
            for expr in toml_data['expr']:
                result = converter.evaluate_expression(expr)
                output.append(f"?({expr}) % = {result}")

        main_config = {k: v for k, v in toml_data.items() if k not in ['var', 'expr']}
        if main_config:
            output.extend(converter.convert_top_level(main_config))

        with open(args.output, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

