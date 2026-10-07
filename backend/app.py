from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from dijkstra import dijkstra
from distance_vector import build_routing_table
from crc import crc_check
from sliding_window import simulate_sliding_window
from go_back_n import simulate_go_back_n
from link_failure import remove_link

app = Flask(__name__)
CORS(app)
DB = "../database/railway.db"

GRAPH = {
    "StationA": {"StationB": 4, "StationD": 7},
    "StationB": {"StationA": 4, "StationC": 3, "StationD": 2},
    "StationC": {"StationB": 3, "StationE": 5, "Server": 4},
    "StationD": {"StationA": 7, "StationB": 2, "StationE": 3},
    "StationE": {"StationD": 3, "StationC": 5, "Server": 2},
    "Server": {"StationC": 4, "StationE": 2}
}

@app.get("/")
def home():
    return jsonify({"project": "Reliable Railway Reservation Network", "status": "Backend running"})

@app.post("/api/route")
def route():
    data = request.get_json() or {}
    source = data.get("source", "StationA")
    destination = data.get("destination", "Server")
    distance, path = dijkstra(GRAPH, source, destination)
    return jsonify({"source": source, "destination": destination, "distance": distance, "path": path})

@app.get("/api/routing-table/<node>")
def routing_table(node):
    return jsonify(build_routing_table(GRAPH, node))

@app.post("/api/crc")
def crc():
    data = request.get_json() or {}
    return jsonify(crc_check(data.get("message", "1011001"), data.get("generator", "1101")))

@app.post("/api/sliding-window")
def sliding_window():
    data = request.get_json() or {}
    return jsonify(simulate_sliding_window(int(data.get("packets", 8)), int(data.get("window_size", 3))))

@app.post("/api/go-back-n")
def go_back_n():
    data = request.get_json() or {}
    return jsonify(simulate_go_back_n(
        int(data.get("packets", 8)),
        int(data.get("window_size", 3)),
        int(data.get("lost_packet", 3))
    ))

@app.post("/api/link-failure")
def link_failure():
    data = request.get_json() or {}
    a, b = data.get("from", "StationB"), data.get("to", "StationC")
    graph = remove_link(GRAPH, a, b)
    distance, path = dijkstra(graph, data.get("source", "StationA"), data.get("destination", "Server"))
    return jsonify({"failed_link": [a, b], "new_path": path, "distance": distance})

@app.get("/api/reservations")
def reservations():
    conn = sqlite3.connect(DB)
    rows = conn.execute("SELECT * FROM reservations ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([{"id":r[0],"name":r[1],"source":r[2],"destination":r[3],"date":r[4],"status":r[5]} for r in rows])

@app.post("/api/reservations")
def create_reservation():
    data = request.get_json() or {}
    required = ["name", "source", "destination", "date"]
    if not all(data.get(x) for x in required):
        return jsonify({"error": "name, source, destination and date are required"}), 400
    conn = sqlite3.connect(DB)
    cur = conn.execute(
        "INSERT INTO reservations(name,source,destination,travel_date,status) VALUES(?,?,?,?,?)",
        (data["name"], data["source"], data["destination"], data["date"], "CONFIRMED")
    )
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return jsonify({"message":"Reservation created","id":rid}), 201

if __name__ == "__main__":
    app.run(debug=True)
