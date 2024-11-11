import GraphGenerator
import argparse

def main():
    parser = argparse.ArgumentParser(description='Generate dependency graph in Mermaid format')
    parser.add_argument('--output', required=True, help='Path to output Mermaid file')
    parser.add_argument('--package', required=True, help='Package name to analyze')
    parser.add_argument('--max-depth', type=int, default=5, help='Maximum depth of dependency tree')

    args = parser.parse_args()

    generator = GraphGenerator(args.output, args.max_depth)
    generator.generate_mermaid(args.package)

if __name__ == "__main__":
    main()