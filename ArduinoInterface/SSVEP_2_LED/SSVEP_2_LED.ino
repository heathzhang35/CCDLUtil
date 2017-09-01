// Witten May 11, 2017 - Written to be used with the Arduino2LightInterface.py file in CCDLUtil

// For convetion, LED3 should always be the LEFT light.

// "Pins 0 and 1 are used for serial communications. It's really not possible to use pins 0 and 1 for external circuitry 
//    and still be able to utilize serial communications or to upload new sketches to the board."

const int LED3 = 6;  // Shown on the case as slot 3
const int LED4 = 7;  // // Shown on the case as slot 4

// Messages we can send to the board
const unsigned char NO_MSG = 0;
const unsigned char BOTH_ON_MSG = 1;
const unsigned char BOTH_OFF_MSG = 2;
const unsigned char LIGHT_3_ACTIVATE_MSG = 3;
const unsigned char LIGHT_4_ACTIVATE_MSG = 4;
const unsigned char LIGHT_3_DEACTIVATE_MSG = 5;
const unsigned char LIGHT_4_DEACTIVATE_MSG = 6;

// Values used in 20 Questions experiment:
// 38 = Yes = 13 Hz = Left side of screen
// 42 = No = 12 Hz = Right side of screen
// 500 = 1 Hz for testing

// Other values:
// 5 Hz = 100
// 7 Hz = 71
// 11 Hz = 
// 13 Hz = 38
// 17 Hz = 29


// Interval that the light remains on (and off) when blinking in ms.  For example if set to 500, the light would be on for 500 ms, then off for 500 ms, flashing at 1 hz.
const unsigned long LED3_interval = 29;  // Left light
const unsigned long LED4_interval = 71;     // Right light

unsigned long LED3_time;
unsigned long LED4_time;
unsigned char LED3_on;
unsigned char LED4_on;

unsigned char msg;  // place holder for the byte we will take in in order to control the light
unsigned char light3_active;  // Is the light active? This is our flag to tell.
unsigned char light4_active;

void setup () {
  msg = 1;  // 2 --Default to all off (1 is both on; 2 is both off)
  Serial.begin(9600);
  pinMode (LED3, OUTPUT);
  pinMode (LED4, OUTPUT);
  LED3_time = millis ();
  LED4_time = millis ();
  LED3_on = 0;  // This flag is to denote whether the light is *currently on*
  LED4_on = 0;
  light3_active = 0; // This flag is to denote whether the light is currently blinking.
  light4_active = 0;
  
}

void turn_off_LED3 (){
   if (LED3_on == 1) {
      digitalWrite (LED3, LOW);
      LED3_on = 0;
   }
}

void turn_off_LED4 (){
   if (LED4_on == 1) {
      digitalWrite (LED4, LOW);
      LED4_on = 0;  
   }
}


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
  
 void toggle_LED4 (){
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
  while (Serial.available() > 0){
    msg = Serial.read();
    delay(200);
    msg = msg - 48;
    Serial.print(msg);
  }
  
  if (msg == BOTH_ON_MSG) {
    // If we get the high both message and either of our lights are off
    light3_active = 1;
    light4_active = 1;
  } else if (msg == BOTH_OFF_MSG) {
    // If we get the low both message, we need to set our flags *and* turn off both lights
    light3_active = 0;
    light4_active = 0;
    turn_off_LED3();
    turn_off_LED4();
  } else if (msg == LIGHT_3_ACTIVATE_MSG) {
    // If we get the message high 3, we need to activate light 3
    light3_active = 1;
  } else if (msg == LIGHT_4_ACTIVATE_MSG) {
    // If we get the message high 3, we need to activate light 3
    light4_active = 1;
  } else if (msg == LIGHT_3_DEACTIVATE_MSG) {
    // If we get the message low 3, we need to turn off light 3 and deactivate light 3
    light3_active = 0;
    turn_off_LED3();
  } else if (msg == LIGHT_4_DEACTIVATE_MSG) {
    // If we get the message low 4, we need to turn off light 4 and deactivate
    light4_active = 0;
    turn_off_LED4();
  }
  msg = NO_MSG;  // Reset our message so we don't continually go into the if/else branches

  // Toggle the lights
  if (light3_active == 1) {
    if (millis () - LED3_time >= LED3_interval) {
      toggle_LED3();
    }
  }
  if (light4_active == 1) {
    if (millis () - LED4_time >= LED4_interval) {
      toggle_LED4();
    }
  }
}
