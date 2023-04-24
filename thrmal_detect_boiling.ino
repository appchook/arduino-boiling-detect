#include <Wire.h>              // I2C library, required for MLX90614
#include <SparkFunMLX90614.h>  //Click here to get the library: http://librarymanager/All#Qwiic_IR_Thermometer by SparkFun

#define WINDOW_SIZE 20

#include "SteadyStateDetectorCuSum.h"
#include "BeepHandler.h"

IRTherm therm;  // Create an IRTherm object to interact with throughout
unsigned long currentMillis, previousMillis;
SteadyStateDetectorCuSum detector;
BeepHandler beepHandler;

#define BLINK_INTERVAL 1000
int buzzerPin = 16;
const int BUTTON_PIN = 14;  // the number of the pushbutton pin

void soundSetupComplete() {
  digitalWrite(buzzerPin, HIGH);
  delay(500);
  digitalWrite(buzzerPin, LOW);
}

void setup() {
  Serial.begin(9600);  // Initialize Serial to log output
  Wire.begin();        //Joing I2C bus

  if (therm.begin() == false) {  // Initialize thermal IR sensor
    Serial.println("Qwiic IR thermometer did not acknowledge! Freezing!");
    while (1)
      ;
  }
  Serial.println("Qwiic IR Thermometer did acknowledge.");

  therm.setUnit(TEMP_C);  // Set the library's units to Farenheit
  // Alternatively, TEMP_F can be replaced with TEMP_C for Celsius or
  // TEMP_K for Kelvin.

  //pinMode(LED_BUILTIN, OUTPUT); // LED pin as output

  currentMillis = millis();
  previousMillis = currentMillis;

  pinMode(buzzerPin, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  detector.init();

  soundSetupComplete();
}


void periodic()
{
  // Call therm.read() to read object and ambient temperatures from the sensor.
  if (therm.read())  // On success, read() will return 1, on fail 0.
  {
    // Use the object() and ambient() functions to grab the object and ambient
    // temperatures.
    // They'll be floats, calculated out to the unit you set with setUnit().
    Serial.println("Object: " + String(therm.object(), 2) + "C" + ". Ambient: " + String(therm.ambient(), 2) + "C");
  }

  bool updated = detector.update_state(therm.object());
  if(updated)
  {
    bool boiling = detector.get_detection();
    if(boiling) 
    {
      beepHandler.startOrContinue();
    }
    else
    {
      beepHandler.reset();
    }
  }
}


void loop() {
  // digitalWrite(LED_BUILTIN, HIGH);
  currentMillis = millis();
  if (currentMillis - previousMillis >= BLINK_INTERVAL) {
    //sevseg.setNumber(numbers[curIdx]);
    previousMillis = currentMillis;

    periodic();
  }

  beepHandler.handle(currentMillis);

  // digitalWrite(LED_BUILTIN, LOW);
  // read the state of the switch/button:
  int currentState = digitalRead(BUTTON_PIN);
  if (currentState == LOW) {
    Serial.println("pressed!");
    beepHandler.reset();
  }
}