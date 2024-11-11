import subprocess
import json
import sys
import argparse

class DependencyGraphGenerator:
    def __init__(self, output_path, max_depth):
        self.output_path = output_path
        self.max_depth = max_depth
        self.dependencies = set()

    def is_package_installed(self, package):
        try:
            result = subprocess.check_output([sys.executable, '-m', 'pip', 'list'])
            installed_packages = [line.split()[0].lower() for line in result.decode().split('\n')[2:] if line]
            return package.lower() in installed_packages
        except subprocess.CalledProcessError:
            return False

    def install_package(self, package):
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            return True
        except subprocess.CalledProcessError:
            print(f"Failed to install {package}")
            return False

    def get_package_info(self, package):
        try:
            result = subprocess.check_output([sys.executable, '-m', 'pip', 'show', package])
            return result.decode('utf-8')
        except subprocess.CalledProcessError:
            return None

    def parse_dependencies(self, package_info):
        if not package_info:
            return []
        
        for line in package_info.split('\n'):
            if line.startswith('Requires:'):
                deps = line.replace('Requires:', '').strip()
                return [dep.strip() for dep in deps.split(',') if dep.strip()]
        return []

    def build_dependency_tree(self, package, current_depth=0):
        if current_depth >= self.max_depth:
            return

        package_info = self.get_package_info(package)
        dependencies = self.parse_dependencies(package_info)

        for dep in dependencies:
            if dep:
                self.dependencies.add(f"{package} --> {dep}")
                if not self.is_package_installed(dep):
                    if not self.install_package(dep):
                        continue
                self.build_dependency_tree(dep, current_depth + 1)

    def generate_mermaid(self, package):
        if not self.is_package_installed(package):
            if not self.install_package(package):
                print(f"Failed to install {package}. Cannot generate dependency graph.")
                return

        mermaid_text = "graph TD\n"
        self.build_dependency_tree(package)
        
        for dep in sorted(self.dependencies):
            mermaid_text += f"    {dep}\n"

        with open(self.output_path, 'w') as f:
            f.write(mermaid_text)

def main():
    parser = argparse.ArgumentParser(description='Generate dependency graph in Mermaid format')
    parser.add_argument('--output', required=True, help='Path to output Mermaid file')
    parser.add_argument('--package', required=True, help='Package name to analyze')
    parser.add_argument('--max-depth', type=int, default=5, help='Maximum depth of dependency tree')

    args = parser.parse_args()

    generator = DependencyGraphGenerator(args.output, args.max_depth)
    generator.generate_mermaid(args.package)

if __name__ == "__main__":
    main()