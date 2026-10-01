
import java.util.Scanner;
import java.util.List;
import java.util.Map;

import database.ReservationDAO;
import network.Routing;

public class server {
    private static String normalizeStationName(String station) {

    if (station.equalsIgnoreCase("hyderabad")) {
        return "Hyderabad";
    }

    if (station.equalsIgnoreCase("vijayawada")) {
        return "Vijayawada";
    }

    if (station.equalsIgnoreCase("chennai")) {
        return "Chennai";
    }

    if (station.equalsIgnoreCase("bengaluru")) {
        return "Bengaluru";
    }

    if (station.equalsIgnoreCase("mumbai")) {
        return "Mumbai";
    }

    return station;
}

    public static void main(String[] args) {

        Scanner scanner = new Scanner(System.in);

        System.out.println("=================================");
        System.out.println(" Railway Reservation Server");
        System.out.println("=================================");

        // -----------------------------------------
        // 1. GET PASSENGER DETAILS
        // -----------------------------------------

        System.out.print("Passenger name: ");
        String name = scanner.nextLine();

        System.out.print("Train number: ");
        int trainNumber = scanner.nextInt();

        System.out.print("Number of seats: ");
        int seats = scanner.nextInt();

        scanner.nextLine();

       System.out.print("Source: ");
       String source = scanner.nextLine().trim();

       System.out.print("Destination: ");
       String destination = scanner.nextLine().trim();
       source = normalizeStationName(source);
       destination = normalizeStationName(destination);
        // -----------------------------------------
        // 2. ERROR DETECTION
        // -----------------------------------------

        boolean hasError = errorDetection.detectError(
                name,
                trainNumber,
                seats,
                source,
                destination
        );

        // -----------------------------------------
        // 3. ERROR RECOVERY
        // -----------------------------------------

        if (hasError) {

            System.out.println(
                    "Reservation contains errors."
            );

            name = errorRecovery.recoverName(name);

            trainNumber =
                    errorRecovery.recoverTrainNumber(
                            trainNumber
                    );

            seats =
                    errorRecovery.recoverSeats(seats);

            String[] route =
                    errorRecovery.recoverRoute(
                            source,
                            destination
                    );

            source = route[0];
            destination = route[1];

            errorRecovery.showRecoveryMessage();
        }

        // -----------------------------------------
        // 4. RAILWAY ROUTING
        // -----------------------------------------

        Map<String, List<Routing.Edge>> railwayNetwork =
                Routing.createRailwayNetwork();

        Routing.RouteResult routeResult =
                Routing.findShortestRoute(
                        railwayNetwork,
                        source,
                        destination
                );

        // Check whether a route exists
        if (routeResult == null) {

            System.out.println(
                    "Error: No railway route found between "
                    + source
                    + " and "
                    + destination
            );

            scanner.close();
            return;
        }

        // Display route information
        System.out.println("\n--- Route Information ---");

        System.out.println(
                "Shortest Route: "
                + routeResult.getRoute()
        );

        System.out.println(
                "Total Distance: "
                + routeResult.getDistance()
                + " km"
        );

        // -----------------------------------------
        // 5. CHECK TRAIN EXISTS
        // -----------------------------------------

        if (!ReservationDAO.trainExists(trainNumber)) {

            System.out.println(
                    "Error: Train does not exist."
            );

            scanner.close();
            return;
        }

        // -----------------------------------------
        // 6. CREATE RESERVATION OBJECT
        // -----------------------------------------

        reservation booking =
                new reservation(
                        name,
                        trainNumber,
                        seats,
                        source,
                        destination
                );

        // -----------------------------------------
        // 7. SAVE RESERVATION TO DATABASE
        // -----------------------------------------

        boolean saved =
                ReservationDAO.saveReservation(
                        booking.getPassengerName(),
                        booking.getTrainNumber(),
                        booking.getSource(),
                        booking.getDestination(),
                        booking.getSeats()
                );

        // -----------------------------------------
        // 8. DISPLAY RESERVATION RESULT
        // -----------------------------------------

        if (saved) {

            System.out.println(
                    "\nReservation saved successfully."
            );

            booking.displayReservation();

            System.out.println(
                    "Available seats: "
                    + ReservationDAO.getAvailableSeats(
                            trainNumber
                    )
            );

        } else {

            System.out.println(
                    "Reservation failed. "
                    + "Not enough seats available."
            );
        }

        scanner.close();
    }
}

