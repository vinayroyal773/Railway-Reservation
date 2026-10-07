def remove_link(graph, node_a, node_b):
    new_graph = {n: neighbors.copy() for n, neighbors in graph.items()}
    new_graph.get(node_a, {}).pop(node_b, None)
    new_graph.get(node_b, {}).pop(node_a, None)
    return new_graph
