import unittest
import os
import sys
from GraphGenerator import GraphGenerator
import main

class TestAll(unittest.TestCase):
    def setUp(self):
        self.test_output = "test_output.txt"
        self.generator = GraphGenerator(self.test_output, 3)
        
    def tearDown(self):
        if os.path.exists(self.test_output):
            os.remove(self.test_output)

    def test_package_operations(self):
        # Test package installation and detection
        self.assertTrue(self.generator.install_package("requests"))
        self.assertTrue(self.generator.is_package_installed("requests"))
        
        info = self.generator.get_package_info("requests")
        self.assertIsNotNone(info)
        self.assertIn("requests", info)

    def test_dependency_parsing(self):
        package_info = self.generator.get_package_info("requests")
        deps = self.generator.parse_dependencies(package_info)
        self.assertIsInstance(deps, list)
        self.assertTrue(len(deps) > 0)

    def test_graph_generation(self):
        # Test full graph generation
        self.assertTrue(self.generator.generate_mermaid("requests"))
        self.assertTrue(os.path.exists(self.test_output))
        
        with open(self.test_output, 'r') as f:
            content = f.read()
            self.assertIn("graph TD", content)
            self.assertIn("requests -->", content)

    def test_main_functionality(self):
        test_args = ['--output', self.test_output, '--package', 'requests', '--max-depth', '2']
        sys.argv[1:] = test_args
        
        main.main()
        self.assertTrue(os.path.exists(self.test_output))
        
        with open(self.test_output, 'r') as f:
            content = f.read()
            self.assertIn("graph TD", content)

if __name__ == '__main__':
    unittest.main()