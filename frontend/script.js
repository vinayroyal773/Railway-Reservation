const searchButton = document.getElementById("searchRoute");
const sourceSelect = document.getElementById("source");
const destinationSelect = document.getElementById("destination");
const result = document.getElementById("result");

searchButton.addEventListener("click", function () {

    const source = sourceSelect.value;
    const destination = destinationSelect.value;

    if (source === "" || destination === "") {
        result.innerHTML = "<p>Please select both source and destination.</p>";
        return;
    }

    if (source === destination) {
        result.innerHTML = "<p>Source and destination cannot be the same.</p>";
        return;
    }

    /*
     * Backend integration will be connected here.
     *
     * The Java backend should eventually receive:
     * source
     * destination
     *
     * and return:
     * shortest route
     * total distance
     */

    result.innerHTML = `
        <h3>Route Request</h3>
        <p><strong>Source:</strong> ${source}</p>
        <p><strong>Destination:</strong> ${destination}</p>
        <p>Searching for the shortest route...</p>
    `;
});