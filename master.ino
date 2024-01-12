#include <QMC5883LCompass.h>
#include <Wire.h>
#include <SoftwareSerial.h>
#include <NewPing.h>
#include <Servo.h>

#define TRIGGER_PIN 5
#define ECHO_PIN_1 10
#define ECHO_PIN_2 12
#define ECHO_PIN_3 11
#define ECHO_PIN_4 13
#define iled 4

enum Movement {
  STOP = 0,
  FORWARD = 1,
  BACKWARD = 2,
  RIGHT_90 = 3,
  LEFT_90 = 4
};

SoftwareSerial BLESerial(2, 3);
SoftwareSerial slave(A0, A1);
QMC5883LCompass compass;
NewPing sonar1(TRIGGER_PIN, ECHO_PIN_1);
NewPing sonar2(TRIGGER_PIN, ECHO_PIN_2);
NewPing sonar3(TRIGGER_PIN, ECHO_PIN_3);
// NewPing sonar4(TRIGGER_PIN, ECHO_PIN_4);

int deg = 30;
int back = false;
int firstwall = true;
int mapping = true;
int i = 1;
byte unit_TH = 20000;
byte unit_TV = 15000;
byte l = 0, b = 0, r = 0;
byte base_size = 0;

int s1 = 0, s2 = 0, s3 = 0, s4 = 0;
byte i1 = 0, i2 = 0, i3 = 0, i4 = 0;

unsigned long prev_t = 0;
unsigned long curr_t = 0;

void scanenv() {
  // update variables globally
  delay(60);
  s1 = sonar1.ping_cm();
  delay(60);
  s2 = sonar2.ping_cm();
  delay(60);
  s3 = sonar3.ping_cm();
  //delay(60);
  // s4 = 0

  //i1 = digitalRead(6);
  //i2 = digitalRead(7);
  //i3 = digitalRead(8);
  //i4 = digitalRead(9);

  compass.read();
}

int getheading(int azimuth) {
  return (azimuth < 0) ? 360 - abs(azimuth) : azimuth;
}

void movealign() {
  int SPTW[2] = { 100, 0 };  // {max, north}
  float head = getheading(compass.getAzimuth());
  byte first = true;

  do {
    //drive(STOP);
    delay(100);
    scanenv();
    int curr_head = getheading(compass.getAzimuth());
    scanenv();
    delay(100);
    //drive(100, -100);

    if (s2 == 0 || s3 == 0) {
      BLESerial.println("FOUND WALL");
      break;
    }

    if (s1 <= SPTW[1]) {
      compass.read();
      SPTW[0] = getheading(compass.getAzimuth());
      SPTW[1] = s1;
      //drive(STOP);
    }

    String sensorData = String(s1) + " " + String(s2) + " " + String(s3) + " " + String(0) + " " + String(digitalRead(6)) + " " + String(digitalRead(7)) + " " + String(digitalRead(8)) + " " + String(digitalRead(9)) + " " + String(head);

    BLESerial.println(sensorData);
    Serial.println(sensorData);
    if (first) {
      delay(1000);
    }
    delay(100);
  } while (head != getheading(compass.getAzimuth()));

  //drive(STOP);

  if (SPTW[1] < 20) {
    Serial.println("Very close to wall");
  } else {
    while (compass.getAzimuth() != SPTW[0]) {
      //drive(100, -100);
    }
    //drive(STOP);

    do {
      // drive(FORWARD);
    } while (sonar1.ping_cm() > 10);

    // drive(STOP);

    BLESerial.println("moved");

    compass.read();
    head = getheading(compass.getAzimuth());
    uint8_t s1 = sonar1.ping_cm();
    uint8_t s2 = sonar2.ping_cm();
    uint8_t s3 = sonar3.ping_cm();
    Movement todo;
    uint8_t c;
    if (s2 > s3) {
      todo = RIGHT_90;
      c = 90;
    } else if (s3 > s2) {
      todo = LEFT_90;
      c = -90;
    } else {
      todo = RIGHT_90;
      c = 90;
    }
    do {
      //drive(todo);
      compass.read();
    } while (head != compass.getAzimuth() + c);
    BLESerial.println("aligned");
    delay(200);
  }
}

