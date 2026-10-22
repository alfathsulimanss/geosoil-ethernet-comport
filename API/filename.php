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

    switch ($action) {
        case "insert":
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

                $sql = "INSERT INTO testfile (testname, jobno, jobdesc, sampleid, date, specimentno, depth, height, diameter, weight)
                        VALUES ('$testname', '$jobno', '$jobdesc', '$sampleid', '$date', '$specimentno', '$depth', '$height', '$diameter', '$weight')";

                if ($conn->query($sql) === TRUE) {
                    $last_id = $conn->insert_id;
                    echo json_encode(array("status" => "success", "message" => "Data inserted successfully", "inserted_id" => $last_id));
                } else {
                    echo json_encode(array("status" => "error", "message" => "Error: " . $sql . " " . $conn->error));
                }
            } else {
                echo json_encode(array("status" => "error", "message" => "Missing required fields for INSERT action"));
            }
            break;

        case "update":
            if (!isset($data['id'])) {
                echo json_encode(["status" => "error", "message" => "Missing 'id' field for UPDATE action"]);
                break;
            }

            $id = $data['id'];
            
            // List of valid updatable database columns to protect against SQL injection
            $allowed_fields = [
                'testname', 'jobno', 'jobdesc', 'sampleid', 'date', 
                'specimentno', 'depth', 'height', 'diameter', 'weight', 'done'
            ];

            $fields_to_update = [];
            $types = "";
            $params = [];

            // Identify which fields were passed in the payload
            foreach ($allowed_fields as $field) {
                if (array_key_exists($field, $data)) {
                    $fields_to_update[] = "`$field` = ?";
                    $types .= "s"; // Bind all parameter values as string
                    $params[] = $data[$field];
                }
            }

            if (empty($fields_to_update)) {
                echo json_encode(["status" => "error", "message" => "No valid fields provided to update"]);
                break;
            }

            // Build dynamic update query
            $sql = "UPDATE testfile SET " . implode(", ", $fields_to_update) . " WHERE id = ?";
            $types .= "i"; // 'id' parameter type
            $params[] = $id;

            $stmt = $conn->prepare($sql);
            if ($stmt) {
                $stmt->bind_param($types, ...$params);

                if ($stmt->execute()) {
                    if ($stmt->affected_rows > 0) {
                        echo json_encode(["status" => "success", "message" => "Record updated successfully", "updated_id" => $id]);
                    } else {
                        echo json_encode(["status" => "warning", "message" => "No changes made or record not found"]);
                    }
                } else {
                    echo json_encode(["status" => "error", "message" => "Execution failed: " . $stmt->error]);
                }
                $stmt->close();
            } else {
                echo json_encode(["status" => "error", "message" => "Preparation failed: " . $conn->error]);
            }
            break;

        case "delete":
            if (isset($data['id'])) {
                $id = $data['id'];
                $sql = "DELETE FROM testfile WHERE id = '$id'";

                if ($conn->query($sql) === TRUE) {
                    if ($conn->affected_rows > 0) {
                        echo json_encode(array("status" => "success", "message" => "Data deleted successfully", "deleted_id" => $id));
                    } else {
                        echo json_encode(array("status" => "error", "message" => "No record found with the given ID"));
                    }
                } else {
                    echo json_encode(array("status" => "error", "message" => "Error: " . $sql . " " . $conn->error));
                }
            } else {
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
                        $row['id'] = (string)$row['id'];
                        $row['done'] = (string)$row['done'];
                        $data[] = $row;
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
            echo json_encode(array("status" => "error", "message" => "Invalid action specified"));
            break;
    }
} else {
    echo json_encode(array("status" => "error", "message" => "Missing 'action' key in JSON"));
}

$conn->close();
?>