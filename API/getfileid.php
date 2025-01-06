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

// Retrieve JSON input
$rawInput = file_get_contents("php://input");
$input = json_decode($rawInput, true);

// Check if valid JSON was provided or no input was sent
if ($rawInput === "" || $input === null) {
    // No JSON or invalid JSON: proceed to fetch all data
    $testname = null;
} else {
    // Extract testname from valid JSON input
    $testname = isset($input['testname']) ? $conn->real_escape_string($input['testname']) : null;
}

// Build SQL query
if ($testname) {
    // Query to fetch data filtered by testname
    $sql = "SELECT * FROM testfile WHERE testname = '$testname' ORDER BY id ASC";
} else {
    // Query to fetch all data
    $sql = "SELECT * FROM testfile ORDER BY id ASC";
}
    
// Execute the query
$result = $conn->query($sql);

if ($result && $result->num_rows > 0) {
	$rows = array();
	while ($row = $result->fetch_assoc()) {

		// Append to the rows array with the same format as write
		$rows[] = array(
			"id" => $row['id'],
			"created_date" => $row['created_date'],
			"testname" => $row['testname'],
			"jobno" => $row['jobno'],
			"jobdesc" => $row['jobdesc'],
			"sampleid" => $row['sampleid'],
			"date" => $row['date'],
			"specimentno" => $row['specimentno'],
			"depth" => $row['depth'],
			"height" => $row['height'],
			"diameter" => $row['diameter'],
			"weight" => $row['date'],
			"done" => $row['done']
		);
	}

	// Return the data in the desired format
	echo json_encode(array("status" => "success", "data" => $rows));
} else {
	echo json_encode(array("status" => "error", "message" => "No records found"));
}
// Close the database connection
$conn->close();
?>
