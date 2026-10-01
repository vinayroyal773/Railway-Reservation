package database;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class ReservationDAO {

    public static boolean trainExists(int trainNumber) {

        String sql = """
                SELECT train_number
                FROM trains
                WHERE train_number = ?
                """;

        try (Connection connection = Database.connect();
             PreparedStatement statement = connection.prepareStatement(sql)) {

            statement.setInt(1, trainNumber);

            try (ResultSet result = statement.executeQuery()) {
                return result.next();
            }

        } catch (SQLException e) {
            System.out.println("Error checking train.");
            e.printStackTrace();
            return false;
        }
    }

    public static int getAvailableSeats(int trainNumber) {

        String sql = """
                SELECT total_seats
                FROM trains
                WHERE train_number = ?
                """;

        try (Connection connection = Database.connect();
             PreparedStatement statement = connection.prepareStatement(sql)) {

            statement.setInt(1, trainNumber);

            try (ResultSet result = statement.executeQuery()) {

                if (result.next()) {
                    return result.getInt("total_seats");
                }

                return 0;
            }

        } catch (SQLException e) {
            System.out.println("Error checking seat availability.");
            e.printStackTrace();
            return 0;
        }
    }

    public static boolean saveReservation(
            String passengerName,
            int trainNumber,
            String source,
            String destination,
            int seats) {

        String insertReservation = """
                INSERT INTO reservations
                (passenger_name, train_number, source, destination, seats)
                VALUES (?, ?, ?, ?, ?)
                """;

        String updateSeats = """
                UPDATE trains
                SET total_seats = total_seats - ?
                WHERE train_number = ?
                AND total_seats >= ?
                """;

        try (Connection connection = Database.connect()) {

            connection.setAutoCommit(false);

            try (PreparedStatement update =
                         connection.prepareStatement(updateSeats);
                 PreparedStatement insert =
                         connection.prepareStatement(insertReservation)) {

                update.setInt(1, seats);
                update.setInt(2, trainNumber);
                update.setInt(3, seats);

                int updatedRows = update.executeUpdate();

                if (updatedRows == 0) {
                    connection.rollback();
                    return false;
                }

                insert.setString(1, passengerName);
                insert.setInt(2, trainNumber);
                insert.setString(3, source);
                insert.setString(4, destination);
                insert.setInt(5, seats);

                insert.executeUpdate();

                connection.commit();
                return true;

            } catch (SQLException e) {
                connection.rollback();
                throw e;
            }

        } catch (SQLException e) {
            System.out.println("Error saving reservation.");
            e.printStackTrace();
            return false;
        }
    }
}