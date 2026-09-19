import os
import sys
import time
import json
import httpx
import serial
import serial.tools.list_ports

def get_target_api_url() -> str:
    """
    Determine target API endpoint for ESP32 hardware telemetry.
    Priority:
    1. AQUASENTINEL_API_BASE_URL or API_BASE_URL env var (e.g. https://aquasentinel-api-r00y.onrender.com)
    2. API_URL env var
    3. Default local fallback: http://localhost:8000/api/hardware/telemetry
    """
    base = os.getenv("AQUASENTINEL_API_BASE_URL") or os.getenv("API_BASE_URL")
    if base:
        base = base.rstrip("/")
        if not base.endswith("/api"):
            return f"{base}/api/hardware/telemetry"
        return f"{base}/hardware/telemetry"

    raw_api_url = os.getenv("API_URL")
    if raw_api_url:
        return raw_api_url

    return "http://localhost:8000/api/hardware/telemetry"

API_URL = get_target_api_url()
BAUD_RATE = int(os.getenv("ESP32_BAUD_RATE", 115200))
ENV_PORT = os.getenv("ESP32_SERIAL_PORT")
HARDWARE_TOKEN = os.getenv("AQUASENTINEL_HARDWARE_TOKEN") or os.getenv("HARDWARE_INGEST_TOKEN")

def find_esp32_port():
    """
    Find COM / serial port for ESP32.
    Priority:
    1. ESP32_SERIAL_PORT environment variable (e.g., COM15, COM3, /dev/ttyUSB0)
    2. Auto-detection searching port descriptions for USB/CP210/CH340/FTDI/UART
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

        if any(keyword in desc or keyword in hardware_id for keyword in ["CH340", "CP210", "FTDI", "USB SERIAL", "UART"]):
            print(f"[BRIDGE] Auto-detected ESP32 serial candidate: {p.device}")
            return p.device

    fallback_port = ports[0].device
    print(f"[BRIDGE] Defaulting to first available port: {fallback_port}")
    return fallback_port


def run_bridge():
    print("=" * 60)
    print("  AquaSentinel ESP32 Serial Telemetry Bridge  ")
    print("=" * 60)
    print(f"[BRIDGE] Target API Endpoint: {API_URL}")
    print(f"[BRIDGE] Baud Rate          : {BAUD_RATE}")
    if HARDWARE_TOKEN:
        print("[BRIDGE] Ingest Token       : Configured (sending authentication header)")
    else:
        print("[BRIDGE] Ingest Token       : None (open hackathon ingest mode)")

    headers = {}
    if HARDWARE_TOKEN:
        headers["X-Hardware-Token"] = HARDWARE_TOKEN
        headers["Authorization"] = f"Bearer {HARDWARE_TOKEN}"

    client = httpx.Client(timeout=5.0, headers=headers)

    while True:
        port_name = find_esp32_port()
        if not port_name:
            print("[BRIDGE] Warning: No active serial ports found. Retrying in 3 seconds...")
            time.sleep(3)
            continue

        try:
            print(f"[BRIDGE] Connecting to ESP32 on {port_name} at {BAUD_RATE} baud...")
            ser = serial.Serial(port_name, BAUD_RATE, timeout=2.0)
            time.sleep(1.5)  # Allow DTR reset to settle
            print(f"[BRIDGE] Connected to ESP32 on {port_name} at {BAUD_RATE} baud")
            print("[BRIDGE] Listening for newline-delimited telemetry JSON...")

            while True:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if not line:
                        continue

                    # Filter out non-JSON boot messages or debug lines
                    if not (line.startswith('{') and line.endswith('}')):
                        continue

                    data = json.loads(line)

                    raw_val = data.get("raw_value", 0)
                    press_eq = data.get("pressure_equivalent", 0.0)
                    status = data.get("status", "UNKNOWN")

                    log_tag = "[ALERT!]" if status == "ALERT" else "[OK]"
                    print(f"[BRIDGE] {log_tag} Telemetry packet received from {port_name}: raw_value={raw_val}, pressure_eq={press_eq}, status={status}")

                    # POST telemetry to target API (local or remote Render URL)
                    try:
                        res = client.post(API_URL, json=data)
                        if res.status_code == 200:
                            print(f"[BRIDGE] Telemetry sent: raw_value={raw_val}, status={status}, http_code=200")
                        else:
                            print(f"[BRIDGE] HTTP error {res.status_code}: {res.text[:100]}")
                    except httpx.HTTPError as he:
                        print(f"[BRIDGE] HTTP transport error sending telemetry to {API_URL}: {he}")

                except json.JSONDecodeError:
                    print(f"[BRIDGE] Parse Warning: Skipped non-JSON line: '{line}'")
                except serial.SerialException as se:
                    print(f"[BRIDGE] Serial error on {port_name}: {se}. Re-connecting...")
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
