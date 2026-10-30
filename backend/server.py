"""Zero-dependency server (Python 3.8+ standard library only; no Flask needed).

    cd backend
    python server.py          ->  http://127.0.0.1:5000   (API + website)

Same API as app.py. Use this if Flask can't be installed.
"""
import json
import mimetypes
import os
import re
import sqlite3
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

import db
from topology import GRAPH, get_graph, get_links, get_nodes
from dijkstra import dijkstra
from distance_vector import (build_routing_table, simulate_failure,
                             export_tables, rounds_to_converge)
from crc import crc_check
from sliding_window import simulate_sliding_window
from go_back_n import simulate_go_back_n
from link_failure import remove_link

FRONTEND = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))


class ApiError(Exception):
    def __init__(self, message, code=400, extra=None):
        self.message, self.code, self.extra = message, code, extra or {}


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
        raise ApiError(f"{name} must be an integer")
    if n < minimum:
        raise ApiError(f"{name} must be >= {minimum}")
    return n


# ------------------------------------------------------------------ handlers
# Each handler takes (body_dict, query_dict, *path_args) and returns (status, json)
def h_home(body, q):
    return 200, {"project": "Reliable Railway Reservation Network", "status": "Backend running"}


def h_topology(body, q):
    return 200, {"nodes": get_nodes(), "links": get_links()}


def h_route(body, q):
    source = body.get("source", "Delhi")
    destination = body.get("destination", "Server")
    bad = unknown_nodes(source, destination)
    if bad:
        raise ApiError(f"unknown node(s): {bad}")
    distance, path = dijkstra(GRAPH, source, destination)
    return 200, {"source": source, "destination": destination,
                 "distance": distance, "path": path}


def h_routing_table(body, q, node):
    if node not in GRAPH:
        raise ApiError(f"unknown node '{node}'", 404, {"nodes": get_nodes()})
    return 200, build_routing_table(GRAPH, node)


def h_distance_vector(body, q):
    poison = bool(body.get("poison_reverse", True))
    fail = body.get("fail")
    if fail:
        if not isinstance(fail, (list, tuple)) or len(fail) != 2:
            raise ApiError('"fail" must be a list of two node names')
        bad = unknown_nodes(*fail)
        if bad:
            raise ApiError(f"unknown node(s): {bad}")
        if not has_link(fail[0], fail[1]):
            raise ApiError(f"no direct link between {fail[0]} and {fail[1]}")
    graph_before = get_graph()
    graph_after = get_graph([tuple(fail)]) if fail else graph_before
    before, after, h_before, h_after = simulate_failure(
        graph_before, graph_after, poison_reverse=poison)
    if fail:
        db.record_event("LINK_FAILURE", fail[0], fail[1], "from distance-vector run")
        db.record_event("DV_CONVERGENCE", fail[0], fail[1],
                        f"re-converged in {rounds_to_converge(h_after)} rounds")
    return 200, {
        "poison_reverse": poison, "failed_link": fail,
        "initial_rounds_to_converge": rounds_to_converge(h_before),
        "recovery_rounds_to_converge": rounds_to_converge(h_after) if fail else 0,
        "history_after_failure": h_after if fail else [],
        "tables_before": export_tables(before),
        "tables_after": export_tables(after)}


def h_crc(body, q):
    message = str(body.get("message", "1011001"))
    generator = str(body.get("generator", "1101"))
    for name, value in (("message", message), ("generator", generator)):
        if not value or set(value) - {"0", "1"}:
            raise ApiError(f"{name} must be a non-empty binary string")
    if generator.strip("0") == "":
        raise ApiError("generator must contain at least one 1")
    return 200, crc_check(message, generator)


def h_sliding_window(body, q):
    packets = to_int(body.get("packets", 8), "packets")
    window = to_int(body.get("window_size", 3), "window_size")
    return 200, simulate_sliding_window(packets, window)


def h_go_back_n(body, q):
    packets = to_int(body.get("packets", 8), "packets")
    window = to_int(body.get("window_size", 3), "window_size")
    lost = to_int(body.get("lost_packet", 3), "lost_packet")
    if lost > packets:
        raise ApiError("lost_packet must be between 1 and packets")
    return 200, simulate_go_back_n(packets, window, lost)


def h_link_failure(body, q):
    a, b = body.get("from", "Bhopal"), body.get("to", "Nagpur")
    source = body.get("source", "Delhi")
    destination = body.get("destination", "Server")
    bad = unknown_nodes(a, b, source, destination)
    if bad:
        raise ApiError(f"unknown node(s): {bad}")
    if not has_link(a, b):
        raise ApiError(f"no direct link between {a} and {b}")
    graph = remove_link(GRAPH, a, b)
    distance, path = dijkstra(graph, source, destination)
    db.record_event("LINK_FAILURE", a, b, f"link {a}-{b} failed")
    db.record_event("ROUTE_CHANGE", source, destination,
                    " > ".join(path) if path else "no route available")
    return 200, {"failed_link": [a, b], "new_path": path, "distance": distance}


def h_reservations(body, q):
    return 200, db.list_reservations(status=q.get("status") or None,
                                     search=q.get("q") or None)


