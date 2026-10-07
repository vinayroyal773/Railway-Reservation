import heapq

def dijkstra(graph, start, goal):
    if start not in graph or goal not in graph:
        return None, []
    dist = {n: float("inf") for n in graph}
    prev = {n: None for n in graph}
    dist[start] = 0
    queue = [(0, start)]
    while queue:
        d, u = heapq.heappop(queue)
        if d != dist[u]:
            continue
        if u == goal:
            break
        for v, w in graph[u].items():
            nd = d + w
            if nd < dist[v]:
                dist[v], prev[v] = nd, u
                heapq.heappush(queue, (nd, v))
    if dist[goal] == float("inf"):
        return None, []
    path, cur = [], goal
    while cur:
        path.append(cur)
        cur = prev[cur]
    return dist[goal], path[::-1]
