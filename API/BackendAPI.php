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
    isset($data['timestamp']) && 
    isset($data['elapsetime']) &&
	isset($data['stage']) && 
    isset($data['testname']) && 
    isset($data['testtype']) && 
	isset($data['fileid']) && 
    isset($data['data']) && 
    is_array($data['data'])
) {
    // Extract the common fields
    $testname = $data['testname'];
	$fileid = $data['fileid'];
    $timestamp = !empty($data['timestamp']) ? $data['timestamp'] : date("Y-m-d H:i:s"); // Use provided timestamp or current if empty
    $elapsetime = $data['elapsetime'];
    $testtype = $data['testtype'];
	$stage = $data['stage'];

    // Initialize variables for the SQL query
    $columns = '';
    $values = '';
    
    // Determine the columns and values to insert based on the testtype
    switch ($testtype) {
        case 1:
            if (count($data['data']) === 12) {
                $columns = "`Cell Pressure`, `Back Pressure`, `Volume Change`, `Load`, `Displacement`, `Pore Pressure`, `Change of Pore Pressure`, `Change in Volume`, `Axial Load Change`, `Change in Length`, `Deviator Stress`, `Axial Strain`";
                $values = "'" . implode("', '", $data['data']) . "'";
            }
            break;
        
        case 2:
            if (count($data['data']) === 9) {
                $columns = "`Cell Pressure`, `Vertical Load`, `Displacement`, `Pore Pressure`, `Change Pore Pressure`, `Axial Load Change`, `Change in Length`, `Deviator Stress`, `Axial Strain`";
                $values = "'" . implode("', '", $data['data']) . "'";
            }
            break;
        
        case 3:
            if (count($data['data']) === 4) {
                $columns = "`Vertical Load`, `Vertical Displacement`, `Horizontal Load`, `Horizontal Displacement`";
                $values = "'" . implode("', '", $data['data']) . "'";
            }
            break;
        
        case 4:
            if (count($data['data']) === 8) {
                $columns = "`Cell Pressure`, `Pore Pressure`, `Back Pressure`, `Inlet Volume`, `Back Pressure 2`, `Outlet Volume`, `Inlet Volume Change`, `Outlet Volume Change`";
                $values = "'" . implode("', '", $data['data']) . "'";
            }
            break;
        
        case 5:
            if (count($data['data']) === 5) {
                $columns = "`Load`, `Displacement`, `Vertical Stress`, `Height Settlement`, `Total Height Settlement`";
                $values = "'" . implode("', '", $data['data']) . "'";
            }
            break;
        
        case 6:
            if (count($data['data']) === 8) {
                $columns = "`Cell Pressure`, `Back Pressure`, `Volume Change`, `Pore Pressure`, `B-Value`, `Change Pore Pressure`, `Pore Pressure Dissipation`, `Change in Volume`";
                $values = "'" . implode("', '", $data['data']) . "'";
            }
            break;
        
        case 7:
            if (count($data['data']) === 10) {
                $columns = "`Cell Pressure`, `Pore Water Pressure`, `Back Pressure`, `Volume Change 1`, `Back Pressure 2`, `Volume Change 2`, `Vertical Load`, `Vertical Displacement`, `Horizontal Load`, `Horizontal Displacement`";
                $values = "'" . implode("', '", $data['data']) . "'";
            }
            break;
			
		case 8:
            if (count($data['data']) === 7) {
                $columns = "`Load`, `Displacement`, `Vertical Stress`, `Load Change`, `Change in Length`, `Deviator Stress`, `Axial Strain`";
                $values = "'" . implode("', '", $data['data']) . "'";
            }
            break;
			
		case 9:
            if (count($data['data']) === 7) {
                $columns = "`Cell Pressure`, `Back Pressure`, `Volume Change`, `Pore Pressure`, `Change Pore Pressure`, `Pore Pressure Dissipation`, `Change in Volume`";
                $values = "'" . implode("', '", $data['data']) . "'";
            }
            break;
        
        default:
            echo json_encode(array("status" => "error", "message" => "Invalid test type"));
            exit();
    }

    // Proceed if the columns and values are correctly mapped
    if (!empty($columns) && !empty($values)) {
        // SQL query to insert the data
        $sql = "INSERT INTO historydata (testname, fileid, stage, `timestamp`, elapsetime, testtype, $columns)
                VALUES ('$testname','$fileid', '$stage', '$timestamp', '$elapsetime', $testtype, $values)";

        // Execute the query
        if ($conn->query($sql) === TRUE) {
            echo json_encode(array("status" => "success", "message" => "Data inserted successfully"));
        } else {
            echo json_encode(array("status" => "error", "message" => "Error: " . $sql . " " . $conn->error));
        }
    } else {
        // Invalid data array length for the test type
        echo json_encode(array("status" => "error", "message" => "Invalid data format for test type $testtype"));
    }

} else {
    // Missing fields in JSON or invalid data format
    echo json_encode(array("status" => "error", "message" => "Missing required fields or invalid data format"));
}

// Close the database connection
$conn->close();
?>
