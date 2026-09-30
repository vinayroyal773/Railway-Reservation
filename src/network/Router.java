package network;

import java.util.*;

public class Router {

    private String name;

    public Router(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }

    // Find the shortest route using Dijkstra's algorithm
    public static void dijkstra(Map<String, List<Edge>> graph,
                                 String source,
                                 String destination) {

        Map<String, Integer> distance = new HashMap<>();
        Map<String, String> previous = new HashMap<>();

        for (String station : graph.keySet()) {
            distance.put(station, Integer.MAX_VALUE);
        }

        distance.put(source, 0);

        PriorityQueue<String> queue =
                new PriorityQueue<>(Comparator.comparingInt(distance::get));

        queue.add(source);

        while (!queue.isEmpty()) {

            String current = queue.poll();

            if (current.equals(destination)) {
                break;
            }

            for (Edge edge : graph.get(current)) {

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

        // Display shortest route
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
        System.out.println("Total Distance: "
                + distance.get(destination) + " km");
    }

    // Edge represents a railway connection
    static class Edge {

        String destination;
        int distance;

        Edge(String destination, int distance) {
            this.destination = destination;
            this.distance = distance;
        }
    }

    public static void main(String[] args) {

        Map<String, List<Edge>> railwayNetwork = new HashMap<>();

        railwayNetwork.put("A", new ArrayList<>());
        railwayNetwork.put("B", new ArrayList<>());
        railwayNetwork.put("C", new ArrayList<>());
        railwayNetwork.put("D", new ArrayList<>());
        railwayNetwork.put("E", new ArrayList<>());

        // Railway connections
        railwayNetwork.get("A").add(new Edge("B", 10));
        railwayNetwork.get("A").add(new Edge("C", 5));

        railwayNetwork.get("B").add(new Edge("A", 10));
        railwayNetwork.get("B").add(new Edge("C", 2));
        railwayNetwork.get("B").add(new Edge("D", 1));

        railwayNetwork.get("C").add(new Edge("A", 5));
        railwayNetwork.get("C").add(new Edge("B", 2));
        railwayNetwork.get("C").add(new Edge("D", 9));
        railwayNetwork.get("C").add(new Edge("E", 2));

        railwayNetwork.get("D").add(new Edge("B", 1));
        railwayNetwork.get("D").add(new Edge("C", 9));
        railwayNetwork.get("D").add(new Edge("E", 4));

        railwayNetwork.get("E").add(new Edge("C", 2));
        railwayNetwork.get("E").add(new Edge("D", 4));

        // Find route from A to E
        dijkstra(railwayNetwork, "A", "E");
    }
}