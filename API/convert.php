<?php

// Allow access from LabVIEW (for CORS policy)
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Content-Type: application/json');

// Get the TDMS file path and output Excel path from the HTTP POST request
$input = file_get_contents('php://input');
$data = json_decode($input, true);

// Retrieve file paths from the JSON request
$tdms_file_path = $data['tdms_path'] ?? null;
$output_excel_path = $data['excel_path'] ?? null;

// Check if the TDMS file path and output file path are provided
if (!$tdms_file_path || !$output_excel_path) {
    echo json_encode(['status' => 'error', 'message' => 'TDMS file path or output path is missing.']);
    exit;
}

// Python script path (make sure the path is correct)
$python_path = 'F:\laragon\bin\python\python-3.10\python.exe';  // Replace with your actual Python path
$python_script = 'tdms-to-excel.py';

// Command to execute the Python script
$command = escapeshellcmd("$python_path \"$python_script\" \"$tdms_file_path\" \"$output_excel_path\"");

// Run the command and capture the output and return status
$output = shell_exec($command);

// Check if the shell_exec output is empty or the command failed
if ($output === null) {
    echo json_encode(['status' => 'error', 'message' => 'Python script execution failed.']);
    exit;
}

// Log the output for debugging
error_log($output);  // Log output to PHP error log for debugging

// Check if the conversion was successful by checking the output
if (strpos($output, 'successfully converted') !== false) {
    echo json_encode(['status' => 'success', 'message' => 'File converted successfully.', 'output' => $output_excel_path]);
} else {
    echo json_encode(['status' => 'error', 'message' => 'Conversion failed.', 'details' => $output]);
}
