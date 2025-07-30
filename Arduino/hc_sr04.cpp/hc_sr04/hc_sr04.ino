// === Pin Definitions ===
const int trigPin = 9;
const int echoPin = 8;
const int buzzerPin = 6; // Optional: comment this line if you don't use a buzzer

// === Variables ===
long duration;
float distanceCm;

void setup() {
  Serial.begin(9600);                // Initialize serial communication
  pinMode(trigPin, OUTPUT);         // Set trigger pin as output
  pinMode(echoPin, INPUT);          // Set echo pin as input
  pinMode(buzzerPin, OUTPUT);       // Optional: set buzzer pin
}

void loop() {
  Serial.println("Starting measurement...");

  // Clear the trigger
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  Serial.println("Trigger LOW");

  // Send trigger pulse
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  Serial.println("Trigger pulse sent");

  // Measure echo duration
  duration = pulseIn(echoPin, HIGH, 30000); // 30ms timeout
  Serial.print("Duration: ");
  Serial.println(duration);

  if (duration == 0) {
    Serial.println("Warning: No echo received (timeout).");
  } else {
    distanceCm = duration * 0.034 / 2;
    Serial.print("Distance: ");
    Serial.print(distanceCm);
    Serial.println(" cm");

    // Optional: Sound buzzer if object is closer than 20 cm
    if (distanceCm < 20) {
      Serial.println("Beep! Object is close.");
      tone(buzzerPin, 1000);  // 1kHz tone
      delay(200);
      noTone(buzzerPin);
    }
  }

  Serial.println("-----");
  delay(1000);
}