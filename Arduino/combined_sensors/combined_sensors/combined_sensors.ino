// === Pin Definitions ===
// Ultrasonic Sensor (HC-SR04)
const int trigPin = 9;
const int echoPin = 8;
const int buzzerPin = 6;              // Optional: buzzer for proximity alert

// Microphone Sensor (MAX4466)
const int micPin = A0;                // Analog pin for microphone output
const int ledPin = 13;                // Optional: LED for sound detection

// === Ultrasonic Variables ===
long duration;
float distanceCm;

// === Microphone Variables ===
int micValue;                         // Raw analog reading from microphone
float voltage;                        // Converted voltage value
int soundLevel;                       // Processed sound level (0-100)
int micThreshold = 512;               // Sound detection threshold

// === Calibration Variables ===
int minSound = 1024;                  // Minimum sound level detected
int maxSound = 0;                     // Maximum sound level detected
bool calibrationMode = true;          // Set to false to disable auto-calibration
unsigned long calibrationTime = 10000; // 10 seconds for calibration
unsigned long startTime;

// === Timing Variables ===
unsigned long lastUltrasonicRead = 0;
unsigned long lastMicRead = 0;
unsigned long lastDataSend = 0;
const unsigned long ultrasonicInterval = 500;  // Read ultrasonic every 500ms
const unsigned long micInterval = 100;          // Read microphone every 100ms
const unsigned long dataSendInterval = 200;     // Send structured data every 200ms

// === Communication Settings ===
bool piMode = true;                   // Set to true for Raspberry Pi communication
bool debugMode = false;               // Set to true for human-readable debug output

void setup() {
  Serial.begin(9600);                 // Initialize serial communication
  
  // Ultrasonic sensor pins
  pinMode(trigPin, OUTPUT);           // Set trigger pin as output
  pinMode(echoPin, INPUT);            // Set echo pin as input
  pinMode(buzzerPin, OUTPUT);         // Optional: set buzzer pin
  
  // Microphone sensor pins
  pinMode(micPin, INPUT);             // Set microphone pin as input
  pinMode(ledPin, OUTPUT);            // Optional: set LED pin as output
  
  startTime = millis();
  
  if (!piMode) {
    Serial.println("=== DUAL SENSOR SYSTEM INITIALIZED ===");
    Serial.println("HC-SR04 Ultrasonic + MAX4466 Microphone");
    Serial.println();
    Serial.println("Pin Configuration:");
    Serial.println("  Ultrasonic Trigger: Pin 9");
    Serial.println("  Ultrasonic Echo: Pin 8");
    Serial.println("  Buzzer (optional): Pin 6");
    Serial.print("  Microphone (OUT): A");
    Serial.println(micPin - A0);
    Serial.println("  LED (optional): Pin 13");
    Serial.println();
  }
  
  if (calibrationMode) {
    if (!piMode) {
      Serial.println("Microphone Calibration Mode: ON");
      Serial.println("Make some noise for 10 seconds to calibrate microphone...");
      Serial.println("=========================================");
    } else {
      Serial.println("STATUS:CALIBRATING");
    }
  }
}

void loop() {
  unsigned long currentTime = millis();
  
  // Handle microphone calibration
  if (calibrationMode && (currentTime - startTime < calibrationTime)) {
    calibrateMicrophone();
    return;
  }
  
  // End calibration
  if (calibrationMode && (currentTime - startTime >= calibrationTime)) {
    calibrationMode = false;
    micThreshold = minSound + ((maxSound - minSound) * 0.3); // 30% above minimum
    
    if (!piMode) {
      Serial.println("Microphone Calibration Complete!");
      Serial.print("Threshold set to: ");
      Serial.println(micThreshold);
      Serial.println("=========================================");
      Serial.println("Starting dual sensor readings...");
      Serial.println();
    } else {
      Serial.println("STATUS:READY");
    }
  }
  
  // Read ultrasonic sensor at specified interval
  if (currentTime - lastUltrasonicRead >= ultrasonicInterval) {
    readUltrasonicSensor();
    lastUltrasonicRead = currentTime;
  }
  
  // Read microphone sensor at specified interval
  if (currentTime - lastMicRead >= micInterval) {
    readMicrophoneSensor();
    lastMicRead = currentTime;
  }
  
  // Send structured data for Raspberry Pi at specified interval
  if (piMode && (currentTime - lastDataSend >= dataSendInterval)) {
    sendStructuredData();
    lastDataSend = currentTime;
  }
  
  // Check for combined conditions (proximity + sound)
  checkCombinedConditions();
}

