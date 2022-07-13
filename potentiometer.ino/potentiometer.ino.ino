// potentiometer.ino
// reads a potentiometer sensor and sends the reading over serial

int mfcPin = A0; // the potentiometer is connected to analog pin 0
int pressurePin = A1;
int outputPin = 5;
int sensorValue; // an integer variable to store the potentiometer reading

void setup() { // this function runs once when the sketch starts up
  // initialize serial communication :
  Serial.begin(9600);

}

void loop() { // this loop runs repeatedly after setup() finishes
  sensorValue = analogRead(pressurePin); // read the sensor
  Serial.println(sensorValue); // output reading to the serial line
  sensorValue = analogRead(mfcPin);
  Serial.println(sensorValue);

  int x = Serial.readString().toInt();
  analogWrite(outputPin, x);

  //delay (500); // Pause in milliseconds before next reading
}
