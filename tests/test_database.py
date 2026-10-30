"""Run from the project root:  python tests/test_database.py   (or pytest)"""
import os, sys, sqlite3, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import db
from topology import GRAPH
from dijkstra import dijkstra


def fresh():
    path = os.path.join(tempfile.mkdtemp(), "t.db")
    os.environ["RAILWAY_DB"] = path
    db.init_db()
    return path


def test_topology_seeded_and_idempotent():
    fresh()
    db.init_db()  # second run must not duplicate anything
    with db.connect() as c:
        assert c.execute("SELECT COUNT(*) FROM stations").fetchone()[0] == 6
        assert c.execute("SELECT COUNT(*) FROM links").fetchone()[0] == 8
        assert c.execute("SELECT is_server FROM stations WHERE name='Server'").fetchone()[0] == 1


def test_create_list_cancel():
    fresh()
    cost, path = dijkstra(GRAPH, "Delhi", "Server")
    rid, pnr = db.create_reservation(" Asha ", "Delhi", "Server", "2026-11-05", path, cost)
    rows = db.list_reservations()
    assert rows[0]["name"] == "Asha" and rows[0]["route"] == path and rows[0]["pnr"] == pnr
    assert db.cancel_reservation(rid) == "cancelled"
    assert db.cancel_reservation(rid) == "already_cancelled"
    assert db.cancel_reservation(9999) == "not_found"
    assert db.list_reservations(status="CANCELLED")[0]["cancelled_at"]


def test_constraints_reject_bad_data():
    fresh()
    for args in [("X", "Delhi", "Delhi", "2026-11-05"),   # same source/dest
                 ("X", "Nowhere", "Server", "2026-11-05"),      # unknown station (FK)
                 ("  ", "Delhi", "Server", "2026-11-05")]:   # blank name
        try:
            db.create_reservation(*args)
        except sqlite3.IntegrityError:
            continue
        raise AssertionError(f"accepted bad row {args}")


def test_search_and_stats():
    fresh()
    db.create_reservation("Asha Rao", "Delhi", "Server", "2026-11-05")
    db.create_reservation("Ravi", "Delhi", "Server", "2026-11-05")
    rid, _ = db.create_reservation("Meera", "Bhopal", "Server", "2026-11-06")
    db.cancel_reservation(rid)
    assert [r["name"] for r in db.list_reservations(search="asha")] == ["Asha Rao"]
    s = db.stats()
    assert s["confirmed"] == 2 and s["cancelled"] == 1
    assert s["top_routes"][0] == {"source": "Delhi", "destination": "Server", "bookings": 2}


def test_events_and_performance():
    fresh()
    db.record_event("LINK_FAILURE", "Nagpur", "Server", "x")
    assert db.list_events()[0]["event_type"] == "LINK_FAILURE"
    _, m = db.record_performance("GO_BACK_N", 100, 5, 1000, 8)
    assert m["packet_loss_pct"] == 5.0 and m["throughput_kbps"] == 389.12
    _, summary = db.list_performance()
    assert summary[0]["protocol"] == "GO_BACK_N" and summary[0]["runs"] == 1


def test_migrates_old_table():
    path = os.path.join(tempfile.mkdtemp(), "old.db")
    c = sqlite3.connect(path)
    c.execute("""CREATE TABLE reservations(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
        source TEXT NOT NULL, destination TEXT NOT NULL, travel_date TEXT NOT NULL, status TEXT DEFAULT 'CONFIRMED')""")
    c.execute("INSERT INTO reservations(name,source,destination,travel_date,status) VALUES('Old','Delhi','Server','2026-01-01','CANCELLED')")
    c.commit(); c.close()
    os.environ["RAILWAY_DB"] = path
    db.init_db()
    r = db.list_reservations()[0]
    assert r["name"] == "Old" and r["status"] == "CANCELLED" and len(r["pnr"]) == 10


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(); print("ok  ", name)
