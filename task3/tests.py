import unittest
from tomlkit import parse
from main import convert_toml, evaluate_expression

class TestTOMLConverter(unittest.TestCase):
    def test_basic_types(self):
        toml_str = """
        string = "hello"
        integer = 42
        float = 3.14
        """
        expected = '\n'.join([
            'string  = @"hello";',
            'integer  = 42;',
            'float  = 3.14;',
        ])
        result = convert_toml(parse(toml_str))
        self.assertEqual(result.strip(), expected.strip())

    def test_nested_tables(self):
        toml_str = """
        [database]
        enabled = true
        port = 8000

        [database.credentials]
        user = "admin"
        pass = "123456"
        """
        expected = '\n'.join([
            'database = {',
            '    enabled : true',
            '    port : 8000',
            '    credentials : {',
            '        user : @"admin",',
            '        pass : @"123456"',
            '    }',
            '};'
        ])
        result = convert_toml(parse(toml_str))
        self.assertEqual(result.strip(), expected.strip())

    def test_inline_tables(self):
        toml_str = """
        point = { x = 10, y = 20 }
        nested = { outer = { inner = 42 } }
        """
        expected = '\n'.join([
            'point  = {',
            '    x : 10,',
            '    y : 20',
            '};',
            'nested  = {',
            '    outer : {',
            '        inner : 42',
            '    }',
            '};'
        ])
        result = convert_toml(parse(toml_str))
        self.assertEqual(result.strip(), expected.strip())

    def test_arrays(self):
        pass

    def test_comments(self):
        toml_str = """
        # Single comment
        value1 = 1

        # Multi-line
        # comment
        # block
        value2 = 2
        """
        expected = '\n'.join([
            '% Single comment',
            'value1  = 1;',
            '<!--',
            'Multi-line',
            'comment',
            'block',
            '-->',
            'value2  = 2;'
        ])
        result = convert_toml(parse(toml_str))
        self.assertEqual(result.strip(), expected.strip())



    def test_invalid_expressions(self):
        with self.assertRaises(ValueError):
            evaluate_expression("?(a)", {"a": 1})  # Too few operands
        with self.assertRaises(ValueError):
            evaluate_expression("?(a b)", {"a": 1, "b": 2})  # No operator
        with self.assertRaises(ValueError):
            evaluate_expression("?(a b + c)", {"a": 1, "b": 2, "c": 3})  # Too many operands
        with self.assertRaises(ValueError):
            evaluate_expression("?(a b /)", {"a": 1, "b": 0})  # Division by zero
        with self.assertRaises(ValueError):
            evaluate_expression("?(a b mod)", {"a": 1, "b": 0})  # Modulo by zero

    def test_invalid_names(self):
        invalid_cases = [
            "1name = 42",
            "[2section]",
            "[valid.3subsection]",
            "valid-name = 42",
            "[invalid-section]"
        ]
        for case in invalid_cases:
            with self.assertRaises(ValueError):
                convert_toml(parse(case))

if __name__ == '__main__':
    unittest.main()