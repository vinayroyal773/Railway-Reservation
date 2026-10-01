
const API_URL = "http://localhost:8080";


// -----------------------------------------
// ROUTE SEARCH
// -----------------------------------------

const searchRouteButton =
    document.getElementById("searchRoute");

const routeSource =
    document.getElementById("routeSource");

const routeDestination =
    document.getElementById("routeDestination");

const routeResult =
    document.getElementById("routeResult");


searchRouteButton.addEventListener(
    "click",
    async function () {

        const source = routeSource.value;
        const destination = routeDestination.value;

        if (source === "" || destination === "") {

            routeResult.innerHTML =
                "<p>Please select both source and destination.</p>";

            return;
        }

        if (source === destination) {

            routeResult.innerHTML =
                "<p>Source and destination cannot be the same.</p>";

            return;
        }

        routeResult.innerHTML =
            "<p>Searching for the shortest route...</p>";

        try {

            const response =
                await fetch(
                    `${API_URL}/api/route?source=${encodeURIComponent(source)}&destination=${encodeURIComponent(destination)}`
                );

            const data =
                await response.json();

            if (!data.success) {

                routeResult.innerHTML =
                    `<p class="error">${data.message}</p>`;

                return;
            }

            routeResult.innerHTML = `
                <h3>Shortest Route</h3>

                <p>
                    <strong>Source:</strong>
                    ${data.source}
                </p>

                <p>
                    <strong>Destination:</strong>
                    ${data.destination}
                </p>

                <p>
                    <strong>Route:</strong>
                    ${data.route}
                </p>

                <p>
                    <strong>Total Distance:</strong>
                    ${data.distance} km
                </p>
            `;

        } catch (error) {

            routeResult.innerHTML =
                `<p class="error">
                    Unable to connect to the Java server.
                    Make sure the backend server is running.
                </p>`;

            console.error(error);
        }
    }
);


// -----------------------------------------
// RESERVATION
// -----------------------------------------

const reservationButton =
    document.getElementById("makeReservation");

const reservationResult =
    document.getElementById("reservationResult");


reservationButton.addEventListener(
    "click",
    async function () {

        const name =
            document.getElementById(
                "passengerName"
            ).value;

        const trainNumber =
            document.getElementById(
                "trainNumber"
            ).value;

        const seats =
            document.getElementById(
                "seatCount"
            ).value;

        const source =
            document.getElementById(
                "reservationSource"
            ).value;

        const destination =
            document.getElementById(
                "reservationDestination"
            ).value;


        // Basic frontend validation

        if (
            name === "" ||
            trainNumber === "" ||
            seats === "" ||
            source === "" ||
            destination === ""
        ) {

            reservationResult.innerHTML =
                "<p class='error'>Please fill in all fields.</p>";

            return;
        }


        if (source === destination) {

            reservationResult.innerHTML =
                "<p class='error'>Source and destination cannot be the same.</p>";

            return;
        }


        reservationResult.innerHTML =
            "<p>Processing reservation...</p>";


        try {

            const formData =
                new URLSearchParams();

            formData.append(
                "name",
                name
            );

            formData.append(
                "trainNumber",
                trainNumber
            );

            formData.append(
                "seats",
                seats
            );

            formData.append(
                "source",
                source
            );

            formData.append(
                "destination",
                destination
            );


            const response =
                await fetch(
                    `${API_URL}/api/reserve`,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/x-www-form-urlencoded"
                        },

                        body: formData
                    }
                );


            const data =
                await response.json();


            if (!data.success) {

                reservationResult.innerHTML =
                    `<p class="error">
                        ${data.message}
                    </p>`;

                return;
            }


            reservationResult.innerHTML = `
                <h3>Reservation Confirmed</h3>

                <p>
                    <strong>Passenger:</strong>
                    ${data.passenger}
                </p>

                <p>
                    <strong>Train:</strong>
                    ${data.trainNumber}
                </p>

                <p>
                    <strong>Seats:</strong>
                    ${data.seats}
                </p>

                <p>
                    <strong>Route:</strong>
                    ${data.source}
                    →
                    ${data.destination}
                </p>

                <p>
                    <strong>Shortest Route:</strong>
                    ${data.route}
                </p>

                <p>
                    <strong>Distance:</strong>
                    ${data.distance} km
                </p>

                <p>
                    <strong>Available Seats:</strong>
                    ${data.availableSeats}
                </p>

                <p class="success">
                    Reservation saved successfully.
                </p>
            `;


        } catch (error) {

            reservationResult.innerHTML =
                `<p class="error">
                    Unable to connect to the Java server.
                    Make sure the backend server is running.
                </p>`;

            console.error(error);
        }
    }
);