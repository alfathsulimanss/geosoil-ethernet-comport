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
            isset($data['jobid']) && 
            isset($data['sampleno']) && 
            isset($data['specimentno']) && 
            isset($data['depth']) && 
            isset($data['height']) && 
            isset($data['diameter']) && 
            isset($data['weight'])
        ) {
            // Extract fields
            $jobid = $data['jobid'];
            $sampleno = $data['sampleno'];
            $specimentno = $data['specimentno'];
            $depth = $data['depth'];
            $height = $data['height'];
            $diameter = $data['diameter'];
            $weight = $data['weight'];

            // SQL query to insert the data
            $sql = "INSERT INTO sample (jobid, sampleno, specimentno, depth, height, diameter, weight)
                    VALUES ('$jobid', '$sampleno', '$specimentno', '$depth', '$height', '$diameter', '$weight')";

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
		// Initialize query
		$conditions = array("`delete` = 0");

		// Add filters if provided
		if (isset($data['jobid'])) {
			$jobid = $data['jobid'];
			$conditions[] = "jobid = '$jobid'";
		}

		if (isset($data['sampleid'])) {
			$sampleid = $data['sampleid'];
			$conditions[] = "id = '$sampleid'";
		}

		// Combine conditions into WHERE clause
		$whereClause = implode(' AND ', $conditions);
		$sql = "SELECT * FROM sample WHERE $whereClause";

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

    case 'delete':
        // Check if sampleno is provided for soft delete
        if (isset($data['sampleid'])) {
            $sampleid = $data['sampleid'];

            // SQL query to update delete column to 1
            $sql = "UPDATE sample SET `delete` = 1 WHERE id = '$sampleid'";

            if ($conn->query($sql) === TRUE) {
                echo json_encode(array("status" => "success", "message" => "Data soft-deleted successfully"));
            } else {
                echo json_encode(array("status" => "error", "message" => "Error: " . $sql . " " . $conn->error));
            }
        } else {
            echo json_encode(array("status" => "error", "message" => "Missing sampleid for deletion"));
        }
        break;

    case 'update':
        // Check if the required fields for update are present
        if (
            isset($data['id']) && 
            isset($data['jobid']) && 
            isset($data['sampleno']) && 
            isset($data['specimentno']) && 
            isset($data['depth']) && 
            isset($data['height']) && 
            isset($data['diameter']) && 
            isset($data['weight'])
        ) {
            // Extract fields
            $id = $data['id'];
            $jobid = $data['jobid'];
            $sampleno = $data['sampleno'];
            $specimentno = $data['specimentno'];
            $depth = $data['depth'];
            $height = $data['height'];
            $diameter = $data['diameter'];
            $weight = $data['weight'];

            // SQL query to update the data
            $sql = "UPDATE sample 
                    SET jobid = '$jobid', sampleno = '$sampleno', specimentno = '$specimentno', 
                        depth = '$depth', height = '$height', diameter = '$diameter', weight = '$weight'
                    WHERE id = '$id'";

            // Execute the query
            if ($conn->query($sql) === TRUE) {
                echo json_encode(array("status" => "success", "message" => "Data updated successfully"));
            } else {
                echo json_encode(array("status" => "error", "message" => "Error: " . $sql . " " . $conn->error));
            }
        } else {
            echo json_encode(array("status" => "error", "message" => "Missing required fields for update"));
        }
        break;

    default:
        echo json_encode(array("status" => "error", "message" => "Invalid action specified"));
        break;
}

// Close the database connection
$conn->close();
?>