def h_create_reservation(body, q):
    required = ["name", "source", "destination", "date"]
    if not all(str(body.get(x, "")).strip() for x in required):
        raise ApiError("name, source, destination and date are required")
    bad = unknown_nodes(body["source"], body["destination"])
    if bad:
        raise ApiError(f"unknown station(s): {bad}")
    if body["source"] == body["destination"]:
        raise ApiError("source and destination must differ")
    try:
        datetime.strptime(str(body["date"]), "%Y-%m-%d")
    except ValueError:
        raise ApiError("date must be in YYYY-MM-DD format")
    cost, path = dijkstra(GRAPH, body["source"], body["destination"])
    if not path:
        raise ApiError("no route between these stations", 409)
    try:
        rid, pnr = db.create_reservation(body["name"], body["source"],
                                         body["destination"], body["date"], path, cost)
    except sqlite3.IntegrityError as e:
        raise ApiError(f"could not save reservation: {e}")
    return 201, {"message": "Reservation created", "id": rid, "pnr": pnr,
                 "route": path, "route_cost": cost}


def h_cancel_reservation(body, q, rid):
    result = db.cancel_reservation(int(rid))
    if result == "not_found":
        raise ApiError("reservation not found", 404)
    if result == "already_cancelled":
        raise ApiError("reservation is already cancelled", 409)
    return 200, {"message": "Reservation cancelled", "id": int(rid)}


def h_stats(body, q):
    return 200, db.stats()


def h_events(body, q):
    return 200, db.list_events()


def h_performance_list(body, q):
    runs, summary = db.list_performance()
    return 200, {"runs": runs, "summary": summary}


def h_performance_add(body, q):
    protocol = str(body.get("protocol", "")).upper()
    if protocol not in ("GO_BACK_N", "SLIDING_WINDOW", "STOP_AND_WAIT"):
        raise ApiError("protocol must be GO_BACK_N, SLIDING_WINDOW or STOP_AND_WAIT")
    sent = to_int(body.get("packets_sent"), "packets_sent", 0)
    lost = to_int(body.get("packets_lost", 0), "packets_lost", 0)
    try:
        delay = float(body.get("delay_ms"))
    except (TypeError, ValueError):
        raise ApiError("delay_ms must be a number")
    window = to_int(body["window_size"], "window_size") if body.get("window_size") is not None else None
    if lost > sent or delay < 0:
        raise ApiError("packets_lost must be <= packets_sent and delay_ms >= 0")
    rid, metrics = db.record_performance(protocol, sent, lost, delay, window, body.get("notes"))
    return 201, dict(id=rid, **metrics)


ROUTES = [
    ("GET", r"/api/topology", h_topology),
    ("POST", r"/api/route", h_route),
    ("GET", r"/api/routing-table/([^/]+)", h_routing_table),
    ("POST", r"/api/distance-vector", h_distance_vector),
    ("POST", r"/api/crc", h_crc),
    ("POST", r"/api/sliding-window", h_sliding_window),
    ("POST", r"/api/go-back-n", h_go_back_n),
    ("POST", r"/api/link-failure", h_link_failure),
    ("GET", r"/api/reservations", h_reservations),
    ("POST", r"/api/reservations", h_create_reservation),
    ("DELETE", r"/api/reservations/(\d+)", h_cancel_reservation),
    ("GET", r"/api/stats", h_stats),
    ("GET", r"/api/events", h_events),
    ("GET", r"/api/performance", h_performance_list),
    ("POST", r"/api/performance", h_performance_add),
    ("GET", r"/api/health", h_home),
]


class Handler(BaseHTTPRequestHandler):
    server_version = "RailwayServer/1.0"

    def _send(self, code, payload):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self._cors()
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _static(self, path):
        rel = "index.html" if path in ("/", "") else path.lstrip("/")
        full = os.path.abspath(os.path.join(FRONTEND, rel))
        if not full.startswith(FRONTEND + os.sep) or not os.path.isfile(full):
            return self._send(404, {"error": "not found"})
        ctype = mimetypes.guess_type(full)[0] or "application/octet-stream"
        with open(full, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype + ("; charset=utf-8" if ctype.startswith("text/") or "javascript" in ctype else ""))
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _dispatch(self):
        url = urlparse(self.path)
        if not url.path.startswith("/api/"):
            if self.command == "GET":
                return self._static(url.path)
            return self._send(405, {"error": "method not allowed"})
        body = {}
        length = int(self.headers.get("Content-Length") or 0)
        if length:
            try:
                body = json.loads(self.rfile.read(length).decode("utf-8")) or {}
                if not isinstance(body, dict):
                    body = {}
            except ValueError:
                body = {}
        query = {k: v[0] for k, v in parse_qs(url.query).items()}
        path_matched = False
        for method, pattern, fn in ROUTES:
            m = re.fullmatch(pattern, url.path)
            if not m:
                continue
            path_matched = True
            if method != self.command:
                continue
            try:
                code, payload = fn(body, query, *m.groups())
            except ApiError as e:
                return self._send(e.code, dict({"error": e.message}, **e.extra))
            except Exception as e:  # keep the server alive on unexpected errors
                return self._send(500, {"error": f"server error: {e}"})
            return self._send(code, payload)
        self._send(405 if path_matched else 404,
                   {"error": "method not allowed" if path_matched else "not found"})

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.send_header("Content-Length", "0")
        self.end_headers()

    do_GET = do_POST = do_DELETE = _dispatch

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args))


def make_server(host="127.0.0.1", port=5000):
    db.init_db()
    return ThreadingHTTPServer((host, port), Handler)


if __name__ == "__main__":
    srv = make_server()
    print("Railway server running:  http://127.0.0.1:5000   (Ctrl+C to stop)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
