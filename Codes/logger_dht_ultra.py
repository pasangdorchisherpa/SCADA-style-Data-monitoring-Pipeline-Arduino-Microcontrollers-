import serial
import csv
from datetime import datetime
import time

PORT = "COM3"
BAUD = 9600
CSV_FILE = "sensor_log.csv"

def open_serial():
    return serial.Serial(PORT, BAUD, timeout=2)

def main():
    ser = None
    while ser is None:
        try:
            ser = open_serial()
            time.sleep(2)  # Arduino resets when serial opens
        except Exception as e:
            print(f"Serial open failed: {e}. Retrying...")
            time.sleep(2)

    print("Logging... Press Ctrl+C to stop.")

    # Create file + header if empty/new
    try:
        with open(CSV_FILE, "x", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "millis", "temp_c", "hum_pct", "dist_cm"])
    except FileExistsError:
        pass

    try:
        with open(CSV_FILE, "a", newline="") as f:
            writer = csv.writer(f)

            while True:
                line = ser.readline().decode(errors="ignore").strip()
                if not line:
                    continue

                if line == "ERROR":
                    # optional: log an error row
                    print("Sensor ERROR line received")
                    continue

                parts = line.split(",")
                if len(parts) != 4:
                    # ignore malformed lines
                    continue

                try:
                    ms = int(parts[0])
                    temp = float(parts[1])
                    hum = float(parts[2])
                    dist = int(float(parts[3]))  # handles "-1" or "12.0"
                except ValueError:
                    continue

                ts = datetime.now().isoformat(timespec="seconds")
                writer.writerow([ts, ms, temp, hum, dist])
                f.flush()  # ensures data is actually written

                print(f"{ts}  T={temp:.1f}C  H={hum:.1f}%  D={dist}cm")

    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        try:
            ser.close()
        except:
            pass

if __name__ == "__main__":
    main()
