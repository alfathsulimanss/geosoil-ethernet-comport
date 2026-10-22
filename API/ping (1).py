import subprocess
import csv
import mysql.connector
import time
import os

# Database configuration
db_config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "",
    "database": "projectdata",
    "auth_plugin": "mysql_native_password"
}

# Paths (use raw strings to avoid escape issues)
csv_file = r"F:\Geosoil Drive\geosoil-ethernet-comport\data\ping_results.csv"
stop_file = r"F:\Geosoil Drive\geosoil-ethernet-comport\data\stop_ping.txt"

# Interval between ping cycles (seconds)
interval = 1

def get_db_connection():
    """Create a MySQL database connection"""
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}", flush=True)
        return None

def read_devices():
    """Read devices from MySQL database"""
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database. Retrying...", flush=True)
        return []
    
    try:
        cursor = conn.cursor()
        query = "SELECT SNIP, devicename FROM device"
        cursor.execute(query)
        devices = [(row[0], row[1]) for row in cursor.fetchall()]
        cursor.close()
        return devices
    except mysql.connector.Error as err:
        print(f"Error reading from database: {err}", flush=True)
        return []
    finally:
        conn.close()

def is_online(ip, ping_counts=[1,2,4]):
    error_strings = [
        "destination host unreachable",
        "request timed out",
        "could not find host"
    ]
    for count in ping_counts:
        try:
            response = subprocess.run(
                ["ping", "-n", str(count), ip],
                capture_output=True,
                text=True
            )
            output = response.stdout.lower()
            if any(err in output for err in error_strings):
                return False
            if "reply from" in output:
                return True
        except Exception as e:
            print(f"Ping error {ip}: {e}", flush=True)
    return False

def read_existing_csv():
    """Read existing CSV into a dict {IP: [Device Name, Status]}"""
    existing = {}
    if os.path.exists(csv_file):
        try:
            with open(csv_file, newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing[row["IP"]] = [row["Device Name"], row["Status"]]
        except Exception as e:
            print(f"Error reading CSV: {e}", flush=True)
    return existing

def write_csv(data_dict):
    """Write the updated CSV using a temporary file to avoid conflicts"""
    temp_file = csv_file + ".tmp"
    try:
        with open(temp_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["IP", "Device Name", "Status"])
            for ip, (name, status) in data_dict.items():
                writer.writerow([ip, name, status])
        os.replace(temp_file, csv_file)
    except Exception as e:
        print(f"Error writing CSV: {e}", flush=True)

try:
    while True:
        # Stop condition for LabVIEW
        if os.path.exists(stop_file):
            print("Stop signal detected. Exiting.", flush=True)
            os.remove(stop_file)
            break

        # Read devices from database
        devices = read_devices()
        if not devices:
            print("No devices found in database!", flush=True)
            time.sleep(interval)
            continue

        # Read existing CSV
        existing = read_existing_csv()

        # Ping devices and update existing dict
        for ip, name in devices:
            status = "Online" if is_online(ip) else "Offline"
            existing[ip] = [name, status]
            # Display in System Exec console immediately
            print(f"{ip} ({name}): {status}", flush=True)

        # Write updated CSV
        write_csv(existing)

        # Wait before next loop
        time.sleep(interval)

except KeyboardInterrupt:
    print("Ping monitoring stopped by user.", flush=True)
