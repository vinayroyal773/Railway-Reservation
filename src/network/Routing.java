package network;

import java.util.*;

public class Routing {

    // Represents a connection between two railway stations
    static class Edge {
        String destination;
        int distance;

        Edge(String destination, int distance) {
            this.destination = destination;
            this.distance = distance;
        }
    }

    // Finds the shortest route using Dijkstra's algorithm
    public static void findShortestRoute(
            Map<String, List<Edge>> network,
            String source,
            String destination) {

        Map<String, Integer> distance = new HashMap<>();
        Map<String, String> previous = new HashMap<>();

        for (String station : network.keySet()) {
            distance.put(station, Integer.MAX_VALUE);
        }

        distance.put(source, 0);

        PriorityQueue<String> queue =
                new PriorityQueue<>(Comparator.comparingInt(distance::get));

        queue.add(source);

        while (!queue.isEmpty()) {

            String current = queue.poll();

            for (Edge edge : network.get(current)) {

                int newDistance =
                        distance.get(current) + edge.distance;

                if (newDistance < distance.get(edge.destination)) {

                    distance.put(edge.destination, newDistance);
                    previous.put(edge.destination, current);

                    queue.remove(edge.destination);
                    queue.add(edge.destination);
                }
            }
        }

        // Build the route
        List<String> route = new ArrayList<>();
        String current = destination;

        while (current != null) {
            route.add(current);
            current = previous.get(current);
        }

        Collections.reverse(route);

        System.out.println("Source      : " + source);
        System.out.println("Destination : " + destination);
        System.out.println("Shortest Route: " + route);
        System.out.println(
                "Total Distance: " + distance.get(destination) + " km"
        );
    }

    public static void main(String[] args) {

        Map<String, List<Edge>> railwayNetwork = new HashMap<>();

        // Create railway stations
        railwayNetwork.put("Hyderabad", new ArrayList<>());
        railwayNetwork.put("Vijayawada", new ArrayList<>());
        railwayNetwork.put("Chennai", new ArrayList<>());
        railwayNetwork.put("Bengaluru", new ArrayList<>());
        railwayNetwork.put("Mumbai", new ArrayList<>());

        // Create railway connections
        railwayNetwork.get("Hyderabad")
                .add(new Edge("Vijayawada", 275));

        railwayNetwork.get("Vijayawada")
                .add(new Edge("Hyderabad", 275));

        railwayNetwork.get("Vijayawada")
                .add(new Edge("Chennai", 450));

        railwayNetwork.get("Chennai")
                .add(new Edge("Vijayawada", 450));

        railwayNetwork.get("Hyderabad")
                .add(new Edge("Bengaluru", 570));

        railwayNetwork.get("Bengaluru")
                .add(new Edge("Hyderabad", 570));

        railwayNetwork.get("Hyderabad")
                .add(new Edge("Mumbai", 710));

        railwayNetwork.get("Mumbai")
                .add(new Edge("Hyderabad", 710));

        // Find route
        findShortestRoute(
                railwayNetwork,
                "Hyderabad",
                "Chennai"
        );
    }
}