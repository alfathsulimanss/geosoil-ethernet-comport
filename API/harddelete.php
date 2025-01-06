<?php
// Set the content-type to JSON (optional but good practice)
header("Content-Type: application/json");

// Database connection settings
$servername = "localhost"; // Or your DB server address
$username = "root";         // Your DB username
$password = "";             // Your DB password
$dbname = "projectdata";    // Your database name

// Create connection to the database
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die(json_encode(array("status" => "error", "message" => "Connection failed: " . $conn->connect_error)));
}

// Retrieve the JSON data from the request
$json_data = file_get_contents('php://input');

// Decode JSON to associative array
$data = json_decode($json_data, true);

// Check if decoding was successful
if (json_last_error() !== JSON_ERROR_NONE) {
    echo json_encode(array("status" => "error", "message" => "Invalid JSON"));
    exit();
}

// Validate required inputs
if (empty($data['table']) || empty($data['condition'])) {
    echo json_encode(array("status" => "error", "message" => "Both 'table' and 'condition' are required"));
    exit();
}

$table = $data['table'];
$condition = $data['condition'];

// Perform the DELETE operation
$delete_query = "DELETE FROM `$table` WHERE $condition";
if ($conn->query($delete_query) === true) {
    echo json_encode(array(
        "status" => "success",
        "message" => "Record(s) deleted successfully."
    ));
} else {
    echo json_encode(array("status" => "error", "message" => "Error deleting records: " . $conn->error));
}

// Close the database connection
$conn->close();
?>
