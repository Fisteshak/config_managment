import argparse
import csv

LOAD_CONST = 0x0F
READ_MEM = 0x03
WRITE_MEM = 0x04
POP_CNT = 0x06

def encode_command(cmd_tuple):
    if cmd_tuple[0] == "LOAD_CONST":
        return (LOAD_CONST << 24) | (cmd_tuple[1] & 0xFFFFFF)
    elif cmd_tuple[0] == "READ_MEM":
        return READ_MEM << 24
    elif cmd_tuple[0] == "WRITE_MEM":
        return (WRITE_MEM << 24) | (cmd_tuple[1] & 0xFFFFFF)
    elif cmd_tuple[0] == "POP_CNT":
        return (POP_CNT << 24) | (cmd_tuple[1] & 0xFFFFFF)
    return 0

def parse_file(file_path):
    raw_commands = []
    line_number = 0

    try:
        with open(file_path, 'r') as file:
            for line in file:
                line_number += 1
                line = line.split('#')[0].strip()
                if not line:
                    continue

                parts = line.split()
                cmd = parts[0] if parts else ""
                try:
                    if cmd == "LOAD_CONST":
                        if len(parts) != 2:
                            raise ValueError("LOAD_CONST requires a decimal value")
                        value = int(parts[1], 10)  # base 10 for decimal
                        raw_commands.append(("LOAD_CONST", value))

                    elif cmd == "READ_MEM":
                        if len(parts) != 1:
                            raise ValueError("READ_MEM takes no arguments")
                        raw_commands.append(("READ_MEM",))

                    elif cmd == "WRITE_MEM":
                        if len(parts) != 2:
                            raise ValueError("WRITE_MEM requires a decimal value")
                        value = int(parts[1], 10)  # base 10 for decimal
                        raw_commands.append(("WRITE_MEM", value))

                    elif cmd == "POP_CNT":
                        if len(parts) != 2:
                            raise ValueError("POP_CNT requires a decimal value")
                        value = int(parts[1], 10)  # base 10 for decimal
                        raw_commands.append(("POP_CNT", value))

                    else:
                        raise ValueError(f"Unknown command: {cmd}")

                except (ValueError, IndexError) as e:
                    print(f"Error on line {line_number}: {str(e)}")
                    print(f"Line content: '{line}'")
                    continue

    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        return []
    except Exception as e:
        print(f"Error parsing file: {e}")
        return []

    return [encode_command(cmd) for cmd in raw_commands]

def write_binary(commands, output_path):
    with open(output_path, 'wb') as f:
        for cmd in commands:
            f.write(bytes([
                (cmd >> 24) & 0xFF,    # opcode
                (cmd >> 16) & 0xFF,   # byte2
                (cmd >> 8) & 0xFF,    # byte1
                cmd & 0xFF,           # byte0
            ]))

def write_log(commands, log_path):
    with open(log_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Command', 'Hex Value', 'Binary'])
        for cmd in commands:
            opcode = (cmd >> 24) & 0xFF
            cmd_name = {
                LOAD_CONST: 'LOAD_CONST',
                READ_MEM: 'READ_MEM',
                WRITE_MEM: 'WRITE_MEM',
                POP_CNT: 'POP_CNT'
            }.get(opcode, 'UNKNOWN')
            # Format each 4 bits separately
            m = [f"{(cmd >> (i * 4)) & 0xF:X}" for i in range(7, -1, -1)]
            hex_value = ', '.join(["0x" + m[7] + m[1], "0x" + m[5] + m[6], "0x" + m[3] + m[4], "0x" + m[0] + m[2]])
            writer.writerow([
                f"{cmd_name}".strip(),
                hex_value,
            ])

def main():
    parser = argparse.ArgumentParser(description='Assembly-like command processor')
    parser.add_argument('input', help='Input file path')
    parser.add_argument('output', help='Output binary file path')
    parser.add_argument('--log', help='Output log file path')
    args = parser.parse_args()

    commands = parse_file(args.input)
    write_binary(commands, args.output)
    if args.log:
        write_log(commands, args.log)

if __name__ == "__main__":
    main()