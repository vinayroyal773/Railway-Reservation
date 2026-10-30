-- Railway Reservation Network: database schema (SQLite)
-- Safe to run repeatedly (IF NOT EXISTS everywhere).

CREATE TABLE IF NOT EXISTS stations (
    name        TEXT PRIMARY KEY,
    ip_address  TEXT NOT NULL UNIQUE,
    is_server   INTEGER NOT NULL DEFAULT 0 CHECK (is_server IN (0, 1))
);

-- One row per physical link. node_a < node_b is enforced so a pair is stored once.
CREATE TABLE IF NOT EXISTS links (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    node_a    TEXT NOT NULL REFERENCES stations(name),
    node_b    TEXT NOT NULL REFERENCES stations(name),
    cost      INTEGER NOT NULL CHECK (cost > 0),
    delay_ms  REAL    NOT NULL CHECK (delay_ms >= 0),
    loss_prob REAL    NOT NULL DEFAULT 0 CHECK (loss_prob >= 0 AND loss_prob <= 1),
    status    TEXT    NOT NULL DEFAULT 'UP' CHECK (status IN ('UP', 'DOWN')),
    CHECK (node_a < node_b),
    UNIQUE (node_a, node_b)
);

CREATE TABLE IF NOT EXISTS reservations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    pnr         TEXT NOT NULL UNIQUE,
    name        TEXT NOT NULL CHECK (length(trim(name)) > 0),
    source      TEXT NOT NULL REFERENCES stations(name),
    destination TEXT NOT NULL REFERENCES stations(name),
    travel_date TEXT NOT NULL,
    route_path  TEXT,                -- e.g. "Delhi > Bhopal > Server" (Dijkstra result)
    route_cost  INTEGER,
    status      TEXT NOT NULL DEFAULT 'CONFIRMED' CHECK (status IN ('CONFIRMED', 'CANCELLED')),
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    cancelled_at TEXT,
    CHECK (source <> destination)
);
CREATE INDEX IF NOT EXISTS idx_res_status_date ON reservations(status, travel_date);
CREATE INDEX IF NOT EXISTS idx_res_name        ON reservations(name COLLATE NOCASE);

-- Log of link failures, recoveries and route changes (for the report/demo).
CREATE TABLE IF NOT EXISTS network_events (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL CHECK (event_type IN
               ('LINK_FAILURE', 'LINK_RECOVERY', 'ROUTE_CHANGE', 'DV_CONVERGENCE')),
    node_a     TEXT,
    node_b     TEXT,
    detail     TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Stored results of protocol experiments (loss, delay, throughput).
CREATE TABLE IF NOT EXISTS performance_runs (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    protocol         TEXT NOT NULL CHECK (protocol IN ('GO_BACK_N', 'SLIDING_WINDOW', 'STOP_AND_WAIT')),
    window_size      INTEGER CHECK (window_size IS NULL OR window_size >= 1),
    packets_sent     INTEGER NOT NULL CHECK (packets_sent >= 0),
    packets_lost     INTEGER NOT NULL CHECK (packets_lost >= 0),
    packets_delivered INTEGER NOT NULL CHECK (packets_delivered >= 0),
    delay_ms         REAL    NOT NULL CHECK (delay_ms >= 0),
    packet_loss_pct  REAL    NOT NULL,
    throughput_kbps  REAL    NOT NULL,
    notes            TEXT,
    created_at       TEXT NOT NULL DEFAULT (datetime('now'))
);
