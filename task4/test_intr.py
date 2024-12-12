import unittest
import os
import subprocess
import csv
from intr import Interpreter

class TestInterpreter(unittest.TestCase):
    def setUp(self):
        # Prepare a test binary file
        self.binary_file = 'test_commands.bin'
        self.result_file = 'test_result.csv'
        self.start_addr = '0'
        self.end_addr = '200'
        self.interpreter = Interpreter()

    def tearDown(self):
        # Clean up test files
        if os.path.exists(self.binary_file):
            os.remove(self.binary_file)
        if os.path.exists(self.result_file):
            os.remove(self.result_file)

    def test_load_const(self):
        commands = [(Interpreter.LOAD_CONST << 24) | 42]
        self.interpreter.execute_commands(commands)
        self.assertEqual(self.interpreter.ax, 42)

    def test_write_and_read_memory(self):
        commands = [
            (Interpreter.LOAD_CONST << 24) | 42,
            (Interpreter.WRITE_MEM << 24) | 100,
            (Interpreter.READ_MEM << 24) | 100
        ]
        self.interpreter.execute_commands(commands)
        self.assertEqual(self.interpreter.memory[100], 42)
        self.assertEqual(self.interpreter.ax, 0)

    def test_pop_cnt(self):
        commands = [
            (Interpreter.LOAD_CONST << 24) | 10,
            (Interpreter.POP_CNT << 24) | 50
        ]
        self.interpreter.execute_commands(commands)
        self.assertEqual(self.interpreter.memory[50], 10)


    def test_execute_commands(self):
        # Create test commands
        with open(self.binary_file, 'wb') as f:
            # LOAD_CONST 10
            f.write((Interpreter.LOAD_CONST << 24 | 10).to_bytes(4, 'big'))
            # WRITE_MEM 100
            f.write((Interpreter.WRITE_MEM << 24 | 100).to_bytes(4, 'big'))
            # READ_MEM 100
            f.write((Interpreter.READ_MEM << 24 | 100).to_bytes(4, 'big'))
            # POP_CNT 50
            f.write((Interpreter.POP_CNT << 24 | 50).to_bytes(4, 'big'))

        # Run the interpreter
        subprocess.run(['python', 'intr.py', self.binary_file, self.result_file, self.start_addr, self.end_addr])

        # Verify the result CSV file
        with open(self.result_file, 'r', newline='') as f:
            reader = csv.reader(f)
            rows = list(reader)

            # Check ax value
            self.assertIn(['Register', 'Value'], rows)
            ax_index = rows.index(['Register', 'Value']) + 1
            self.assertEqual(rows[ax_index], ['ax', '0'])

            # Check memory values
            self.assertIn(['Address', 'Value'], rows)
            mem_index = rows.index(['Address', 'Value']) + 1
            memory_rows = rows[mem_index:]

            expected_memory = {'50': '10', '100': '10'}
            for addr, value in memory_rows:
                self.assertEqual(expected_memory.get(addr), value)

if __name__ == '__main__':
    unittest.main()