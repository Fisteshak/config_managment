import unittest
import os
import platform
import tarfile
from io import BytesIO
from main import CommandProcessor

class TestCommandProcessor(unittest.TestCase):
    def setUp(self):
        # Create a test tar file with sample structure
        self.test_tar_path = 'test_fs.tar'
        with tarfile.open(self.test_tar_path, 'w') as tar:
            # Add home directory
            info = tarfile.TarInfo('test_fs/home')
            info.type = tarfile.DIRTYPE
            tar.addfile(info)
            
            # Add olya directory
            info = tarfile.TarInfo('test_fs/home/olya')
            info.type = tarfile.DIRTYPE
            tar.addfile(info)
            
            # Add test file
            test_file_content = b"Hello, World!"
            info = tarfile.TarInfo('test_fs/home/test_file.txt')
            info.size = len(test_file_content)
            tar.addfile(info, fileobj=BytesIO(test_file_content))

        # Initialize the CommandProcessor instance
        self.processor = CommandProcessor('user', 'computer', self.test_tar_path)   

    def tearDown(self):
        self.processor.exit()
        if os.path.exists(self.test_tar_path):
            os.remove(self.test_tar_path)

    def test_cd(self):
        # Test changing to an existing directory
        output = self.processor.cd('home')
        output = self.processor.cd('olya')
        self.assertEqual(self.processor.current_dir, 'test_fs/home/olya')
        self.assertEqual(output, "")

        # Test changing to a non-existing directory
        output = self.processor.cd('non_existing_dir')
        self.assertEqual(output, "cd: no such file or directory\n")

        output = self.processor.cd("..")
        output = self.processor.cd("..")

    def test_ls(self):
        # Test listing files in root directory

        output = self.processor.ls()

        self.assertIn('home', output)
        
        # Test listing files in nested directory
        self.processor.cd('home')
        output = self.processor.ls()
        self.assertIn('test_file.txt', output)

        self.processor.cd("..")

    def test_cat(self):
        # Test reading an existing file
        output = self.processor.cat('home/test_file.txt')
        self.assertEqual(output, "Hello, World!\n")

        # Test reading a non-existing file
        output = self.processor.cat('non_existing_file.txt')
        self.assertEqual(output, "cat: non_existing_file.txt: No such file\n")

    def test_uname(self):
        output = self.processor.uname()
        self.assertEqual(output, platform.system() + "\n")

    def test_rmdir(self):
        # Test removing a non-existing directory
        output = self.processor.rmdir('non_existing_dir')
        self.assertEqual(output, "rmdir: non_existing_dir: No such directory\n")

        # Test removing an existing directory
        output = self.processor.ls()
        output = self.processor.cd('home')
        output = self.processor.ls()
        output = self.processor.rmdir('olya')
        self.assertEqual(output, "Directory olya removed successfully\n")

    def test_exit(self):
        # Test the exit command
        output = self.processor.exit()
        self.assertEqual(output, "")

    def test_get_prompt(self):
        self.assertEqual(self.processor.get_prompt(), "user@computer:/$ ")
        self.processor.cd('home')
        self.assertEqual(self.processor.get_prompt(), "user@computer:/home$ ")

if __name__ == "__main__":
    unittest.main()