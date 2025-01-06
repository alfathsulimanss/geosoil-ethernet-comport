<?php
// Set the content-type to JSON
header("Content-Type: application/json");

// Database connection settings
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "projectdata";

// Create connection to the database
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die(json_encode(array("status" => "error", "message" => "Connection failed: " . $conn->connect_error)));
}

// Retrieve JSON data from the request
$json_data = file_get_contents('php://input');

// Decode JSON to associative array
$data = json_decode($json_data, true);

// Check if decoding was successful
if (json_last_error() !== JSON_ERROR_NONE) {
    echo json_encode(array("status" => "error", "message" => "Invalid JSON"));
    exit();
}

// Check if required parameters are present
if (isset($data['fileid'])) {
	$fileid = $data['fileid'];

    // SQL query to select the data based on testname and testtype
    $sql = "SELECT testname, testtype FROM historydata WHERE fileid = '$fileid' ORDER BY id ASC";
    
    // Execute the query
    $result = $conn->query($sql);

    if ($result && $result->num_rows > 0) {
        $rows = array();
        while ($row = $result->fetch_assoc()) {

            // Append to the rows array with the same format as write
            $rows[] = array(
                "testname" => $row ['testname'],
                "testtype" => $row ['testtype']
            );
        }

        // Return the data in the desired format
        echo json_encode(array("status" => "success", "data" => $rows));
    } else {
        echo json_encode(array("status" => "error", "message" => "No records found for fileid: $fileid"));
    }

} else {
    // Missing required fields
    echo json_encode(array("status" => "error", "message" => "Missing required fields: fileid"));
}

// Close the database connection
$conn->close();
?>
