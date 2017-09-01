int LED3 = 6;
int LED4 = 7;
// 38 = Yes = 13 Hz
// 42 = No = 12 Hz
// 500 = 1 Hz for testing
const unsigned long LED3_interval = 500; // Interval between on and off in ms

// 17 Hz = 29
// 13 Hz = 38
// 7 hz = 71
// 5 hz = 100
const unsigned long LED4_interval = 38; 

unsigned long LED3_time;
unsigned long LED4_time;
unsigned char LED3_on;
unsigned char LED4_on;

unsigned char LIGHTS_ON = 1;  // Set to zero and upload to turn both lights off.  Set to 1 and upload to have both lights flash.

void setup () 
  {
  pinMode (LED3, OUTPUT);
  pinMode (LED4, OUTPUT);
  LED3_time = millis ();
  LED4_time = millis ();
  LED3_on = 0;
  LED4_on = 0;
  }  // end of setup
  

void toggle_LED3 () {
   if (LED3_on == 0) {
      digitalWrite (LED3, HIGH);
      LED3_on = 1;
   }
   else {
      digitalWrite (LED3, LOW);
      LED3_on = 0;
   }

  LED3_time = millis ();  
  }
  
 void toggle_LED4 ()
  {
   if (LED4_on == 0) {
      digitalWrite (LED4, HIGH);
      LED4_on = 1;
   }
   else {
      digitalWrite (LED4, LOW);
      LED4_on = 0;
   }

  LED4_time = millis ();  
  }

void loop () {
  if (LIGHTS_ON == 1) {
    if ( (millis () - LED3_time) >= LED3_interval) {
      toggle_LED3 ();
    }
    if ( (millis () - LED4_time) >= LED4_interval) {
      toggle_LED4 ();
    }
  }  
}
