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

// Check if 'action' is specified
if (!isset($data['action'])) {
    echo json_encode(array("status" => "error", "message" => "Missing action parameter"));
    exit();
}

// Determine action
$action = $data['action'];

switch ($action) {
    case 'insert':
        // Check if the required fields are present
        if (
            isset($data['message']) &&
			isset($data['fileid'])
        ) {
            // Extract fields
            $message = $data['message'];
			$fileid = $data['fileid'];

            // SQL query to insert the data
            $sql = "INSERT INTO event (message, fileid)
                    VALUES ('$message','$fileid')";

            // Execute the query
            if ($conn->query($sql) === TRUE) {
                $last_id = $conn->insert_id;
                echo json_encode(array("status" => "success", "message" => "Data inserted successfully", "inserted_id" => $last_id));
            } else {
                echo json_encode(array("status" => "error", "message" => "Error: " . $sql . " " . $conn->error));
            }
        } else {
            echo json_encode(array("status" => "error", "message" => "Missing required fields for insertion"));
        }
        break;

	case 'read':
		// Check if the required fields are present
		if (
			isset($data['fileid'])
        ) {
            // Extract fields
			$fileid = $data['fileid'];
	
		// Initialize query

		$sql = "SELECT `created_date`, `message` FROM event WHERE fileid = $fileid ORDER BY created_date DESC LIMIT 5";

		// Execute query
		$result = $conn->query($sql);

		if ($result->num_rows > 0) {
			$rows = array();
			while ($row = $result->fetch_assoc()) {
				$rows[] = $row;
			}
			echo json_encode(array("status" => "success", "data" => $rows));
		} else {
			echo json_encode(array("status" => "success", "data" => []));
		}
		
		} else {
            echo json_encode(array("status" => "error", "message" => "Missing required fields for insertion"));
        }
		
		break;
		
	case 'readAll':
	
		// Initialize query

		$sql = "SELECT `created_date`, `message` FROM event ORDER BY created_date DESC LIMIT 5";

		// Execute query
		$result = $conn->query($sql);

		if ($result->num_rows > 0) {
			$rows = array();
			while ($row = $result->fetch_assoc()) {
				$rows[] = $row;
			}
			echo json_encode(array("status" => "success", "data" => $rows));
		} else {
			echo json_encode(array("status" => "success", "data" => []));
		}
		
		break;

    default:
        echo json_encode(array("status" => "error", "message" => "Invalid action specified"));
        break;
}

// Close the database connection
$conn->close();
?>