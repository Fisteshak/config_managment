import GraphGenerator
import argparse
import os

def print_graph(file_path):
    print("\nGenerated graph:")
    print("-" * 40)
    with open(os.path.normpath(file_path), 'r') as f:
        print(f.read())
    print("-" * 40) 

def main():
    parser = argparse.ArgumentParser(description='Generate dependency graph in Mermaid format')
    parser.add_argument('--output', required=True, help='Path to output Mermaid file')
    parser.add_argument('--package', required=True, help='Package name to analyze')
    parser.add_argument('--max-depth', type=int, default=5, help='Maximum depth of dependency tree')

    args = parser.parse_args()

    generator = GraphGenerator.GraphGenerator(args.output, args.max_depth)
    success = generator.generate_mermaid(args.package)
    
    # Print graph to console only if generation was successful
    if success:
        print_graph(args.output)
    else:
        print("\nFailed to generate dependency graph.")

if __name__ == "__main__": 
    main()