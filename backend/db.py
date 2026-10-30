"""Database layer for the railway reservation project (SQLite).

All SQL lives here so app.py stays about HTTP and networking.
Set RAILWAY_DB to point at a different file (used by the tests).
"""
import os
import secrets
import sqlite3
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get(
    "RAILWAY_DB", os.path.join(BASE_DIR, "..", "database", "railway.db"))
SCHEMA_PATH = os.path.join(BASE_DIR, "..", "database", "schema.sql")
PAYLOAD_BYTES = 512  # frame payload size used to turn packets into kbps


def _path():
    return os.environ.get("RAILWAY_DB", DB_PATH)


@contextmanager
def connect():
    """Connection with foreign keys on and dict-like rows; commits or rolls back."""
    conn = sqlite3.connect(_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ------------------------------------------------------------ setup / migrate
def _columns(conn, table):
    return [r["name"] for r in conn.execute(f"PRAGMA table_info({table})")]


def station_ip(name, nodes):
    """Server gets 10.0.0.1; the other stations get 10.0.<n>.1 in order."""
    if name == "Server":
        return "10.0.0.1"
    others = [n for n in nodes if n != "Server"]
    return f"10.0.{others.index(name) + 1}.1"


def seed_topology(conn):
    """Copy stations and links from topology.py into the database (idempotent).
    A link's UP/DOWN status is never overwritten by re-seeding."""
    from topology import get_nodes, get_links
    nodes = sorted(get_nodes())
    for n in nodes:
        conn.execute(
            "INSERT OR IGNORE INTO stations(name, ip_address, is_server) VALUES(?,?,?)",
            (n, station_ip(n, nodes), 1 if n == "Server" else 0))
    for l in get_links():
        a, b = sorted((l["a"], l["b"]))
        vals = (l["cost"], l["delay_ms"], l["loss"])
        # UPDATE then INSERT OR IGNORE works on old SQLite versions (no upsert needed)
        conn.execute("UPDATE links SET cost=?, delay_ms=?, loss_prob=? "
                     "WHERE node_a=? AND node_b=?", vals + (a, b))
        conn.execute("INSERT OR IGNORE INTO links(node_a,node_b,cost,delay_ms,loss_prob) "
                     "VALUES(?,?,?,?,?)", (a, b) + vals)


def init_db():
    """Create/upgrade the schema, migrating the old 6-column reservations table."""
    os.makedirs(os.path.dirname(os.path.abspath(_path())), exist_ok=True)
    with connect() as conn:
        old_rows = None
        cols = _columns(conn, "reservations")
        if cols and "pnr" not in cols:               # old starter-project table
            old_rows = conn.execute(
                "SELECT name, source, destination, travel_date, status "
                "FROM reservations ORDER BY id").fetchall()
            conn.execute("DROP TABLE reservations")
        with open(SCHEMA_PATH, encoding="utf-8") as f:
            conn.executescript(f.read())
        seed_topology(conn)
        for r in old_rows or []:
            conn.execute(
                "INSERT INTO reservations(pnr,name,source,destination,travel_date,status) "
                "VALUES(?,?,?,?,?,?)",
                (_new_pnr(conn), r["name"], r["source"], r["destination"],
                 r["travel_date"], r["status"] or "CONFIRMED"))


# --------------------------------------------------------------- reservations
def _new_pnr(conn):
    while True:
        pnr = secrets.token_hex(5).upper()           # 10 hex characters
        if not conn.execute("SELECT 1 FROM reservations WHERE pnr=?", (pnr,)).fetchone():
            return pnr


def _res_dict(r):
    return {"id": r["id"], "pnr": r["pnr"], "name": r["name"],
            "source": r["source"], "destination": r["destination"],
            "date": r["travel_date"], "status": r["status"],
            "route": r["route_path"].split(" > ") if r["route_path"] else [],
            "route_cost": r["route_cost"], "created_at": r["created_at"],
            "cancelled_at": r["cancelled_at"]}


def create_reservation(name, source, destination, date, path=None, cost=None):
    """Insert a CONFIRMED reservation. Raises sqlite3.IntegrityError on bad data."""
    with connect() as conn:
        pnr = _new_pnr(conn)
        cur = conn.execute(
            """INSERT INTO reservations
               (pnr,name,source,destination,travel_date,route_path,route_cost)
               VALUES(?,?,?,?,?,?,?)""",
            (pnr, name.strip(), source, destination, date,
             " > ".join(path) if path else None, cost))
        return cur.lastrowid, pnr


def list_reservations(status=None, search=None, limit=500):
    sql, args = "SELECT * FROM reservations WHERE 1=1", []
    if status:
        sql += " AND status=?"; args.append(status)
    if search:
        sql += " AND (name LIKE ? OR pnr LIKE ? OR source LIKE ? OR destination LIKE ?)"
        args += [f"%{search}%"] * 4
    sql += " ORDER BY id DESC LIMIT ?"; args.append(limit)
    with connect() as conn:
        return [_res_dict(r) for r in conn.execute(sql, args)]


def cancel_reservation(rid):
    """Returns 'cancelled', 'already_cancelled' or 'not_found'."""
    with connect() as conn:
        row = conn.execute("SELECT status FROM reservations WHERE id=?", (rid,)).fetchone()
        if not row:
            return "not_found"
        if row["status"] == "CANCELLED":
            return "already_cancelled"
        conn.execute("UPDATE reservations SET status='CANCELLED', "
                     "cancelled_at=datetime('now') WHERE id=?", (rid,))
        return "cancelled"


# ------------------------------------------------------------ network events
def record_event(event_type, node_a=None, node_b=None, detail=None):
    with connect() as conn:
        conn.execute("INSERT INTO network_events(event_type,node_a,node_b,detail) "
                     "VALUES(?,?,?,?)", (event_type, node_a, node_b, detail))


def list_events(limit=100):
    with connect() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM network_events ORDER BY id DESC LIMIT ?", (limit,))]


# ----------------------------------------------------------- performance runs
def record_performance(protocol, packets_sent, packets_lost, delay_ms,
                       window_size=None, notes=None):
    """Store one experiment and derive loss % and throughput (kbps)."""
    delivered = packets_sent - packets_lost
    loss_pct = round(packets_lost / packets_sent * 100, 2) if packets_sent else 0.0
    kbps = round(delivered * PAYLOAD_BYTES * 8 / delay_ms, 2) if delay_ms else 0.0
    with connect() as conn:
        cur = conn.execute(
            """INSERT INTO performance_runs
               (protocol,window_size,packets_sent,packets_lost,packets_delivered,
                delay_ms,packet_loss_pct,throughput_kbps,notes)
               VALUES(?,?,?,?,?,?,?,?,?)""",
            (protocol, window_size, packets_sent, packets_lost, delivered,
             delay_ms, loss_pct, kbps, notes))
        return cur.lastrowid, {"packet_loss_pct": loss_pct, "throughput_kbps": kbps}


def list_performance(limit=100):
    with connect() as conn:
        runs = [dict(r) for r in conn.execute(
            "SELECT * FROM performance_runs ORDER BY id DESC LIMIT ?", (limit,))]
        summary = [dict(r) for r in conn.execute(
            """SELECT protocol, COUNT(*) AS runs,
                      ROUND(AVG(packet_loss_pct),2) AS avg_loss_pct,
                      ROUND(AVG(delay_ms),2) AS avg_delay_ms,
                      ROUND(AVG(throughput_kbps),2) AS avg_throughput_kbps
               FROM performance_runs GROUP BY protocol""")]
    return runs, summary


# ------------------------------------------------------------------ dashboard
def stats():
    with connect() as conn:
        by_status = {r["status"]: r["n"] for r in conn.execute(
            "SELECT status, COUNT(*) AS n FROM reservations GROUP BY status")}
        top_routes = [dict(r) for r in conn.execute(
            """SELECT source, destination, COUNT(*) AS bookings FROM reservations
               WHERE status='CONFIRMED' GROUP BY source, destination
               ORDER BY bookings DESC, source LIMIT 5""")]
        per_day = [dict(r) for r in conn.execute(
            """SELECT travel_date AS date, COUNT(*) AS bookings FROM reservations
               WHERE status='CONFIRMED' GROUP BY travel_date ORDER BY travel_date LIMIT 30""")]
        events = conn.execute("SELECT COUNT(*) AS n FROM network_events").fetchone()["n"]
        links_down = conn.execute(
            "SELECT COUNT(*) AS n FROM links WHERE status='DOWN'").fetchone()["n"]
    return {"confirmed": by_status.get("CONFIRMED", 0),
            "cancelled": by_status.get("CANCELLED", 0),
            "top_routes": top_routes, "bookings_per_day": per_day,
            "network_events": events, "links_down": links_down}
