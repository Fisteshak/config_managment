import unittest
import subprocess
import os
from asm import encode_command, parse_file, write_binary, write_log

class TestAssembler(unittest.TestCase):
    def setUp(self):
        # Prepare test assembly and output files
        self.assembly_file = 'test_commands.asm'
        self.binary_file = 'test_commands.bin'
        self.log_file = 'test_log.csv'

    def tearDown(self):
        # Clean up test files
        if os.path.exists(self.assembly_file):
            os.remove(self.assembly_file)
        if os.path.exists(self.binary_file):
            os.remove(self.binary_file)
        if os.path.exists(self.log_file):
            os.remove(self.log_file)

    def test_assemble_commands(self):
        # Create test assembly commands
        with open(self.assembly_file, 'w') as f:
            f.write('LOAD_CONST 10\n')
            f.write('WRITE_MEM 100\n')
            f.write('READ_MEM\n')
            f.write('POP_CNT 50\n')

        # Run the assembler
        result = subprocess.run(
            ['python', 'asm.py', self.assembly_file, self.binary_file, '--log', self.log_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Check if assembler ran successfully
        if result.returncode != 0:
            print("asm.py failed with return code", result.returncode)
            print("stdout:", result.stdout)
            print("stderr:", result.stderr)
            self.fail("asm.py failed to assemble commands")

        # Verify the binary file exists
        if not os.path.exists(self.binary_file):
            self.fail(f"Binary file {self.binary_file} was not created")

        # Verify the binary file contents
        with open(self.binary_file, 'rb') as f:
            commands = f.read()
            self.assertEqual(len(commands), 16)  # 4 commands * 4 bytes
            cmds = [int.from_bytes(commands[i:i+4], 'big') for i in range(0, len(commands), 4)]
            expected_cmds = [
                (0x0F << 24) | 10,
                (0x04 << 24) | 100,
                0x03 << 24,
                (0x06 << 24) | 50
            ]
            self.assertEqual(cmds, expected_cmds)

        # Verify the log file
        self.assertTrue(os.path.exists(self.log_file))

    def test_encode_command(self):
        test_cases = [
            (("LOAD_CONST", 42), 0x0F00002A),
            (("READ_MEM",), 0x03000000),
            (("WRITE_MEM", 100), 0x04000064),
            (("POP_CNT", 50), 0x06000032),
        ]
        for cmd_tuple, expected in test_cases:
            with self.subTest(cmd=cmd_tuple):
                result = encode_command(cmd_tuple)
                self.assertEqual(result, expected)

    def test_parse_file_errors(self):
        # Test invalid commands
        with open(self.assembly_file, 'w') as f:
            f.write('INVALID_CMD 10\n')
            f.write('LOAD_CONST\n')  # Missing operand
            f.write('READ_MEM 42\n')  # Extra operand
            f.write('WRITE_MEM\n')   # Missing operand

        commands = parse_file(self.assembly_file)
        self.assertEqual(commands, [])  # Should return empty list for invalid commands

    def test_write_binary_format(self):
        test_cmd = (0x0F << 24) | 42  # LOAD_CONST 42
        write_binary([test_cmd], self.binary_file)

        with open(self.binary_file, 'rb') as f:
            data = f.read()
            self.assertEqual(len(data), 4)
            cmd = int.from_bytes(data, 'big')
            self.assertEqual(cmd, test_cmd)

if __name__ == '__main__':
    unittest.main()