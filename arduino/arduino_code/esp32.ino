#include <WiFi.h>
#include <WebServer.h>

// WiFi credentials
const char* ssid     = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";

// Define ESP32 hardware serial for Arduino communication
#define ARDUINO_SERIAL Serial1  // RX/TX pins must be connected to Arduino

WebServer server(80);

// Embedded HTML without camera/sound/voice
const char* index_html = R"rawliteral(
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>H3RU Home Control System</title>
  <style>
    body { font-family: sans-serif; text-align: center; margin-top: 50px; background: #222; color: #fff; }
    button { margin: 10px; padding: 15px 25px; font-size: 16px; }
  </style>
</head>
<body>
  <h1>H3RU Home Control System</h1>
  <button onclick="location.href='/doorbell'">Doorbell</button>
  <button onclick="location.href='/open_door'">Open Door</button>
  <button onclick="location.href='/open_garage'">Open Garage</button>
</body>
</html>
)rawliteral";

void handleRoot() {
  server.send(200, "text/html", index_html);
}

void handleDoorbell() {
  ARDUINO_SERIAL.println("DOORBELL");
  server.send(200, "text/plain", "Doorbell triggered");
}

void handleOpenDoor() {
  ARDUINO_SERIAL.println("OPEN_DOOR");
  server.send(200, "text/plain", "Door opening");
}

void handleOpenGarage() {
  ARDUINO_SERIAL.println("OPEN_GARAGE");
  server.send(200, "text/plain", "Garage opening");
}

void setup() {
  Serial.begin(115200);
  // Initialize Arduino serial for ESP32 TX/RX communication
  ARDUINO_SERIAL.begin(115200);
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");

  // Start web server and define routes
  server.on("/", handleRoot);
  server.on("/doorbell", handleDoorbell);
  server.on("/open_door", handleOpenDoor);
  server.on("/open_garage", handleOpenGarage);
  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  server.handleClient();
  // ...existing code if required...
}
