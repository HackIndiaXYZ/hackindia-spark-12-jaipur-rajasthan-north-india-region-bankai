/*
  AquaSentinel ESP32 FSR402 Hardware Telemetry Firmware
  -----------------------------------------------------
  Hardware:
  - FSR402: one side to 3.3V, other side to GPIO34 + 10k resistor to GND
  - Buzzer: VCC to 3.3V, GND to GND, signal to GPIO32

  Serial:
  - 115200 baud
  - newline-delimited JSON
*/

#include <Arduino.h>

const int FSR_PIN = 34;
const int BUZZER_PIN = 32;

const int ALERT_THRESHOLD = 50;
const unsigned long TELEMETRY_INTERVAL_MS = 500;

const char* DEVICE_ID = "AQUA-ESP32-001";
const char* SENSOR_ID = "FSR-P01";
const char* ZONE_ID = "Zone_B";

unsigned long lastTelemetryTime = 0;

void setup() {
  Serial.begin(115200);

  pinMode(FSR_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  noTone(BUZZER_PIN);

  delay(1000);
}

void loop() {
  unsigned long currentMillis = millis();

  int rawValue = analogRead(FSR_PIN);

  float pressureEquivalent =
      map(rawValue, 0, 4095, 0, 1000) / 10.0;

  bool isAlert = (rawValue >= ALERT_THRESHOLD);
  const char* status = isAlert ? "ALERT" : "NORMAL";

  // Physical buzzer
  if (isAlert) {
    tone(BUZZER_PIN, 2500);
  } else {
    noTone(BUZZER_PIN);
  }

  // Send telemetry every 500 ms
  if (currentMillis - lastTelemetryTime >= TELEMETRY_INTERVAL_MS) {
    lastTelemetryTime = currentMillis;

    Serial.print("{\"device_id\":\"");
    Serial.print(DEVICE_ID);

    Serial.print("\",\"sensor_id\":\"");
    Serial.print(SENSOR_ID);

    Serial.print("\",\"zone_id\":\"");
    Serial.print(ZONE_ID);

    Serial.print("\",\"raw_value\":");
    Serial.print(rawValue);

    Serial.print(",\"pressure_equivalent\":");
    Serial.print(pressureEquivalent, 1);

    Serial.print(",\"threshold\":");
    Serial.print(ALERT_THRESHOLD);

    Serial.print(",\"status\":\"");
    Serial.print(status);

    Serial.print("\",\"timestamp_ms\":");
    Serial.print(currentMillis);

    Serial.println("}");
  }

  delay(20);
}