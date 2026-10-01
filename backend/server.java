
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;

import database.ReservationDAO;
import network.Routing;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class server {

    private static final int PORT = 8080;

    public static void main(String[] args) throws IOException {

        HttpServer httpServer =
                HttpServer.create(
                        new InetSocketAddress(PORT),
                        0
                );

        // ==============================
        // API ENDPOINTS
        // ==============================

        httpServer.createContext(
                "/api/reserve",
                server::handleReservation
        );

        httpServer.createContext(
                "/api/route",
                server::handleRoute
        );

        // ==============================
        // FRONTEND
        // ==============================

        httpServer.createContext(
                "/",
                server::handleFrontend
        );

        httpServer.setExecutor(null);

        System.out.println("=================================");
        System.out.println(" Railway Reservation Server");
        System.out.println("=================================");
        System.out.println(
                "Server running at http://localhost:" + PORT
        );

        httpServer.start();
    }

    // =====================================================
    // RESERVATION API
    // =====================================================

    private static void handleReservation(
            HttpExchange exchange) throws IOException {

        addCorsHeaders(exchange);

        if ("OPTIONS".equalsIgnoreCase(
                exchange.getRequestMethod())) {

            exchange.sendResponseHeaders(204, -1);
            return;
        }

        if (!"POST".equalsIgnoreCase(
                exchange.getRequestMethod())) {

            sendJson(
                    exchange,
                    405,
                    "{\"success\":false,\"message\":\"Method not allowed\"}"
            );
            return;
        }

        String body =
                new String(
                        exchange.getRequestBody().readAllBytes(),
                        StandardCharsets.UTF_8
                );

        Map<String, String> data =
                parseFormData(body);

        String name = data.get("name");
        String source = data.get("source");
        String destination = data.get("destination");

        int trainNumber;
        int seats;

        try {

            trainNumber =
                    Integer.parseInt(
                            data.get("trainNumber")
                    );

            seats =
                    Integer.parseInt(
                            data.get("seats")
                    );

        } catch (Exception e) {

            sendJson(
                    exchange,
                    400,
                    "{\"success\":false,\"message\":\"Invalid train number or seat count\"}"
            );
            return;
        }

        // ==============================
        // ERROR DETECTION
        // ==============================

        boolean hasError =
                errorDetection.detectError(
                        name,
                        trainNumber,
                        seats,
                        source,
                        destination
                );

        // ==============================
        // ERROR RECOVERY
        // ==============================

        if (hasError) {

            name =
                    errorRecovery.recoverName(name);

            trainNumber =
                    errorRecovery.recoverTrainNumber(
                            trainNumber
                    );

            seats =
                    errorRecovery.recoverSeats(seats);

            String[] recoveredRoute =
                    errorRecovery.recoverRoute(
                            source,
                            destination
                    );

            source = recoveredRoute[0];
            destination = recoveredRoute[1];
        }

        // ==============================
        // NORMALIZE STATIONS
        // ==============================

        source =
                normalizeStationName(source);

        destination =
                normalizeStationName(destination);

        // ==============================
        // CHECK TRAIN
        // ==============================

        if (!ReservationDAO.trainExists(trainNumber)) {

            sendJson(
                    exchange,
                    404,
                    "{\"success\":false,\"message\":\"Train does not exist\"}"
            );
            return;
        }

        // ==============================
        // FIND SHORTEST ROUTE
        // ==============================

        Map<String, List<Routing.Edge>> railwayNetwork =
                Routing.createRailwayNetwork();

        Routing.RouteResult routeResult =
                Routing.findShortestRoute(
                        railwayNetwork,
                        source,
                        destination
                );

        if (routeResult == null) {

            sendJson(
                    exchange,
                    400,
                    "{\"success\":false,\"message\":\"No railway route found\"}"
            );
            return;
        }

        // ==============================
        // CREATE RESERVATION
        // ==============================

        reservation booking =
                new reservation(
                        name,
                        trainNumber,
                        seats,
                        source,
                        destination
                );

        // ==============================
        // SAVE RESERVATION
        // ==============================

        boolean saved =
                ReservationDAO.saveReservation(
                        booking.getPassengerName(),
                        booking.getTrainNumber(),
                        booking.getSource(),
                        booking.getDestination(),
                        booking.getSeats()
                );

        if (!saved) {

            sendJson(
                    exchange,
                    400,
                    "{\"success\":false,\"message\":\"Reservation failed. Not enough seats available.\"}"
            );
            return;
        }

        // ==============================
        // GET REMAINING SEATS
        // ==============================

        int availableSeats =
                ReservationDAO.getAvailableSeats(
                        trainNumber
                );

        // ==============================
        // JSON RESPONSE
        // ==============================

        String json =
                "{"
                + "\"success\":true,"
                + "\"message\":\"Reservation saved successfully\","
                + "\"passenger\":\""
                + escapeJson(name)
                + "\","
                + "\"trainNumber\":"
                + trainNumber
                + ","
                + "\"seats\":"
                + seats
                + ","
                + "\"source\":\""
                + escapeJson(source)
                + "\","
                + "\"destination\":\""
                + escapeJson(destination)
                + "\","
                + "\"route\":\""
                + escapeJson(
                        routeResult.getRoute().toString()
                )
                + "\","
                + "\"distance\":"
                + routeResult.getDistance()
                + ","
                + "\"availableSeats\":"
                + availableSeats
                + "}";

        sendJson(
                exchange,
                200,
                json
        );
    }

    // =====================================================
    // ROUTE API
    // =====================================================

    private static void handleRoute(
            HttpExchange exchange) throws IOException {

        addCorsHeaders(exchange);

        if ("OPTIONS".equalsIgnoreCase(
                exchange.getRequestMethod())) {

            exchange.sendResponseHeaders(204, -1);
            return;
        }

        if (!"GET".equalsIgnoreCase(
                exchange.getRequestMethod())) {

            sendJson(
                    exchange,
                    405,
                    "{\"success\":false,\"message\":\"Method not allowed\"}"
            );
            return;
        }

        String query =
                exchange.getRequestURI()
                        .getRawQuery();

        Map<String, String> data =
                parseFormData(
                        query == null ? "" : query
                );

        String source = data.get("source");
        String destination = data.get("destination");

        if (source == null || destination == null) {

            sendJson(
                    exchange,
                    400,
                    "{\"success\":false,\"message\":\"Source and destination are required\"}"
            );
            return;
        }

        source =
                normalizeStationName(source);

        destination =
                normalizeStationName(destination);

        // Same station check

        if (source.equalsIgnoreCase(destination)) {

            sendJson(
                    exchange,
                    400,
                    "{\"success\":false,\"message\":\"Source and destination cannot be the same\"}"
            );
            return;
        }

        // ==============================
        // FIND ROUTE
        // ==============================

        Map<String, List<Routing.Edge>> network =
                Routing.createRailwayNetwork();

        Routing.RouteResult result =
                Routing.findShortestRoute(
                        network,
                        source,
                        destination
                );

        if (result == null) {

            sendJson(
                    exchange,
                    400,
                    "{\"success\":false,\"message\":\"No railway route found\"}"
            );
            return;
        }

        String json =
                "{"
                + "\"success\":true,"
                + "\"source\":\""
                + escapeJson(source)
                + "\","
                + "\"destination\":\""
                + escapeJson(destination)
                + "\","
                + "\"route\":\""
                + escapeJson(
                        result.getRoute().toString()
                )
                + "\","
                + "\"distance\":"
                + result.getDistance()
                + "}";

        sendJson(
                exchange,
                200,
                json
        );
    }

    // =====================================================
    // FRONTEND SERVER
    // =====================================================

    private static void handleFrontend(
            HttpExchange exchange) throws IOException {

        String path =
                exchange.getRequestURI()
                        .getPath();

        // Root page

        if (path.equals("/")) {
            path = "/index.html";
        }

        // Prevent directory traversal

        Path frontendRoot =
                Paths.get("frontend")
                        .toAbsolutePath()
                        .normalize();

        Path requestedFile =
                frontendRoot
                        .resolve(
                                path.substring(1)
                        )
                        .normalize();

        if (!requestedFile.startsWith(
                frontendRoot)) {

            sendJson(
                    exchange,
                    403,
                    "{\"success\":false,\"message\":\"Forbidden\"}"
            );
            return;
        }

        // File not found

        if (!Files.exists(requestedFile)
                || Files.isDirectory(requestedFile)) {

            sendJson(
                    exchange,
                    404,
                    "{\"success\":false,\"message\":\"Page not found\"}"
            );
            return;
        }

        // Read file

        byte[] content =
                Files.readAllBytes(
                        requestedFile
                );

        // Determine content type

        String contentType =
                getContentType(path);

        exchange.getResponseHeaders()
                .set(
                        "Content-Type",
                        contentType
                );

        exchange.sendResponseHeaders(
                200,
                content.length
        );

        try (OutputStream output =
                     exchange.getResponseBody()) {

            output.write(content);
        }
    }

    // =====================================================
    // CONTENT TYPE
    // =====================================================

    private static String getContentType(
            String path) {

        if (path.endsWith(".html")) {
            return "text/html; charset=UTF-8";
        }

        if (path.endsWith(".css")) {
            return "text/css; charset=UTF-8";
        }

        if (path.endsWith(".js")) {
            return "application/javascript; charset=UTF-8";
        }

        if (path.endsWith(".json")) {
            return "application/json; charset=UTF-8";
        }

        return "text/plain; charset=UTF-8";
    }

    // =====================================================
    // STATION NORMALIZATION
    // =====================================================

    private static String normalizeStationName(
            String station) {

        if (station == null) {
            return "";
        }

        station =
                station.trim();

        if (station.equalsIgnoreCase(
                "hyderabad")) {

            return "Hyderabad";
        }

        if (station.equalsIgnoreCase(
                "vijayawada")) {

            return "Vijayawada";
        }

        if (station.equalsIgnoreCase(
                "chennai")) {

            return "Chennai";
        }

        if (station.equalsIgnoreCase(
                "bengaluru")) {

            return "Bengaluru";
        }

        if (station.equalsIgnoreCase(
                "mumbai")) {

            return "Mumbai";
        }

        return station;
    }

    // =====================================================
    // FORM DATA PARSER
    // =====================================================

    private static Map<String, String> parseFormData(
            String data) {

        Map<String, String> result =
                new HashMap<>();

        if (data == null
                || data.isEmpty()) {

            return result;
        }

        String[] pairs =
                data.split("&");

        for (String pair : pairs) {

            String[] keyValue =
                    pair.split("=", 2);

            if (keyValue.length == 2) {

                String key =
                        URLDecoder.decode(
                                keyValue[0],
                                StandardCharsets.UTF_8
                        );

                String value =
                        URLDecoder.decode(
                                keyValue[1],
                                StandardCharsets.UTF_8
                        );

                result.put(
                        key,
                        value
                );
            }
        }

        return result;
    }

    // =====================================================
    // CORS
    // =====================================================

    private static void addCorsHeaders(
            HttpExchange exchange) {

        exchange.getResponseHeaders()
                .set(
                        "Access-Control-Allow-Origin",
                        "*"
                );

        exchange.getResponseHeaders()
                .set(
                        "Access-Control-Allow-Methods",
                        "GET, POST, OPTIONS"
                );

        exchange.getResponseHeaders()
                .set(
                        "Access-Control-Allow-Headers",
                        "Content-Type"
                );
    }

    // =====================================================
    // JSON RESPONSE
    // =====================================================

    private static void sendJson(
            HttpExchange exchange,
            int statusCode,
            String json) throws IOException {

        byte[] response =
                json.getBytes(
                        StandardCharsets.UTF_8
                );

        exchange.getResponseHeaders()
                .set(
                        "Content-Type",
                        "application/json; charset=UTF-8"
                );

        exchange.sendResponseHeaders(
                statusCode,
                response.length
        );

        try (OutputStream output =
                     exchange.getResponseBody()) {

            output.write(response);
        }
    }

    // =====================================================
    // JSON ESCAPING
    // =====================================================

    private static String escapeJson(
            String value) {

        if (value == null) {
            return "";
        }

        return value
                .replace(
                        "\\",
                        "\\\\"
                )
                .replace(
                        "\"",
                        "\\\""
                );
    }
}
