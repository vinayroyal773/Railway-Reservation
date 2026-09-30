/*
    Railway Reservation
    Error Detection Module

    Method:
    CRC - Cyclic Redundancy Check
*/


// Generate CRC value from data
function calculateCRC(data) {

    let crc = 0;

    for (let i = 0; i < data.length; i++) {

        crc = crc ^ data.charCodeAt(i);

    }

    return crc.toString(16).toUpperCase();
}



// Generate CRC for reservation data
function generateCRC() {

    const data =
        document.getElementById("originalData").value;

    if (data.trim() === "") {

        alert("Please enter reservation data.");

        return;
    }


    const crc = calculateCRC(data);


    document.getElementById("generatedCRC").textContent = crc;


    // Automatically place data and CRC
    // into the received section for testing

    document.getElementById("receivedData").value = data;

    document.getElementById("receivedCRC").value = crc;


    showStatus(
        "CRC generated successfully.",
        "success"
    );
}



// Check whether received data contains an error
function checkError() {

    const receivedData =
        document.getElementById("receivedData").value;

    const receivedCRC =
        document.getElementById("receivedCRC").value.trim();


    if (receivedData.trim() === "") {

        alert("Please enter received data.");

        return;
    }


    if (receivedCRC === "") {

        alert("Please enter received CRC.");

        return;
    }


    // Calculate CRC again from received data

    const calculatedCRC =
        calculateCRC(receivedData);


    // Compare CRC values

    if (
        calculatedCRC.toUpperCase() ===
        receivedCRC.toUpperCase()
    ) {

        showStatus(
            "✓ No Error Detected - Data is correct.",
            "success"
        );

    } else {

        showStatus(
            "✗ Error Detected - Data may be corrupted.",
            "error"
        );

    }

}



// Display result message
function showStatus(message, type) {

    const status =
        document.getElementById("status");


    status.textContent = message;


    status.className =
        "status " + type;

}