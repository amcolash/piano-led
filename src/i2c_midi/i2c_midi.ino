#include "MIDIUSB.h"
#include <Wire.h>

#define DEBUG false

#define I2C_ADDRESS 8

void setup() {  
  if (DEBUG) Serial.begin(9600);

  Wire.begin(I2C_ADDRESS);        // join i2c bus with address #8
  Wire.onReceive(receiveEvent);   // register event
}

// function that executes whenever data is received from master on i2c
void receiveEvent() {
  int i = 0;
  
  while (Wire.available() > 0) {
    if (i != 0 && Wire.available() >= 3) {
      byte channel = Wire.read();
      byte note = Wire.read();
      byte velocity = Wire.read();
      
      noteOn(channel, note, velocity);
      MidiUSB.flush();

      i += 3;
    } else {
      Wire.read();
      i++;
    }
  }
}

void noteOn(byte channel, byte pitch, byte velocity) {
  midiEventPacket_t noteOn = {0x09, 0x90 | channel, pitch, velocity};
  MidiUSB.sendMIDI(noteOn);
}

void noteOff(byte channel, byte pitch, byte velocity) {
  midiEventPacket_t noteOff = {0x08, 0x80 | channel, pitch, velocity};
  MidiUSB.sendMIDI(noteOff);
}

void loop() {
  delay(1);
}
