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



### Original 20 Questions code
    int LED1 = 1;
    int LED2 = 2;
    // 38 = Yes = 13 Hz
    // 42 = No = 12 Hz
    // 500 = 1 Hz for testing
    const unsigned long LED1_interval = 500; // Interval ON (and subsequently off) in ms.  For example 500 = 1 Hz.
    const unsigned long LED2_interval = 250; // Interval between on and off in ms

    unsigned long LED1_time;
    unsigned long LED2_time;
    unsigned char LED1_on;
    unsigned char LED2_on;

    void setup () {
      pinMode (LED1, OUTPUT);
      pinMode (LED2, OUTPUT);
      LED1_time = millis ();
      LED2_time = millis ();
      LED1_on = 0;
      LED2_on = 0;
    }


     void toggle_LED1 () {
       if (LED1_on == 0) {
          digitalWrite (LED1, HIGH);
          LED1_on = 1;
       }
       else {
          digitalWrite (LED1, LOW);
          LED1_on = 0;
       }

      LED1_time = millis ();
     }

     void toggle_LED2 ()
      {
       if (LED2_on == 0) {
          digitalWrite (LED2, LOW);
          LED2_on = 1;
       }
       else {
          digitalWrite (LED2, LOW);
          LED2_on = 0;
       }
      LED2_time = millis ();
     }

    void loop ()
      {

     // Handling the blink of LED1.

        if ((millis () - LED1_time) >= LED1_interval) {
          toggle_LED1 ();
        }
        if ( (millis () - LED2_time) >= LED2_interval) {
          toggle_LED2 ();
        }
    }