package network;

import java.util.*;

public class Routing {

    public static class Edge {
        String destination;
        int distance;

        Edge(String destination, int distance) {
            this.destination = destination;
            this.distance = distance;
        }
    }

    public static class RouteResult {
        private final List<String> route;
        private final int distance;

        public RouteResult(List<String> route, int distance) {
            this.route = route;
            this.distance = distance;
        }

        public List<String> getRoute() {
            return route;
        }

        public int getDistance() {
            return distance;
        }
    }

    public static RouteResult findShortestRoute(
            Map<String, List<Edge>> network,
            String source,
            String destination) {

        if (!network.containsKey(source) ||
            !network.containsKey(destination)) {
            return null;
        }

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

        if (distance.get(destination) == Integer.MAX_VALUE) {
            return null;
        }

        List<String> route = new ArrayList<>();
        String current = destination;

        while (current != null) {
            route.add(current);
            current = previous.get(current);
        }

        Collections.reverse(route);

        return new RouteResult(
                route,
                distance.get(destination)
        );
    }

    public static Map<String, List<Edge>> createRailwayNetwork() {

        Map<String, List<Edge>> railwayNetwork = new HashMap<>();

        railwayNetwork.put("Hyderabad", new ArrayList<>());
        railwayNetwork.put("Vijayawada", new ArrayList<>());
        railwayNetwork.put("Chennai", new ArrayList<>());
        railwayNetwork.put("Bengaluru", new ArrayList<>());
        railwayNetwork.put("Mumbai", new ArrayList<>());

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

        return railwayNetwork;
    }

    public static void main(String[] args) {

        Map<String, List<Edge>> railwayNetwork =
                createRailwayNetwork();

        RouteResult result = findShortestRoute(
                railwayNetwork,
                "Hyderabad",
                "Chennai"
        );

        System.out.println("Source      : Hyderabad");
        System.out.println("Destination : Chennai");
        System.out.println("Shortest Route: " + result.getRoute());
        System.out.println(
                "Total Distance: " + result.getDistance() + " km"
        );
    }
}