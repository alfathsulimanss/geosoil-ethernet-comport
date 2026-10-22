<?php
header("Content-Type: application/json");

// Set the server's local timezone automatically
date_default_timezone_set(ini_get('date.timezone') ?: 'Asia/Kuala_Lumpur');

$response = [
    "time" => date("H:i:s"),
    "seconds_since_midnight" => (date("H") * 3600) + (date("i") * 60) + date("s"),
    "unix_timestamp" => time(),  // ✅ Unix timestamp
    "timezone" => date_default_timezone_get()
];

echo json_encode($response);
?>
