"""Create or upgrade the database.   python database/init_db.py [--reset] [--demo]

--reset  delete railway.db first      --demo  add sample reservations/events/runs
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "backend"))
import db  # noqa: E402


def demo():
    from topology import GRAPH
    from dijkstra import dijkstra
    rows = [("Asha Rao", "Delhi", "Server", "2026-11-05"),
            ("Vinay Kumar", "Bhopal", "Server", "2026-11-05"),
            ("Meera Nair", "Mumbai", "Server", "2026-11-06"),
            ("Ravi Teja", "Delhi", "Hyderabad", "2026-11-06"),
            ("Sana Khan", "Nagpur", "Delhi", "2026-11-07"),
            ("Kiran Das", "Delhi", "Server", "2026-11-07")]
    ids = []
    for name, s, d, date in rows:
        cost, path = dijkstra(GRAPH, s, d)
        ids.append(db.create_reservation(name, s, d, date, path, cost)[0])
    db.cancel_reservation(ids[2])
    db.record_event("LINK_FAILURE", "Nagpur", "Server", "demo: Server reachable via Hyderabad")
    db.record_event("ROUTE_CHANGE", "Delhi", "Server", "Delhi > Bhopal > Mumbai > Hyderabad > Server")
    for proto, w, sent, lost, ms in [("GO_BACK_N", 4, 100, 5, 900), ("GO_BACK_N", 8, 100, 12, 1100),
                                     ("SLIDING_WINDOW", 4, 100, 5, 700), ("STOP_AND_WAIT", 1, 100, 5, 2600)]:
        db.record_performance(proto, sent, lost, ms, w, "demo run")


if __name__ == "__main__":
    if "--reset" in sys.argv and os.path.exists(db.DB_PATH):
        os.remove(db.DB_PATH)
    db.init_db()
    if "--demo" in sys.argv:
        demo()
    print("Database ready:", os.path.abspath(db.DB_PATH))