void setup() {
  Serial.begin(9600);
  BLESerial.begin(9600);
  slave.begin(9600);
  compass.init();
  compass.read();
  pinMode(iled, OUTPUT);
  String connection = "";
  BLESerial.println("ok");

  /* Wait for connection acknowledgment
  while (connection != "yes") {
    if (BLESerial.available()) {
      connection = BLESerial.readStringUntil('\n');
    }
  }
  BLESerial.println("doneinit");  // only if doneinit is sent python should start taking values
  delay(2000); */
}

void loop() {
  digitalWrite(iled, HIGH);
  compass.read();
  int head = getheading(compass.getAzimuth());

  scanenv();
  if (s1 > 15) {
    move_s();
  }

  if (BLESerial.available() > 0) {
      String incoming = BLESerial.readStringUntil("\n");
      if (incoming == "control"){
        mapping = false;
      } 
      else if (incoming = "mapping"){
        mapping = true;
      }
    }

  if (mapping) {
    Serial.println("I is: ");
    Serial.println(i);
    l = 0;
    b = 0;
    r = 0;
    if (readUS() > 15) {
      if (i % 2 != 0) {
        prev_t = millis();
        while (readUS() > 15) {
          Serial.println("Inside 1");
          sendscan();
          move_f();
          move_oneblock();
        }
      } else {
        sendscan();
        if (i % 4 != 0) {
          sendscan();
          turn_r();
          move_oneblock();
          sendscan();
          if (look_l() > 20) {
            sendscan();
            turn_l();
            prev_t = millis();
            while (readUS() > 10) {
              Serial.println("Inside 2");
              sendscan();
              move_f();
              move_oneblock();
            }
            curr_t = millis();
            l = (curr_t - prev_t) / unit_TH;
            sendscan();
            turn_r();
            Serial.println("Inside 3");
            sendscan();
            move_f();
            move_oneblock();
            delay(curr_t - prev_t);
          }
          turn_r();
          i++;
        } else {
          turn_l();
          sendscan();
          move_oneblock();
          if (look_r() > 20) {
            turn_r();
            prev_t = millis();
            while (readUS() > 10) {
              Serial.println("Inside 4");
              sendscan();
              move_f();
              move_oneblock();
            }
            curr_t = millis();
            r = (curr_t - prev_t) / unit_TH;
            turn_l();
            sendscan();
            Serial.println("Inside 5");
            move_f();
            move_oneblock();
            delay(curr_t - prev_t);
          }
          turn_l();
          i++;
        }
      }
    } else {
      move_s();
      curr_t = millis();
      b = (curr_t - prev_t) / unit_TH;
      i++;
      if (look_r() > 20) {
        turn_r();
      }
    }
  } else if (!mapping) {
    // Different logic for path planning and control of bot from server
    // The data from BLE is directly sent to slave for other processing because we dont have enough
    // processing space and storage for variables + Also decreases our work because we can directly communicate to motors
    if (BLESerial.available() > 0) {
      String incoming = BLESerial.readString();
      slave.println("BLE " + incoming);
    }
  }

  String sensorData = String(s1) + " " + String(s2) + " " + String(s3) + " " + String(s4) + " " + String(i1) + " " + String(i2) + " " + String(i3) + " " + String(i4) + " " + String(head) + " " + String(deg);

  Serial.println(sensorData);
  BLESerial.println(sensorData);
  // slave.println("S " + String(deg) + "\n");
  slave.println("C " + String(head));

  if (slave.available() > 0) {
    String incoming = slave.readString();
  }

  digitalWrite(iled, LOW);
}

int readUS() {
  scanenv();
  return s1;
}

int look_r() {
  scanenv();
  return s3;
}

int look_l() {
  scanenv();
  return s2;
}

void move_s() {
  slave.println("move_s");
}

void move_f() {
  slave.println("move_f");
  BLESerial.println("MF");
  BLESerial.println("MF");
  BLESerial.println("MF");
}

void move_oneblock() {
  slave.println("move_oneblock");
  BLESerial.println("MF");
}

void turn_r() {
  slave.println("turn_r");
}

void turn_l() {
  slave.println("turn_l");
}


void sendscan() {
  scanenv();
  int head = getheading(compass.getAzimuth());
  String sensorData = String(s1) + " " + String(s2) + " " + String(s3) + " " + String(s4) + " " + String(i1) + " " + String(i2) + " " + String(i3) + " " + String(i4) + " " + String(head) + " " + String(deg);

  Serial.println(sensorData);
  BLESerial.println(sensorData);
}
