# ArduinoInterace

This project is for all arduino relevant code (python, cpp, c).

See documentation/Projects/20Questions for information related to the SSVEP-TMS 20 questions project.

### Pins
As of May 11, the pins on the Arduino board are mislabeled as the labeling on the case uses 1 based indexing,
while referencing the code uses 0 based indexing.  Therefore the pin marked 1 is actually pin 0, etc.

**Do not use pins 0 and 1 if you need to communicate with the board**

"Pins 0 and 1 are used for serial communications. It's really not possible to use pins 0 and 1 for external circuitry and still be able to utilize serial communications or to upload new sketches to the board."

This response is taken from stackoverflow question:
http://stackoverflow.com/questions/43881852/using-serial-print-and-digitialwrite-in-same-arduino-script/43885201#43885201

