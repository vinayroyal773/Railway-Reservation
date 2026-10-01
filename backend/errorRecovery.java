public class errorRecovery {

    public static String recoverName(String name) {
        if (name == null || name.trim().isEmpty()) {
            System.out.println("Recovery: Passenger name is missing.");
            return "Unknown Passenger";
        }
        return name.trim();
    }

    public static int recoverTrainNumber(int trainNumber) {
        if (trainNumber <= 0) {
            System.out.println("Recovery: Invalid train number.");
            return 0;
        }
        return trainNumber;
    }

    public static int recoverSeats(int seats) {
        if (seats <= 0) {
            System.out.println("Recovery: Invalid seat count.");
            return 1;
        }
        return seats;
    }

    public static String[] recoverRoute(String source, String destination) {

        if (source == null || source.trim().isEmpty()) {
            source = "Unknown";
        }

        if (destination == null || destination.trim().isEmpty()) {
            destination = "Unknown";
        }

        if (source.equalsIgnoreCase(destination)) {
            System.out.println(
                "Recovery: Source and destination cannot be the same."
            );
            destination = "Unknown";
        }

        return new String[] {
            source.trim(),
            destination.trim()
        };
    }

    public static void showRecoveryMessage() {
        System.out.println("Error recovery completed.");
    }
}