<?php
// Set the content-type to JSON
header("Content-Type: application/json");

// Database connection settings
$servername = "localhost";
$username   = "root";
$password   = "";
$dbname     = "projectdata";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die(json_encode(["status" => "error", "message" => "Connection failed: " . $conn->connect_error]));
}

// Retrieve raw JSON data
$json_data = file_get_contents('php://input');
$data = json_decode($json_data, true);

// Validate JSON syntax
if (json_last_error() !== JSON_ERROR_NONE) {
    echo json_encode(["status" => "error", "message" => "Invalid JSON"]);
    exit();
}

// Ensure 'done' field exists
if (!isset($data['done'])) {
    echo json_encode(["status" => "error", "message" => "Missing required field: 'done'"]);
    $conn->close();
    exit();
}

$done = $data['done'];

// Check if fileid is provided and not empty
if (isset($data['fileid']) && $data['fileid'] !== '') {
    $id = $data['fileid'];
    $stmt = $conn->prepare("UPDATE testfile SET done = ? WHERE id = ?");
    $stmt->bind_param("ss", $done, $id);
} else {
    // Fallback query when fileid is omitted
    $stmt = $conn->prepare("UPDATE testfile SET done = ? WHERE done = '0'");
    $stmt->bind_param("s", $done);
}

// Execute query
if ($stmt->execute()) {
    echo json_encode([
        "status" => "success",
        "message" => "Data updated successfully",
        "affected_rows" => $stmt->affected_rows
    ]);
} else {
    echo json_encode(["status" => "error", "message" => "Query failed: " . $stmt->error]);
}

$stmt->close();
$conn->close();
?>