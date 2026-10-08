"""Real Distance Vector routing (Bellman-Ford, distributed).

Each round, every node recomputes  D_n(d) = min over neighbours v of
(cost(n, v) + D_v(d))  using the tables its neighbours had last round,
until no table changes. poison_reverse=True stops count-to-infinity.
"""

from copy import deepcopy

INF = 99  # "infinity" cap


def init_tables(graph):
    return {
        n: {d: {"cost": 0 if d == n else INF,
                "next_hop": n if d == n else None} for d in graph}
        for n in graph
    }


def _exchange_round(graph, tables, poison_reverse):
    snapshot = deepcopy(tables)
    changes = 0
    for n in graph:
        for d in graph:
            if d == n:
                continue
            best_cost, best_hop = INF, None
            for nbr, link_cost in graph[n].items():
                advertised = snapshot[nbr][d]["cost"]
                if poison_reverse and snapshot[nbr][d]["next_hop"] == n:
                    advertised = INF
                cost = min(INF, link_cost + advertised)
                if cost < best_cost:
                    best_cost, best_hop = cost, nbr
            current = tables[n][d]
            if (best_cost, best_hop) != (current["cost"], current["next_hop"]):
                tables[n][d] = {"cost": best_cost, "next_hop": best_hop}
                changes += 1
    return changes


def run_dv(graph, tables=None, poison_reverse=True, max_rounds=200):
    tables = tables if tables is not None else init_tables(graph)
    history = []
    for rnd in range(1, max_rounds + 1):
        changes = _exchange_round(graph, tables, poison_reverse)
        history.append({"round": rnd, "changes": changes})
        if changes == 0:
            break
    return tables, history


def rounds_to_converge(history):
    return sum(1 for h in history if h["changes"] > 0)


def get_path(tables, source, destination):
    path, current = [source], source
    while current != destination:
        hop = tables[current][destination]["next_hop"]
        if hop is None or hop in path:
            return []
        path.append(hop)
        current = hop
    return path


def export_tables(tables):
    out = {}
    for n, row in tables.items():
        out[n] = {}
        for d, e in row.items():
            reachable = e["cost"] < INF
            out[n][d] = {
                "cost": e["cost"] if reachable else None,
                "next_hop": e["next_hop"] if reachable else None,
                "path": get_path(tables, n, d) if reachable else [],
            }
    return out


def build_routing_table(graph, source):
    tables, history = run_dv(graph)
    table = export_tables(tables)[source]
    return {"node": source, "rounds_to_converge": rounds_to_converge(history),
            "table": table}


def simulate_failure(graph_before, graph_after, poison_reverse=True):
    before, h_before = run_dv(graph_before, poison_reverse=poison_reverse)
    after, h_after = run_dv(graph_after, tables=deepcopy(before),
                            poison_reverse=poison_reverse)
    return before, after, h_before, h_after
