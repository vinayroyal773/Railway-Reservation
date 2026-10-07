from dijkstra import dijkstra

def build_routing_table(graph, source):
    result = {}
    for destination in graph:
        cost, path = dijkstra(graph, source, destination)
        result[destination] = {
            "cost": cost,
            "next_hop": path[1] if len(path) > 1 else source,
            "path": path
        }
    return result
