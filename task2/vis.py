import networkx as nx
import matplotlib.pyplot as plt
import argparse

def read_mermaid_graph(file_path):
    edges = []
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith("graph TD"):
                continue
            parts = line.strip().split(" --> ")
            if len(parts) == 2:
                edges.append((parts[0].strip(), parts[1].strip()))
    return edges

def create_graph(edges):
    graph = nx.DiGraph()
    graph.add_edges_from(edges)
    return graph

def visualize_graph(graph):
    pos = nx.spring_layout(graph)
    plt.figure(figsize=(10, 8))
    nx.draw(graph, pos, with_labels=True, node_size=3000, node_color="skyblue", font_size=15, font_weight="bold", arrows=True)
    plt.title("Mermaid Graph Visualization")
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualize a Mermaid graph.")
    parser.add_argument("--path", type=str, help="Path to the Mermaid graph file")
    args = parser.parse_args()

    edges = read_mermaid_graph(args.path)
    graph = create_graph(edges)
    visualize_graph(graph)