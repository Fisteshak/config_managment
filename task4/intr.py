import argparse
import csv

class Interpreter:
    LOAD_CONST = 0x0F
    READ_MEM = 0x03
    WRITE_MEM = 0x04
    POP_CNT = 0x06

    def __init__(self):
        self.memory = dict()
        self.ax = 0

    def read_binary(self, file_path):
        commands = []
        with open(file_path, 'rb') as f:
            while True:
                bytes_read = f.read(4)
                if not bytes_read:
                    break
                if len(bytes_read) < 4:
                    print("Incomplete command at the end of file")
                    break
                cmd = int.from_bytes(bytes_read, byteorder='big')
                commands.append(cmd)
        return commands

    def save_results(self, result_path, mem_range):
        start, end = mem_range
        with open(result_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Register', 'Value'])
            writer.writerow(['ax', self.ax])
            writer.writerow([])
            writer.writerow(['Address', 'Value'])
            for addr in range(start, end + 1):
                value = self.memory.get(addr, 0)
                if value != 0:
                    writer.writerow([addr, value])

    def execute_commands(self, commands):
        for cmd in commands:
            opcode = (cmd >> 24) & 0xFF
            operand = cmd & 0xFFFFFF
            if opcode == self.LOAD_CONST:
                self.ax = operand
            elif opcode == self.READ_MEM:
                print(self.memory)
                if self.memory.get(self.ax) != None:
                    self.ax = self.memory.get(self.ax)
                else:
                    self.ax = 0
            elif opcode == self.WRITE_MEM:
                self.memory[operand] = self.ax
            elif opcode == self.POP_CNT:
                self.memory[operand] = self.ax
            else:
                print(f"Unknown opcode: {opcode}")

def main():
    parser = argparse.ArgumentParser(description='Interpreter for binary commands')
    parser.add_argument('input', help='Input binary file path')
    parser.add_argument('result', help='Result file path')
    parser.add_argument('mem_range', nargs=2, type=int, metavar=('START', 'END'),
                        help='Range of memory addresses to save')

    args = parser.parse_args()
    interpreter = Interpreter()
    commands = interpreter.read_binary(args.input)
    interpreter.execute_commands(commands)
    interpreter.save_results(args.result, args.mem_range)

if __name__ == "__main__":
    main()