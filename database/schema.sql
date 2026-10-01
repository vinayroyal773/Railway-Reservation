CREATE TABLE IF NOT EXISTS trains (
    train_number INTEGER PRIMARY KEY,
    train_name TEXT NOT NULL,
    source TEXT NOT NULL,
    destination TEXT NOT NULL,
    total_seats INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS reservations (
    reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    passenger_name TEXT NOT NULL,
    train_number INTEGER NOT NULL,
    source TEXT NOT NULL,
    destination TEXT NOT NULL,
    seats INTEGER NOT NULL,
    FOREIGN KEY (train_number) REFERENCES trains(train_number)
);