import csv
import os
import time
import datetime
import serial.tools.list_ports

# Paths (use raw strings to avoid escape issues)
csv_file  = r"F:\Geosoil Drive\geosoil-ethernet-comport\data\serial_log.csv"
stop_file = r"F:\Geosoil Drive\geosoil-ethernet-comport\data\stop_serial.txt"

# Interval between checks (seconds)
interval = 5

# COM port to monitor -- set to None to auto-detect all ports
target_port = None  # e.g. "COM3"

CSV_HEADERS = ["timestamp", "port", "description", "status"]


def scan_ports():
    return {p.device: p.description for p in serial.tools.list_ports.comports()}


def write_csv(row):
    os.makedirs(os.path.dirname(os.path.abspath(csv_file)), exist_ok=True)
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        if not file_exists or os.path.getsize(csv_file) == 0:
            writer.writeheader()
        writer.writerow(row)


print("\n=== Serial Port Monitor ===")
print(f"  Log file : {csv_file}")
print(f"  Stop file: {stop_file}")
print(f"  Interval : {interval}s")
print(f"  Port     : {target_port or 'auto-detect all'}")
print(f"  Press Ctrl+C or create the stop file to stop.\n")

prev_status = {}

while True:
    if os.path.exists(stop_file):
        print("Stop signal detected. Exiting.", flush=True)
        os.remove(stop_file)
        break

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    detected = scan_ports()

    check_ports = [target_port] if target_port else list(detected.keys())

    if not check_ports:
        print(f"[{timestamp}]  No ports detected. Waiting...", flush=True)
        time.sleep(interval)
        continue

    for port in check_ports:
        if port in detected:
            status      = "PRESENT"
            description = detected[port]
            indicator   = "OK"
        else:
            status      = "ABSENT"
            description = "N/A"
            indicator   = "!!"

        if prev_status.get(port) != status:
            change = " (changed)" if port in prev_status else " (first check)"
            print(f"[{timestamp}]  [{indicator}] {port}  {description}  {status}{change}", flush=True)
        else:
            print(f"[{timestamp}]  [{indicator}] {port}  {description}  {status}", flush=True)

        prev_status[port] = status

        write_csv({"timestamp": timestamp, "port": port,
                   "description": description, "status": status})

    time.sleep(interval)
