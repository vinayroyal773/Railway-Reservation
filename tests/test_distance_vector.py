"""Run from the project root:  python tests/test_distance_vector.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from topology import get_graph
from dijkstra import dijkstra
from distance_vector import (run_dv, get_path, rounds_to_converge,
                             simulate_failure, INF)


def test_dv_matches_dijkstra_everywhere():
    graph = get_graph()
    tables, _ = run_dv(graph)
    for s in graph:
        for d in graph:
            cost, _path = dijkstra(graph, s, d)
            assert tables[s][d]["cost"] == cost, (s, d)


def test_path_follows_next_hops():
    tables, _ = run_dv(get_graph())
    assert get_path(tables, "StationA", "Server")[0] == "StationA"
    assert get_path(tables, "StationA", "Server")[-1] == "Server"


def test_link_failure_reroutes():
    before_g = get_graph()
    after_g = get_graph([("StationC", "Server")])
    before, after, _, _ = simulate_failure(before_g, after_g)
    path = get_path(after, "StationB", "Server")
    assert path[-1] == "Server"
    assert ("StationC", "Server") not in list(zip(path, path[1:]))
    for s in after_g:
        for d in after_g:
            cost, _ = dijkstra(after_g, s, d)
            assert after[s][d]["cost"] == cost


def test_partition_becomes_unreachable():
    g = {"A": {"B": 1}, "B": {"A": 1, "C": 1}, "C": {"B": 1}}
    after_g = {"A": {"B": 1}, "B": {"A": 1}, "C": {}}
    _, after, _, _ = simulate_failure(g, after_g)
    assert after["A"]["C"]["cost"] == INF


def test_poison_reverse_prevents_count_to_infinity():
    line = {"A": {"B": 1}, "B": {"A": 1, "C": 1}, "C": {"B": 1}}
    cut = {"A": {"B": 1}, "B": {"A": 1}, "C": {}}
    _, _, _, h_plain = simulate_failure(line, cut, poison_reverse=False)
    _, _, _, h_poison = simulate_failure(line, cut, poison_reverse=True)
    assert rounds_to_converge(h_poison) < rounds_to_converge(h_plain)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(); print("PASS", name)
