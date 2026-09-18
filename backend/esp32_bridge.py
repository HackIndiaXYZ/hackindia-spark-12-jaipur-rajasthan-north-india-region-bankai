import os
import sys
import time
import json
import httpx
import serial
import serial.tools.list_ports

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000/api/hardware/telemetry")
BAUD_RATE = int(os.getenv("ESP32_BAUD_RATE", 115200))
ENV_PORT = os.getenv("ESP32_SERIAL_PORT")

def find_esp32_port():
    """
    Find COM port for ESP32.
    Priority:
    1. ESP32_SERIAL_PORT environment variable (e.g., COM15)
    2. Auto-detection by searching port descriptions for USB/CP210/CH340/FTDI
    3. Fallback to first available serial port
    """
    if ENV_PORT:
        print(f"[BRIDGE] Using configured port from environment ESP32_SERIAL_PORT={ENV_PORT}")
        return ENV_PORT

    ports = list(serial.tools.list_ports.comports())
    if not ports:
        return None

    print(f"[BRIDGE] Scanning {len(ports)} available serial port(s)...")
    for p in ports:
        desc = (p.description or "").upper()
        hardware_id = (p.hwid or "").upper()
        print(f"  - {p.device}: {p.description}")

        # Check common USB-Serial chip identifiers used on ESP32 dev boards
        if any(keyword in desc or keyword in hardware_id for keyword in ["CH340", "CP210", "FTDI", "USB SERIAL", "UART"]):
            print(f"[BRIDGE] Auto-detected ESP32 serial candidate: {p.device}")
            return p.device

    # Default fallback to first port if available
    fallback_port = ports[0].device
    print(f"[BRIDGE] Defaulting to first available port: {fallback_port}")
    return fallback_port


def run_bridge():
    print("=" * 60)
    print("  AquaSentinel ESP32 USB Serial Bridge  ")
    print("=" * 60)
    print(f"Target API Endpoint: {API_URL}")
    print(f"Baud Rate          : {BAUD_RATE}")

    client = httpx.Client(timeout=3.0)

    while True:
        port_name = find_esp32_port()
        if not port_name:
            print("[BRIDGE] Warning: No active serial ports found. Retrying in 3 seconds...")
            time.sleep(3)
            continue

        try:
            print(f"[BRIDGE] Connecting to {port_name} at {BAUD_RATE} baud...")
            ser = serial.Serial(port_name, BAUD_RATE, timeout=2.0)
            time.sleep(1.5)  # Allow DTR reset to settle
            print(f"[BRIDGE] SUCCESS: Connected to {port_name}. Listening for newline-delimited telemetry JSON...")

            while True:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if not line:
                        continue

                    # Filter out non-JSON boot messages or debug lines
                    if not (line.startswith('{') and line.endswith('}')):
                        continue

                    data = json.loads(line)

                    # Validate key fields in protocol
                    raw_val = data.get("raw_value", 0)
                    press_eq = data.get("pressure_equivalent", 0.0)
                    status = data.get("status", "UNKNOWN")

                    log_tag = "[ALERT!]" if status == "ALERT" else "[OK]"
                    print(f"[BRIDGE] {log_tag} Telemetry received: raw={raw_val}, pressure_eq={press_eq} (simulated), status={status}")

                    # POST telemetry to local FastAPI server
                    res = client.post(API_URL, json=data)
                    if res.status_code != 200:
                        print(f"[BRIDGE] API Warning ({res.status_code}): {res.text[:100]}")

                except json.JSONDecodeError:
                    print(f"[BRIDGE] Parse Warning: Skipped non-JSON line: '{line}'")
                except serial.SerialException as se:
                    print(f"[BRIDGE] Serial error: {se}. Connection lost.")
                    break

        except serial.SerialException as e:
            print(f"[BRIDGE] Failed to open {port_name}: {e}")
            print("[BRIDGE] Re-scanning in 3 seconds...")
            time.sleep(3)
        except Exception as e:
            print(f"[BRIDGE] Unexpected error: {e}")
            time.sleep(3)

if __name__ == "__main__":
    run_bridge()
