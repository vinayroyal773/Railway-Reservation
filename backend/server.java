import java.util.Scanner;

public class server {

    public static void main(String[] args) {

        Scanner scanner = new Scanner(System.in);

        System.out.println("=================================");
        System.out.println(" Railway Reservation Server");
        System.out.println("=================================");

        System.out.print("Passenger name: ");
        String name = scanner.nextLine();

        System.out.print("Train number: ");
        int trainNumber = scanner.nextInt();

        System.out.print("Number of seats: ");
        int seats = scanner.nextInt();

        scanner.nextLine();

        System.out.print("Source: ");
        String source = scanner.nextLine();

        System.out.print("Destination: ");
        String destination = scanner.nextLine();

        // Detect errors before processing the reservation
        boolean hasError = errorDetection.detectError(
                name,
                trainNumber,
                seats,
                source,
                destination
        );

        if (hasError) {
            System.out.println("Reservation contains errors.");

            // Attempt error recovery
            name = errorRecovery.recoverName(name);
            trainNumber = errorRecovery.recoverTrainNumber(trainNumber);
            seats = errorRecovery.recoverSeats(seats);

            String[] route =
                    errorRecovery.recoverRoute(source, destination);

            source = route[0];
            destination = route[1];

            errorRecovery.showRecoveryMessage();
        }

       reservation booking = new reservation(
        name,
        trainNumber,
        seats,
        source,
        destination
);

booking.displayReservation();

        scanner.close();
    }
}