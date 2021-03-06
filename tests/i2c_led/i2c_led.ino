#include <FastLED.h>
#include <Wire.h>

#define NUM_LEDS 148
#define LED_PIN 11

CRGB leds[NUM_LEDS];

#define I2C_ADDRESS 8

# define DEBUG false

void setup() {
  FastLED.setMaxPowerInVoltsAndMilliamps(5, 1000);
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

  leds[143] = CRGB::Red;
  leds[144] = CRGB::Green;
  leds[145] = CRGB::Blue;
  leds[146] = CRGB::Red;
  leds[147] = CRGB::Green;
  
  if (DEBUG) Serial.begin(9600);

  Wire.begin(I2C_ADDRESS);                // join i2c bus with address #1
  Wire.onReceive(receiveEvent); // register event
}

int i, pixel;
bool firstKey = true;

// function that executes whenever data is received from master on i2c
void receiveEvent() {
  i = 0;
  
  while (Wire.available() > 0) {
    if (i > 0 && Wire.available() >= 4) {
      pixel = Wire.read();
      leds[pixel][0] = Wire.read();
      leds[pixel][1] = Wire.read();
      leds[pixel][2] = Wire.read();
      
      i += 4;
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
