// === Pin Definitions ===
const int micPin = A0;              // Analog pin for microphone output
const int ledPin = 13;              // Optional: LED to indicate sound detection

// === Variables ===
int micValue;                       // Raw analog reading from microphone
float voltage;                      // Converted voltage value
int soundLevel;                     // Processed sound level (0-100)
int threshold = 512;                // Sound detection threshold (adjust as needed)

// === Calibration Variables ===
int minSound = 1024;                // Minimum sound level detected
int maxSound = 0;                   // Maximum sound level detected
bool calibrationMode = true;        // Set to false to disable auto-calibration
unsigned long calibrationTime = 10000; // 10 seconds for calibration
unsigned long startTime;

void setup() {
  Serial.begin(9600);               // Initialize serial communication
  pinMode(micPin, INPUT);           // Set microphone pin as input
  pinMode(ledPin, OUTPUT);          // Optional: set LED pin as output
  
  startTime = millis();
  
  Serial.println("MAX4466 Microphone Sensor Initialized");
  Serial.println("Pin Configuration:");
  Serial.print("  Microphone (OUT): A");
  Serial.println(micPin - A0);
  Serial.println("  GND: Ground");
  Serial.println("  VCC: 5V or 3.3V");
  Serial.println();
  
  if (calibrationMode) {
    Serial.println("Calibration Mode: ON");
    Serial.println("Make some noise for 10 seconds to calibrate...");
    Serial.println("-----");
  }
}

void loop() {
  // Read microphone value
  micValue = analogRead(micPin);
  
  // Convert to voltage (0-5V range)
  voltage = micValue * (5.0 / 1023.0);
  
  // Auto-calibration for first 10 seconds
  if (calibrationMode && (millis() - startTime < calibrationTime)) {
    if (micValue < minSound) minSound = micValue;
    if (micValue > maxSound) maxSound = micValue;
    
    // Show calibration progress every second
    if ((millis() - startTime) % 1000 < 50) {
      Serial.print("Calibrating... Min: ");
      Serial.print(minSound);
      Serial.print(", Max: ");
      Serial.print(maxSound);
      Serial.print(", Current: ");
      Serial.println(micValue);
    }
    
    delay(50);
    return;
  }
  
  // End calibration and set threshold
  if (calibrationMode && (millis() - startTime >= calibrationTime)) {
    calibrationMode = false;
    threshold = minSound + ((maxSound - minSound) * 0.3); // 30% above minimum
    Serial.println("Calibration Complete!");
    Serial.print("Threshold set to: ");
    Serial.println(threshold);
    Serial.println("-----");
  }
  
  // Map sound level to 0-100 scale
  soundLevel = map(micValue, minSound, maxSound, 0, 100);
  soundLevel = constrain(soundLevel, 0, 100);
  
  // Display readings
  Serial.print("Raw Value: ");
  Serial.print(micValue);
  Serial.print(" | Voltage: ");
  Serial.print(voltage, 2);
  Serial.print("V | Sound Level: ");
  Serial.print(soundLevel);
  Serial.print("%");
  
  // Sound detection
  if (micValue > threshold) {
    Serial.print(" | SOUND DETECTED!");
    
    // Optional: Turn on LED when sound is detected
    digitalWrite(ledPin, HIGH);
  } else {
    Serial.print(" | Quiet");
    
    // Optional: Turn off LED when quiet
    digitalWrite(ledPin, LOW);
  }
  
  Serial.println();
  
  delay(100); // Small delay for readable output
} 