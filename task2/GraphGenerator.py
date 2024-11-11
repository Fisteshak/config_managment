import subprocess
import json
import sys
import argparse
from subprocess import DEVNULL

class GraphGenerator:
    def __init__(self, output_path, max_depth):
        self.output_path = output_path
        self.max_depth = max_depth
        self.dependencies = set()
        self.installed_packages = set()
        self._refresh_installed_packages()

    def _refresh_installed_packages(self):
        self.log("Refreshing list of installed packages")
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'list'],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                self.log("Failed to get list of installed packages")
                return
                
            self.installed_packages = {
                line.split()[0].lower() 
                for line in result.stdout.split('\n')[2:] 
                if line
            }
            self.log(f"Found {len(self.installed_packages)} installed packages")
        except subprocess.SubprocessError:
            self.log("Failed to refresh installed packages list")

    def log(self, message):
        print(f"{message}")

    def is_package_installed(self, package):
        self.log(f"Checking if package is installed: {package}")
        is_installed = package.lower() in self.installed_packages
        self.log(f"Package {package} is {'installed' if is_installed else 'not installed'}")
        return is_installed
    
    def install_package(self, package):
        self.log(f"Installing package: {package}")
        try:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', package],
                stdout=DEVNULL,
                stderr=DEVNULL
            )
            self.log(f"Successfully installed {package}")
            self._refresh_installed_packages()  # Update cache after installation
            return True
        except subprocess.CalledProcessError:
            self.log(f"Failed to install {package}")
            return False

    def get_package_info(self, package):
        self.log(f"Getting info for package: {package}")
        try:
            result = subprocess.check_output(
                [sys.executable, '-m', 'pip', 'show', package],
                stderr=DEVNULL
            )
            return result.decode('utf-8')
        except subprocess.CalledProcessError:
            self.log(f"Failed to get info for {package}")
            return None

    def parse_dependencies(self, package_info):
        if not package_info:
            return []
        
        for line in package_info.split('\n'):
            if line.startswith('Requires:'):
                deps = line.replace('Requires:', '').strip()
                dependencies = [dep.strip() for dep in deps.split(',') if dep.strip()]
                self.log(f"Found dependencies: {', '.join(dependencies) if dependencies else 'none'}")
                return dependencies
        return []

    def build_dependency_tree(self, package, current_depth=0):
        if current_depth >= self.max_depth:
            self.log(f"Reached max depth {self.max_depth} for {package}")
            return

        self.log(f"Building dependency tree for {package} (depth: {current_depth})")
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
        self.log(f"Starting graph generation for {package}")
        if not self.is_package_installed(package):
            if not self.install_package(package):
                self.log(f"Failed to install {package}. Cannot generate dependency graph.")
                return

        mermaid_text = "graph TD\n"
        self.build_dependency_tree(package)
        
        self.log(f"Writing graph with {len(self.dependencies)} dependencies")
        for dep in sorted(self.dependencies):
            mermaid_text += f"    {dep}\n"

        with open(self.output_path, 'w') as f:
            f.write(mermaid_text)
        self.log(f"Graph saved to {self.output_path}")