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
if (isset($data['testtype']) && isset($data['testname']) && isset($data['fileid'])) {
    $testtype = $data['testtype'];
    $testname = $data['testname'];
	$fileid = $data['fileid'];

    // Initialize SQL query based on testtype
    $columns = '';
    $dataFields = array(); // To store the data fields for the response

    switch ($testtype) {
        case 1:
            $columns = "`timestamp`, `elapsetime`, `Cell Pressure`, `Pore Pressure`, `Back Pressure`, `Volume Change`, `Load`, `Displacement`, `Change of Pore Pressure`, `Change in Volume`, `Axial Load Change`, `Change in Length`, `Deviator Stress`, `Axial Strain`";
            $dataFields = ['Cell Pressure', 'Pore Pressure', 'Back Pressure', 'Volume Change', 'Load', 'Displacement', 'Change of Pore Pressure', 'Change in Volume', 'Axial Load Change', 'Change in Length', 'Deviator Stress', 'Axial Strain'];
            break;

        case 2:
            $columns = "`timestamp`, `elapsetime`, `Cell Pressure`, `Pore Pressure`, `Vertical Load`, `Displacement`, `Change Pore Pressure`, `Axial Load Change`, `Change in Length`, `Deviator Stress`, `Axial Strain`";
            $dataFields = ['Cell Pressure', 'Pore Pressure', 'Vertical Load', 'Displacement', 'Change Pore Pressure', 'Axial Load Change', 'Change in Length', 'Deviator Stress', 'Axial Strain'];
            break;

        case 3:
            $columns = "`timestamp`, `elapsetime`, `Vertical Load`, `Vertical Displacement`, `Horizontal Load`, `Horizontal Displacement`";
            $dataFields = ['Vertical Load', 'Vertical Displacement', 'Horizontal Load', 'Horizontal Displacement'];
            break;

        case 4:
            $columns = "`timestamp`, `elapsetime`, `Cell Pressure`, `Pore Pressure`, `Back Pressure`, `Inlet Volume`, `Back Pressure 2`, `Outlet Volume`, `Inlet Volume Change`, `Outlet Volume Change`";
            $dataFields = ['Cell Pressure', 'Pore Pressure', 'Back Pressure', 'Inlet Volume', 'Back Pressure 2', 'Outlet Volume', 'Inlet Volume Change', 'Outlet Volume Change'];
            break;

        case 5:
            $columns = "`timestamp`, `elapsetime`, `Load`, `Displacement`, `Vertical Stress`, `Height Settlement`, `Total Height Settlement`";
            $dataFields = ['Load', 'Displacement', 'Vertical Stress', 'Height Settlement', 'Total Height Settlement'];
            break;

        case 6:
            $columns = "`timestamp`, `elapsetime`, `Cell Pressure`, `Pore Pressure`, `Back Pressure`, `Volume Change`, `B-Value`";
            $dataFields = ['Cell Pressure', 'Pore Pressure', 'Back Pressure', 'Volume Change', 'B-Value'];
            break;

        case 7:
            $columns = "`timestamp`, `elapsetime`, `Cell Pressure`, `Pore Water Pressure`, `Back Pressure`, `Volume Change 1`, `Back Pressure 2`, `Volume Change 2`, `Vertical Load`, `Vertical Displacement`, `Horizontal Load`, `Horizontal Displacement`";
            $dataFields = ['Cell Pressure', 'Pore Water Pressure', 'Back Pressure', 'Volume Change 1', 'Back Pressure 2', 'Volume Change 2', 'Vertical Load', 'Vertical Displacement', 'Horizontal Load', 'Horizontal Displacement'];
            break;
			
		case 8:
            $columns = "`timestamp`, `elapsetime`, `Load`, `Displacement`, `Vertical Stress`, `Load Change`, `Change in Length`, `Deviator Stress`, `Axial Strain`";
            $dataFields = ['Load', 'Displacement', 'Vertical Stress', 'Load Change', 'Change in Length', 'Deviator Stress', 'Axial Strain'];
            break;
		
		case 9:
            $columns = "`timestamp`, `elapsetime`, `Cell Pressure`, `Pore Pressure`, `Back Pressure`, `Volume Change`, `Change Pore Pressure`, `Change in Volume`, `Pore Pressure Dissipation`";
            $dataFields = ['Cell Pressure', 'Pore Pressure', 'Back Pressure', 'Volume Change', 'Change Pore Pressure', 'Change in Volume', 'Pore Pressure Dissipation'];
            break;

        default:
            echo json_encode(array("status" => "error", "message" => "Invalid test type"));
            exit();
    }

    // SQL query to select the data based on testname and testtype
    $sql = "SELECT $columns FROM historydata WHERE testname = '$testname' AND testtype = $testtype AND fileid = '$fileid'";
    
    // Execute the query
    $result = $conn->query($sql);

    if ($result && $result->num_rows > 0) {
        $rows = array();
        while ($row = $result->fetch_assoc()) {
            // Build the 'data' array based on dataFields
            $dataArray = array();
            foreach ($dataFields as $field) {
                $dataArray[] = $row[$field];
            }

            // Append to the rows array with the same format as write
            $rows[] = array(
                "testname" => $testname,
                "timestamp" => $row['timestamp'],
                "elapsetime" => $row['elapsetime'],
                "testtype" => $testtype,
                "data" => $dataArray
            );
        }

        // Return the data in the desired format
        echo json_encode(array("status" => "success", "data" => $rows));
    } else {
        echo json_encode(array("status" => "error", "message" => "No records found for testname: $testname and testtype: $testtype"));
    }

} else {
    // Missing required fields
    echo json_encode(array("status" => "error", "message" => "Missing required fields: testtype or testname"));
}

// Close the database connection
$conn->close();
?>
