public class errorDetection {

    // Check passenger name
    public static boolean isValidName(String name) {
        return name != null && !name.trim().isEmpty();
    }

    // Check train number
    public static boolean isValidTrainNumber(int trainNumber) {
        return trainNumber > 0;
    }

    // Check number of seats
    public static boolean isValidSeats(int seats) {
        return seats > 0;
    }

    // Check source and destination
    public static boolean isValidRoute(String source, String destination) {
        return source != null
                && destination != null
                && !source.trim().isEmpty()
                && !destination.trim().isEmpty()
                && !source.equalsIgnoreCase(destination);
    }

    // Detect reservation errors
    public static boolean detectError(
            String name,
            int trainNumber,
            int seats,
            String source,
            String destination) {

        if (!isValidName(name)) {
            System.out.println("Error: Invalid passenger name.");
            return true;
        }

        if (!isValidTrainNumber(trainNumber)) {
            System.out.println("Error: Invalid train number.");
            return true;
        }

        if (!isValidSeats(seats)) {
            System.out.println("Error: Number of seats must be greater than 0.");
            return true;
        }

        if (!isValidRoute(source, destination)) {
            System.out.println("Error: Invalid source or destination.");
            return true;
        }

        System.out.println("No errors detected.");
        return false;
    }
}