void calibrateMicrophone() {
  micValue = analogRead(micPin);
  
  if (micValue < minSound) minSound = micValue;
  if (micValue > maxSound) maxSound = micValue;
  
  // Show calibration progress every second
  if ((millis() - startTime) % 1000 < 50) {
    if (!piMode) {
      Serial.print("Calibrating microphone... Min: ");
      Serial.print(minSound);
      Serial.print(", Max: ");
      Serial.print(maxSound);
      Serial.print(", Current: ");
      Serial.println(micValue);
    } else {
      Serial.print("CALIBRATION:");
      Serial.print(minSound);
      Serial.print(",");
      Serial.print(maxSound);
      Serial.print(",");
      Serial.println(micValue);
    }
  }
  
  delay(50);
}

void readUltrasonicSensor() {
  // Clear the trigger
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  
  // Send trigger pulse
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  // Measure echo duration
  duration = pulseIn(echoPin, HIGH, 30000); // 30ms timeout
  
  if (duration == 0) {
    distanceCm = -1; // Invalid reading
    if (debugMode) Serial.println("ULTRASONIC: No echo received (timeout)");
  } else {
    distanceCm = duration * 0.034 / 2;
    if (debugMode) {
      Serial.print("ULTRASONIC: Distance = ");
      Serial.print(distanceCm);
      Serial.println(" cm");
    }
  }
}

void readMicrophoneSensor() {
  // Read microphone value
  micValue = analogRead(micPin);
  
  // Convert to voltage (adjust for 3.3V if needed)
  voltage = micValue * (5.0 / 1023.0); // Change to 3.3 if using 3.3V
  
  // Map sound level to 0-100 scale
  soundLevel = map(micValue, minSound, maxSound, 0, 100);
  soundLevel = constrain(soundLevel, 0, 100);
  
  if (debugMode) {
    // Display readings
    Serial.print("MICROPHONE: Level = ");
    Serial.print(soundLevel);
    Serial.print("% | Raw = ");
    Serial.print(micValue);
    
    // Sound detection
    if (micValue > micThreshold) {
      Serial.print(" | SOUND DETECTED!");
      digitalWrite(ledPin, HIGH);
    } else {
      Serial.print(" | Quiet");
      digitalWrite(ledPin, LOW);
    }
    
    Serial.println();
  } else {
    // Just handle LED for non-debug mode
    if (micValue > micThreshold) {
      digitalWrite(ledPin, HIGH);
    } else {
      digitalWrite(ledPin, LOW);
    }
  }
}

void sendStructuredData() {
  // Send data in JSON-like format for easy parsing
  Serial.print("DATA:{");
  Serial.print("\"timestamp\":");
  Serial.print(millis());
  Serial.print(",\"distance\":");
  Serial.print(distanceCm);
  Serial.print(",\"sound_level\":");
  Serial.print(soundLevel);
  Serial.print(",\"sound_raw\":");
  Serial.print(micValue);
  Serial.print(",\"sound_detected\":");
  Serial.print((micValue > micThreshold) ? "true" : "false");
  Serial.print(",\"proximity_alert\":");
  Serial.print((distanceCm > 0 && distanceCm < 20) ? "true" : "false");
  Serial.println("}");
}

void checkCombinedConditions() {
  // Example: Alert if object is close AND sound is detected
  if (distanceCm > 0 && distanceCm < 20 && micValue > micThreshold) {
    if (!piMode) {
      Serial.println("*** ALERT: Close object + Sound detected! ***");
    } else {
      Serial.println("ALERT:PROXIMITY_AND_SOUND");
    }
    
    // Sound buzzer with alternating tones
    tone(buzzerPin, 1000);
    delay(100);
    tone(buzzerPin, 1500);
    delay(100);
    noTone(buzzerPin);
  }
  
  // Example: Different alert for just proximity
  else if (distanceCm > 0 && distanceCm < 20) {
    if (piMode) {
      Serial.println("ALERT:PROXIMITY_ONLY");
    }
    tone(buzzerPin, 800);  // Lower tone for proximity only
    delay(50);
    noTone(buzzerPin);
  }
} 