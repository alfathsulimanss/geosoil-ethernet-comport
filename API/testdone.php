<?php
// Set the content-type to JSON (optional but good practice)
header("Content-Type: application/json");

// Database connection settings
$servername = "localhost"; // Or your DB server address
$username = "root";         // Your DB username
$password = "";             // Your DB password
$dbname = "projectdata";  // Your database name

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

// Check if the required fields are present in the JSON object
if (
    isset($data['done']) &&
	isset($data['fileid'])
) {
    // Extract the common fields
    $done = $data['done'];
	$id = $data['fileid'];

    // SQL query to insert the data (make sure 'sampleid' and 'date' are quoted)
    $sql = "UPDATE testfile SET done = '$done' WHERE id = '$id'";

    // Execute the query
    if ($conn->query($sql) === TRUE) {
        
        // Return success response with the inserted ID
        echo json_encode(array("status" => "success", "message" => "Data updated successfully"));
    } else {
        // Return error if the query fails
        echo json_encode(array("status" => "error", "message" => "Error: " . $sql . " " . $conn->error));
    }
} else {
    // Missing fields in JSON or invalid data format
    echo json_encode(array("status" => "error", "message" => "Missing required fields or invalid data format"));
}

// Close the database connection
$conn->close();
?>
