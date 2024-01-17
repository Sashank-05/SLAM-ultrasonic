#include <AFMotor.h>
#include <Servo.h>
#include <SoftwareSerial.h>

//motor init
AF_DCMotor motor1(1);
AF_DCMotor motor4(4);

SoftwareSerial master(A4, A5);

byte unit_TH = 20000;
byte unit_TV = 15000;
unsigned long prev_t = 0;
unsigned long curr_t = 0;

void setup() {
  Serial.begin(9600);  // Initialize serial communication for debugging
  master.begin(9600);  // Initialize communication with the master
  // Additional setup if needed
  move_f();
  move_s();
  turn_r();
  move_f();
  move_oneblock();
}

void loop() {
  // checking if serial is available
  if (master.available() > 0) {
    String incoming = master.readStringUntil('\n');  // we dont want to read the next line if we got them together do we?


    if (incoming.length() > 0) {
      switch (incoming.charAt(0)) {
        // to save time instead of matching whole string
        case 'm':
          if (incoming.startsWith("move_s")) {
            move_s();
          } else if (incoming.startsWith("move_f")) {
            move_f();
          } else if (incoming.startsWith("move_oneblock")) {
            move_oneblock();
          }
          break;
        case 't':
          if (incoming.startsWith("turn_r")) {
            turn_r();

          } else if (incoming.startsWith("turn_l")) {
            turn_l();
          }
          break;
        case 'b':
          if (incoming.startsWith("ble s")) {
            move_s();
          } else if (incoming.startsWith("ble f")) {
            move_f();
          } else if (incoming.startsWith("ble 1b")) {
            move_oneblock();
          }
          if (incoming.startsWith("ble r")) {
            turn_r();

          } else if (incoming.startsWith("ble l")) {
            turn_l();
          }
          break;

        // need to handle cases here
        default:
          // need to do something here
          break;
      }
    }
  }
}


void move_s() {
  Serial.println("Stop");
  motor1.run(RELEASE);
  motor4.run(RELEASE);
}

void move_f() {
  Serial.println("Forward");
  motor1.setSpeed(255);  // why is the rover going in max speed
  motor4.setSpeed(255);
  motor1.run(FORWARD);
  motor4.run(FORWARD);
}

void move_oneblock() {
  Serial.println("OneBlock");
  motor1.run(FORWARD);
  motor4.run(FORWARD);
  delay(unit_TV);
  move_s();
}

void turn_r() {
  Serial.println("Right");
  motor1.run(FORWARD);
  motor4.run(BACKWARD);
  delay(400);
  move_s();
  //  motor1.run(FORWARD);
  //  motor2.run(FORWARD);
  //  motor3.run(FORWARD);
  //  motor4.run(FORWARD);
}

void turn_l() {
  Serial.println("Left");
  motor1.run(BACKWARD);
  motor4.run(FORWARD);
  delay(500);  // correct??
  move_s();
  //  motor1.run(FORWARD);
  //  motor2.run(FORWARD);
  //  motor3.run(FORWARD);
  //  motor4.run(FORWARD);
}
