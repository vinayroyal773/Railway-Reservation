public class reservation {

    private String passengerName;
    private int trainNumber;
    private int seats;
    private String source;
    private String destination;

    public reservation(String passengerName, int trainNumber, int seats,
                       String source, String destination) {

        this.passengerName = passengerName;
        this.trainNumber = trainNumber;
        this.seats = seats;
        this.source = source;
        this.destination = destination;
    }

    public void displayReservation() {
        System.out.println("\n--- Reservation Details ---");
        System.out.println("Passenger: " + passengerName);
        System.out.println("Train: " + trainNumber);
        System.out.println("Seats: " + seats);
        System.out.println("Route: " + source + " -> " + destination);
    }

    public String getPassengerName() {
        return passengerName;
    }

    public int getTrainNumber() {
        return trainNumber;
    }

    public int getSeats() {
        return seats;
    }

    public String getSource() {
        return source;
    }

    public String getDestination() {
        return destination;
    }
}