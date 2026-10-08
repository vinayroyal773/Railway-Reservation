"""Network topology: the single source of truth for nodes, links and costs."""

LINKS = [
    {"a": "StationA", "b": "StationB", "cost": 4, "delay_ms": 10, "loss": 0.02},
    {"a": "StationA", "b": "StationD", "cost": 7, "delay_ms": 18, "loss": 0.03},
    {"a": "StationB", "b": "StationC", "cost": 3, "delay_ms": 8,  "loss": 0.02},
    {"a": "StationB", "b": "StationD", "cost": 2, "delay_ms": 5,  "loss": 0.01},
    {"a": "StationC", "b": "StationE", "cost": 5, "delay_ms": 12, "loss": 0.03},
    {"a": "StationC", "b": "Server",   "cost": 4, "delay_ms": 9,  "loss": 0.02},
    {"a": "StationD", "b": "StationE", "cost": 3, "delay_ms": 7,  "loss": 0.02},
    {"a": "StationE", "b": "Server",   "cost": 2, "delay_ms": 4,  "loss": 0.01},
]


def get_graph(failed_links=None):
    """Return {node: {neighbor: cost}}, leaving out any failed links."""
    failed = {frozenset(pair) for pair in (failed_links or [])}
    graph = {}
    for link in LINKS:
        a, b = link["a"], link["b"]
        graph.setdefault(a, {})
        graph.setdefault(b, {})
        if frozenset((a, b)) in failed:
            continue
        graph[a][b] = link["cost"]
        graph[b][a] = link["cost"]
    return graph


def get_nodes():
    return list(get_graph().keys())


def get_links():
    return [dict(link) for link in LINKS]


GRAPH = get_graph()
