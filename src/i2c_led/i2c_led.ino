#include <FastLED.h>
#include <Wire.h>

#define NUM_LEDS 144
#define LED_PIN 11

CRGB leds[NUM_LEDS];

#define I2C_ADDRESS 8

# define DEBUG false

void setup() {
  FastLED.addLeds<WS2812B, LED_PIN, GRB>(leds, NUM_LEDS);
  FastLED.clear(true);

  for (int i = 0; i < 5; i++) {
    leds[0] = CRGB::Red; 
    FastLED.show();
    delay(150);
    
    leds[0] = CRGB::Black; 
    FastLED.show();
    delay(150);
  }
  
  if (DEBUG) Serial.begin(9600);

  Wire.begin(I2C_ADDRESS);                // join i2c bus with address #1
  Wire.onReceive(receiveEvent); // register event
}

int i, pixel;
bool firstKey = true;

// function that executes whenever data is received from master on i2c
void receiveEvent() {
  i = 0;
  pixel = 0;
  
  while (Wire.available() > 0) {
    
    if (i == 0) {
      pixel = Wire.read();
      i++;

      if (DEBUG) {
        Serial.println("---");
        Serial.print("pixel: ");
        Serial.println(pixel);
      }
    } else if (Wire.available() >= 3) {
      leds[pixel][0] = Wire.read();
      leds[pixel][1] = Wire.read();
      leds[pixel][2] = Wire.read();
      
      i += 3;
    } else {
      Wire.read();
      i++;
    }
  }

  if (DEBUG) {
   Serial.println("---");
  
  for (i = 0; i < NUM_LEDS; i++) {
    Serial.print(i);
    Serial.print(": [");
    Serial.print(leds[i].r); 
    Serial.print(", ");
    Serial.print(leds[i].g);
    Serial.print(", ");
    Serial.print(leds[i].b);
    Serial.println("]");
  } 
  }
}

void loop() {
  FastLED.show();
  delay(1);
}
