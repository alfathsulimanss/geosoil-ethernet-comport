import serial
import time

# 1. Configure the serial port
# Change 'COM3' to your actual port (e.g., 'COM1', '/dev/ttyUSB0')
# Change 9600 to your device's specific baud rate
ser = serial.Serial(port='COM3', baudrate=9600, timeout=2)

try:
    if ser.is_open:
        print(f"Connected successfully to {ser.name}")
        
        # 2. Define your hex command (02 04 22 26)
        hex_command = b'\x02\x04\x22\x26'
        
        # 3. Send the command
        print(f"Sending hex command: {hex_command.hex().upper()}")
        ser.write(hex_command)
        
        # Give the device a brief moment to process and reply
        time.sleep(0.5)
        
        # 4. Read the feedback
        # in_waiting checks how many bytes are sitting in the buffer
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting)
            
            print("\n--- Feedback Received ---")
            print(f"Raw Bytes: {response}")
            print(f"Hex Format: {response.hex().upper()}")
            try:
                # Try to decode as text, just in case it replies in plain ASCII
                print(f"Text Format: {response.decode('utf-8').strip()}")
            except UnicodeDecodeError:
                print("Text Format: (Response contains non-printable binary data)")
        else:
            print("\nNo feedback received. (Check connections or if a termination character like CR/LF is needed).")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Always close the port when done
    ser.close()
    print("\n Port closed.")