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
    isset($data['testname']) && 
    isset($data['jobno']) && 
    isset($data['jobdesc']) && 
    isset($data['sampleid']) && 
    isset($data['date']) &&
	isset($data['specimentno']) && 
    isset($data['depth']) && 
    isset($data['height']) && 
    isset($data['diameter']) && 
    isset($data['weight'])
) {
    // Extract the common fields
    $testname = $data['testname'];
    $jobno = $data['jobno'];
    $jobdesc = $data['jobdesc'];
    $sampleid = $data['sampleid'];
	$date = $data['date'];
	$specimentno = $data['specimentno'];
    $depth = $data['depth'];
    $height = $data['height'];
    $diameter = $data['diameter'];
	$weight = $data['weight'];

    // SQL query to insert the data (make sure 'sampleid' and 'date' are quoted)
    $sql = "INSERT INTO testfile (testname, jobno, jobdesc, sampleid, date, specimentno, depth, height, diameter, weight)
            VALUES ('$testname', '$jobno', '$jobdesc', '$sampleid', '$date', '$specimentno', '$depth', '$height', '$diameter', '$weight')";

    // Execute the query
    if ($conn->query($sql) === TRUE) {
        // Get the last inserted ID
        $last_id = $conn->insert_id;
        
        // Return success response with the inserted ID
        echo json_encode(array("status" => "success", "message" => "Data inserted successfully", "inserted_id" => $last_id));
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
