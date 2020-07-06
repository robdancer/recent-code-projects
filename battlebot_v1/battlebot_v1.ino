/* BattleBot Code Version 1
 * By Robert Dancer
 * 
 * Pins:
 * 0 RX
 * 1 TX
 * 2 PS2 DAT
 * 3 SERVO
 * 4 PS2 CMD
 * 5 MOTOR ENA
 * 6 MOTOR ENB
 * 7 MOTOR IN1
 * 8 MOTOR IN2
 * 9 MOTOR IN3
 * 10 PS2 SEL
 * 11 MOTOR IN4
 * 12 IR RECV
 * 13 PS2 CLK
 */

#include <IRremote.h>
#include <Servo.h>
#include <PS2X_lib.h>

// IR key codes
#define f 16736925 // FORWARD
#define b 16754775 // BACK
#define l 16720605 // LEFT
#define r 16761405 // RIGHT
#define s 16712445 // STOP
#define KEY1 16738455 // NUMPAD 1
#define KEY2 16750695 // NUMPAD 2
#define KEY_STAR 16728765 // STAR
#define KEY_HASH 16732845 // HASH

// IR reciever pin
#define RECV_PIN 12

// Ultrasonic sensor pins
#define ECHO_PIN A4
#define TRIG_PIN A5
//const int ObstacleDetection = 35;

// Motor drive module pins
#define ENA 5
#define ENB 6
#define IN1 7
#define IN2 8
#define IN3 9
#define IN4 11

// PS2 connection pins
#define PS2_DAT 2
#define PS2_CMD 4
#define PS2_SEL 10
#define PS2_CLK 13

// Servo pin
#define SERVO_PIN 3

#define CAR_SPEED 250 // Maximum car speed... 255 is the limit, so 250 for safety
#define DEBUG_MODE false;

Servo servo;
IRrecv irrecv(RECV_PIN);
PS2X ps2x;

int error = 0;
byte type = 0;
int left_y = 128;
int right_y = 128;
unsigned int distance = 0;
int servoAngle = 90;

// Get ultrasonic sensor distance
unsigned int getDistance(void)
{ //Getting distance
  unsigned int dist = 0;
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  dist = ((unsigned int)pulseIn(ECHO_PIN, HIGH) / 58);
  return dist;
}

void setup(void)
{
  Serial.begin(9600); // Set baud rate to 9600
  servo.attach(SERVO_PIN);
  servo.write(90);

  pinMode(ECHO_PIN, INPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);

  delay(300);
  error = ps2x.config_gamepad(PS2_CLK, PS2_CMD, PS2_SEL, PS2_DAT, false, true);
  if(DEBUG_MODE) {
    if(error == 0)
      Serial.println("Controller connected");
    else if(error == 1)
      Serial.println("No controller found");
    else if(error == 2)
      Serial.println("Controller found but not accepting commands");
    else if(error == 3)
      Serial.println("This error should never occur... make sure pressures mode is off I guess");
  }
  type = ps2x.readType();
  if(DEBUG_MODE) {
    Serial.print("Controller type: ");
    switch(type) {
      case 0:
        Serial.println("Unknown");
        break;
      case 1:
        Serial.println("DualShock Controller");
        break;
      case 2:
        Serial.println("GuitarHero Controller");
        break;
      case 3:
        Serial.println("Wireless Sony DualShock Controller");
        break;
    }
  }
}

void loop(void)
{
  if(error == 1) // No controller connected
    return; 
  else if(type == 2){ //Guitar Hero controller connected
    if(DEBUG_MODE)
      Serial.println("Guitar Hero controller? Seriously dude? Nobody uses them. There's either a problem with the Arduino or a problem with your brain.");
    return;
  } else { //DualShock controller
    distance = getDistance();
    if(DEBUG_MODE) {
      Serial.print("DISTANCE: ");
      Serial.print(getDistance());
    }
    if(distance < 32) {
      ps2x.read_gamepad(false, 255-distance*8); // Read controller inputs, rumble
    } else {
      ps2x.read_gamepad(false, 0); // Read controller inputs, no rumble
    }
    left_y = ps2x.Analog(PSS_LY); // Get left stick y
    right_y = ps2x.Analog(PSS_RY); // Get right stick y

    /* Remember:
     * Y=0: STICK UP
     * Y=128: STICK NEUTRAL
     * Y=255: STICK DOWN
     */

    if(DEBUG_MODE) {
      Serial.println("Y VALUES:");
      Serial.println(left_y);
      Serial.println(right_y);
    }
    
    if(left_y < 120 ) { // Left stick up
      analogWrite(ENA, CAR_SPEED*(128 - left_y)/128);
      digitalWrite(IN1, HIGH);
      digitalWrite(IN2, LOW);
      if(DEBUG_MODE)
        Serial.println("LEFT FWD");
    } else if(left_y > 136) { // Left stick down
      analogWrite(ENA, CAR_SPEED*(left_y - 128)/128);
      digitalWrite(IN1, LOW);
      digitalWrite(IN2, HIGH);
      if(DEBUG_MODE)
        Serial.println("LEFT BWD");
    } else { // Left stick neutral
      digitalWrite(ENA, LOW);
    }
    if(right_y < 120) { // Right stick up
      analogWrite(ENB, CAR_SPEED*(128 - right_y)/128);
      digitalWrite(IN3, LOW);
      digitalWrite(IN4, HIGH);
      if(DEBUG_MODE)
        Serial.println("RIGHT FWD");
    } else if(right_y > 136) { // Right stick down
      analogWrite(ENB, CAR_SPEED*(right_y - 128)/128);
      digitalWrite(IN3, HIGH);
      digitalWrite(IN4, LOW);
      if(DEBUG_MODE)
        Serial.println("RIGHT BWD");
    } else { // Right stick neutral
      digitalWrite(ENB, LOW);
    };
    if(ps2x.ButtonPressed(PSB_R1) && (servoAngle > 10)) {
      servoAngle -= 5;
      servo.write(servoAngle);
    } else if(ps2x.ButtonPressed(PSB_L1) && (servoAngle < 170)) {
      servoAngle += 5;
      servo.write(servoAngle);
    } else if(ps2x.ButtonPressed(PSB_TRIANGLE)) {
      servoAngle = 90;
      servo.write(servoAngle);
    }
  }
  delay(50); 
}
