import unittest
import os
import platform
import json
from main import CommandProcessor

class TestCommandProcessor(unittest.TestCase):
    def setUp(self):
        # Create a temporary config file for testing
        self.config_data = {
            "user_name": "test_user",
            "computer_name": "test_computer",
            "path": "fs.tar"
        }
        with open('test_config.json', 'w') as config_file:
            json.dump(self.config_data, config_file)

        # Initialize the CommandProcessor instance
        self.processor = CommandProcessor('test_config.json')

    def tearDown(self):
        # Clean up the test configuration file
        if os.path.isfile('test_config.json'):
            os.remove('test_config.json')

    def test_cd(self):
        # Test changing to an existing directory
        output = self.processor.cd('home/olya')
        self.assertEqual(self.processor.current_dir, os.path.join(self.processor.extracted_dir, 'home', 'olya'))
        self.assertEqual(output, "")

        # Test changing to a non-existing directory
        output = self.processor.cd('non_existing_dir')
        self.assertEqual(self.processor.current_dir, os.path.join(self.processor.extracted_dir, 'home', 'olya'))
        self.assertEqual(output, "cd: no such file or directory\n")

    def test_ls(self):
        # Test listing files in the current directory
        self.processor.cd('home/olya')
        output = self.processor.ls()
        self.assertIn('test_file.txt', output)

    def test_cat(self):
        # Test reading an existing file
        output = self.processor.cat('home/olya/test_file.txt')
        self.assertEqual(output, "Hello, World!\n")

        # Test reading a non-existing file
        output = self.processor.cat('home/olya/non_existing_file.txt')
        self.assertEqual(output, "cat: home/olya/non_existing_file.txt: No such file\n")

    def test_uname(self):
        # Test getting the system name
        output = self.processor.uname()
        self.assertEqual(output, platform.system() + "\n")

    def test_rmdir(self):
        # Test removing an existing directory
        self.processor.cd('home')
        output = self.processor.rmdir('test_dir')
        self.assertEqual(output, "rmdir: test_dir: No such directory\n")
        self.assertFalse(os.path.isdir(os.path.join(self.processor.extracted_dir, 'home', 'test_dir')))

        # Test removing a non-existing directory
        output = self.processor.rmdir('non_existing_dir')
        self.assertEqual(output, "rmdir: non_existing_dir: No such directory\n")

    def test_exit(self):
        # Test the exit command
        output = self.processor.exit()
        self.assertEqual(output, "")

if __name__ == "__main__":
    unittest.main()