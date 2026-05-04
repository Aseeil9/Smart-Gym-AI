#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Server url should be the IP of the machine running FastAPI inside the gym network
const char* serverName = "http://192.168.1.100:8000/sensor-data/";
const int athlete_id = 1; // Assuming static ID for this specific wearable

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  
  Serial.println("Connecting to WiFi...");
  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi network with IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // Check WiFi connection status and reconnect if needed
  if(WiFi.status() != WL_CONNECTED){
    Serial.println("WiFi Disconnected. Reconnecting...");
    WiFi.disconnect();
    WiFi.reconnect();
    
    // Wait for connection
    int retries = 0;
    while(WiFi.status() != WL_CONNECTED && retries < 10) {
      delay(500);
      Serial.print(".");
      retries++;
    }
    Serial.println();
  }

  if(WiFi.status() == WL_CONNECTED){
    HTTPClient http;
    
    // Start connection
    http.begin(serverName);
    
    // Specify content-type header
    http.addHeader("Content-Type", "application/json");
    
    // Simulate reading from actual hardware sensors like MAX30102 (Heart Rate) or MPU6050 (Steps)
    float simulated_hr = random(70, 180); 
    int simulated_steps = random(0, 100);
    float simulated_cal = random(10, 50);

    // Create JSON document
    StaticJsonDocument<200> doc;
    doc["user_id"] = athlete_id;
    doc["heart_rate"] = simulated_hr;
    doc["steps"] = simulated_steps;
    doc["calories"] = simulated_cal;
    
    String jsonOutput;
    serializeJson(doc, jsonOutput);
    
    // Send HTTP POST request
    int httpResponseCode = http.POST(jsonOutput);
    
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);
    if(httpResponseCode > 0) {
      String response = http.getString();
      Serial.println(response);
    }
    
    http.end();
  }
  else {
    Serial.println("WiFi Disconnected");
  }
  // Send data every 5 seconds for real-time monitoring
  delay(5000);
}
