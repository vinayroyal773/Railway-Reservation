package database;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Statement;

public class Database {
private static final String URL = "jdbc:sqlite:database/railway.db";

public static Connection connect() throws SQLException {
    return DriverManager.getConnection(URL);
}

public static void initializeDatabase() {

    String trainsTable = """
            CREATE TABLE IF NOT EXISTS trains (
                train_number INTEGER PRIMARY KEY,
                train_name TEXT NOT NULL,
                source TEXT NOT NULL,
                destination TEXT NOT NULL,
                total_seats INTEGER NOT NULL
            )
            """;

    String reservationsTable = """
            CREATE TABLE IF NOT EXISTS reservations (
                reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                passenger_name TEXT NOT NULL,
                train_number INTEGER NOT NULL,
                source TEXT NOT NULL,
                destination TEXT NOT NULL,
                seats INTEGER NOT NULL,
                FOREIGN KEY (train_number)
                    REFERENCES trains(train_number)
            )
            """;

    String insertTrains = """
            INSERT OR IGNORE INTO trains
            (train_number, train_name, source, destination, total_seats)
            VALUES
            (12701, 'Hyderabad Chennai Express',
                'Hyderabad', 'Chennai', 500),

            (12702, 'Chennai Hyderabad Express',
                'Chennai', 'Hyderabad', 500),

            (12703, 'Hyderabad Vijayawada Express',
                'Hyderabad', 'Vijayawada', 400),

            (12704, 'Vijayawada Chennai Express',
                'Vijayawada', 'Chennai', 400),

            (12705, 'Hyderabad Bengaluru Express',
                'Hyderabad', 'Bengaluru', 450),

            (12706, 'Hyderabad Mumbai Express',
                'Hyderabad', 'Mumbai', 450)
            """;

    try (Connection connection = connect();
         Statement statement = connection.createStatement()) {

        // Create tables
        statement.execute(trainsTable);
        statement.execute(reservationsTable);

        // Insert initial train data
        statement.executeUpdate(insertTrains);

        System.out.println("Database initialized successfully.");

    } catch (SQLException e) {

        System.out.println("Database initialization failed.");
        e.printStackTrace();
    }
}

public static void main(String[] args) {
    initializeDatabase();
}

}
