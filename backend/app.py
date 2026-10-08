import os
import sqlite3
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS

from topology import GRAPH, get_graph, get_links, get_nodes
from dijkstra import dijkstra
from distance_vector import (build_routing_table, simulate_failure,
                             export_tables, rounds_to_converge)
from crc import crc_check
from sliding_window import simulate_sliding_window
from go_back_n import simulate_go_back_n
from link_failure import remove_link

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "..", "database", "railway.db")


# ---------------------------------------------------------------- helpers
def get_db():
    return sqlite3.connect(DB)


def init_db():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS reservations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        source TEXT NOT NULL,
        destination TEXT NOT NULL,
        travel_date TEXT NOT NULL,
        status TEXT DEFAULT 'CONFIRMED')''')
    conn.commit()
    conn.close()


def error(message, code=400):
    return jsonify({"error": message}), code


def unknown_nodes(*nodes):
    valid = set(get_nodes())
    return [n for n in nodes if n not in valid]


def has_link(a, b):
    try:
        return b in GRAPH[a]
    except (KeyError, TypeError):
        return False


def to_int(value, name, minimum=1):
    try:
        n = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be an integer")
    if n < minimum:
        raise ValueError(f"{name} must be >= {minimum}")
    return n


# ----------------------------------------------------------------- routes
@app.get("/")
def home():
    return jsonify({"project": "Reliable Railway Reservation Network",
                    "status": "Backend running"})


@app.get("/api/topology")
def topology():
    return jsonify({"nodes": get_nodes(), "links": get_links()})


@app.post("/api/route")
def route():
    data = request.get_json(silent=True) or {}
    source = data.get("source", "StationA")
    destination = data.get("destination", "Server")
    bad = unknown_nodes(source, destination)
    if bad:
        return error(f"unknown node(s): {bad}")
    distance, path = dijkstra(GRAPH, source, destination)
    return jsonify({"source": source, "destination": destination,
                    "distance": distance, "path": path})


@app.get("/api/routing-table/<node>")
def routing_table(node):
    if node not in GRAPH:
        return jsonify({"error": f"unknown node '{node}'",
                        "nodes": get_nodes()}), 404
    return jsonify(build_routing_table(GRAPH, node))


@app.post("/api/distance-vector")
def distance_vector():
    data = request.get_json(silent=True) or {}
    poison = bool(data.get("poison_reverse", True))
    fail = data.get("fail")

    if fail:
        if not isinstance(fail, (list, tuple)) or len(fail) != 2:
            return error('"fail" must be a list of two node names')
        bad = unknown_nodes(*fail)
        if bad:
            return error(f"unknown node(s): {bad}")
        if not has_link(fail[0], fail[1]):
            return error(f"no direct link between {fail[0]} and {fail[1]}")

    graph_before = get_graph()
    graph_after = get_graph([tuple(fail)]) if fail else graph_before
    before, after, h_before, h_after = simulate_failure(
        graph_before, graph_after, poison_reverse=poison)
    return jsonify({
        "poison_reverse": poison,
        "failed_link": fail,
        "initial_rounds_to_converge": rounds_to_converge(h_before),
        "recovery_rounds_to_converge": rounds_to_converge(h_after) if fail else 0,
        "history_after_failure": h_after if fail else [],
        "tables_before": export_tables(before),
        "tables_after": export_tables(after),
    })


@app.post("/api/crc")
def crc():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "1011001"))
    generator = str(data.get("generator", "1101"))
    for name, value in (("message", message), ("generator", generator)):
        if not value or set(value) - {"0", "1"}:
            return error(f"{name} must be a non-empty binary string")
    if generator.strip("0") == "":
        return error("generator must contain at least one 1")
    return jsonify(crc_check(message, generator))


@app.post("/api/sliding-window")
def sliding_window():
    data = request.get_json(silent=True) or {}
    try:
        packets = to_int(data.get("packets", 8), "packets")
        window = to_int(data.get("window_size", 3), "window_size")
    except ValueError as e:
        return error(str(e))
    return jsonify(simulate_sliding_window(packets, window))


@app.post("/api/go-back-n")
def go_back_n():
    data = request.get_json(silent=True) or {}
    try:
        packets = to_int(data.get("packets", 8), "packets")
        window = to_int(data.get("window_size", 3), "window_size")
        lost = to_int(data.get("lost_packet", 3), "lost_packet")
    except ValueError as e:
        return error(str(e))
    if lost > packets:
        return error("lost_packet must be between 1 and packets")
    return jsonify(simulate_go_back_n(packets, window, lost))


@app.post("/api/link-failure")
def link_failure():
    data = request.get_json(silent=True) or {}
    a, b = data.get("from", "StationB"), data.get("to", "StationC")
    source = data.get("source", "StationA")
    destination = data.get("destination", "Server")
    bad = unknown_nodes(a, b, source, destination)
    if bad:
        return error(f"unknown node(s): {bad}")
    if not has_link(a, b):
        return error(f"no direct link between {a} and {b}")
    graph = remove_link(GRAPH, a, b)
    distance, path = dijkstra(graph, source, destination)
    return jsonify({"failed_link": [a, b], "new_path": path,
                    "distance": distance})


@app.get("/api/reservations")
def reservations():
    conn = get_db()
    rows = conn.execute(
        "SELECT id, name, source, destination, travel_date, status "
        "FROM reservations ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([{"id": r[0], "name": r[1], "source": r[2],
                     "destination": r[3], "date": r[4], "status": r[5]}
                    for r in rows])


@app.post("/api/reservations")
def create_reservation():
    data = request.get_json(silent=True) or {}
    required = ["name", "source", "destination", "date"]
    if not all(data.get(x) for x in required):
        return error("name, source, destination and date are required")
    bad = unknown_nodes(data["source"], data["destination"])
    if bad:
        return error(f"unknown station(s): {bad}")
    if data["source"] == data["destination"]:
        return error("source and destination must differ")
    try:
        datetime.strptime(str(data["date"]), "%Y-%m-%d")
    except ValueError:
        return error("date must be in YYYY-MM-DD format")

    conn = get_db()
    cur = conn.execute(
        "INSERT INTO reservations(name,source,destination,travel_date,status) "
        "VALUES(?,?,?,?,?)",
        (data["name"], data["source"], data["destination"],
         data["date"], "CONFIRMED"))
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return jsonify({"message": "Reservation created", "id": rid}), 201


@app.delete("/api/reservations/<int:rid>")
def cancel_reservation(rid):
    conn = get_db()
    cur = conn.execute(
        "UPDATE reservations SET status='CANCELLED' WHERE id=?", (rid,))
    conn.commit()
    changed = cur.rowcount
    conn.close()
    if not changed:
        return error("reservation not found", 404)
    return jsonify({"message": "Reservation cancelled", "id": rid})


init_db()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)