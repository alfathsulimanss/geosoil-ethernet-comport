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

// Check if the 'action' key exists in the JSON object
if (isset($data['action'])) {
    $action = $data['action'];

    // Use a switch statement to handle actions
    switch ($action) {
        case "insert":
            // Check if the required fields are present
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
                // Extract the fields
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

                // SQL query to insert the data
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
                // Missing fields for INSERT action
                echo json_encode(array("status" => "error", "message" => "Missing required fields for INSERT action"));
            }
            break;

        case "delete":
            // Check if the required field 'id' is present
            if (isset($data['id'])) {
                $id = $data['id'];

                // SQL query to delete the data
                $sql = "DELETE FROM testfile WHERE id = '$id'";

                // Execute the query
                if ($conn->query($sql) === TRUE) {
                    if ($conn->affected_rows > 0) {
                        // Return success response
                        echo json_encode(array("status" => "success", "message" => "Data deleted successfully", "deleted_id" => $id));
                    } else {
                        // No rows affected, ID not found
                        echo json_encode(array("status" => "error", "message" => "No record found with the given ID"));
                    }
                } else {
                    // Return error if the query fails
                    echo json_encode(array("status" => "error", "message" => "Error: " . $sql . " " . $conn->error));
                }
            } else {
                // Missing 'id' field for DELETE action
                echo json_encode(array("status" => "error", "message" => "Missing 'id' field for DELETE action"));
            }
            break;
			
		case "read_all":
			$sql = "SELECT * FROM testfile";
			$result = $conn->query($sql);

			if ($result->num_rows > 0) {
				$data = [];
				while ($row = $result->fetch_assoc()) {
					$data[] = $row;
				}
				echo json_encode(["status" => "success", "data" => $data]);
			} else {
				echo json_encode(["status" => "error", "message" => "No records found"]);
			}
			break;

		case "read_by_id":
			if (isset($data['id'])) {
				$stmt = $conn->prepare("SELECT * FROM testfile WHERE id = ?");
				$stmt->bind_param("i", $data['id']);
				$stmt->execute();
				$result = $stmt->get_result();

				if ($result->num_rows > 0) {
					$data = [];
					while ($row = $result->fetch_assoc()) {
						$row['id'] = (string)$row['id']; // Convert ID to string
						$row['done'] = (string)$row['done']; // Convert ID to string
						$data[] = $row; // Store result as an array, same as "read_all"
					}
					echo json_encode(["status" => "success", "data" => $data]);
				} else {
					echo json_encode(["status" => "error", "message" => "No record found with the given ID", "data" => []]);
				}

				$stmt->close();
			} else {
            echo json_encode(["status" => "error", "message" => "Missing 'id' field"]);
			}
			break;

        default:
            // Handle invalid actions
            echo json_encode(array("status" => "error", "message" => "Invalid action specified"));
            break;
    }
} else {
    // Missing 'action' key in JSON
    echo json_encode(array("status" => "error", "message" => "Missing 'action' key in JSON"));
}

// Close the database connection
$conn->close();
?>
