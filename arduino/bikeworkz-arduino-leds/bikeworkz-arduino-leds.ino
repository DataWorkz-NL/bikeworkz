
// starting from left to right
const int ledLefGrePin = 9;
const int ledLefYelPin = 11;
const int ledLefRedPin = 12;
const int ledCenGrePin = 5;
const int ledCenYelPin = 6;
const int ledCenRedPin = 7;
const int ledRigGrePin = 2;
const int ledRigYelPin = 3;
const int ledRigRedPin = 4;
int incomingByte;      // a variable to read incoming serial data into

const int noobArray[] = {
  ledLefGrePin,
  ledLefYelPin,
  ledLefRedPin,
  ledCenGrePin,
  ledCenYelPin,
  ledCenRedPin,
  ledRigGrePin,
  ledRigYelPin,
  ledRigRedPin
};

const String ledArray[9][2] = {
  {"ledLefGrePin", "9"},
  {"ledLefYelPin", "11"},
  {"ledLefRedPin", "12"},
  {"ledCenGrePin", "5"},
  {"ledCenYelPin", "6"},
  {"ledCenRedPin", "7"},
  {"ledRigGrePin", "2"},
  {"ledRigYelPin", "3"},
  {"ledRigRedPin", "4"}
};
const int arrayLength = 9;
//const int ledLength = sizeof(ledArray);

bool blinking = false;

void setup() {
  // initialize serial communication:
  Serial.begin(115200);
  for (int i = 0; i <= 9; i++) {
    int id = ledArray[i][1].toInt();
    pinMode(id, OUTPUT);
  }
}

void loop() {

  // see if there's incoming serial data:
  if (Serial.available() > 0) {
    // read the oldest byte in the serial buffer:
    incomingByte = Serial.read();

    int woei[arrayLength];

    switch (incomingByte) {
      case '2':
        // middle red
        woei[0] = ledLefGrePin;
        woei[1] = ledRigGrePin;
        woei[2] = ledCenRedPin;
        break;
      case 'w':
        // middle yellow
        woei[0] = ledLefGrePin;
        woei[1] = ledRigGrePin;
        woei[2] = ledCenYelPin;
        break;
      case 'q':
        // left red
        woei[0] = ledCenGrePin;
        woei[1] = ledRigGrePin;
        woei[2] = ledLefRedPin;
        break;
      case 'a':
        // left yellow
        woei[0] = ledCenGrePin;
        woei[1] = ledRigGrePin;
        woei[2] = ledLefYelPin;
        break;
      case 'd':
        // right yellow
        woei[0] = ledLefGrePin;
        woei[1] = ledCenGrePin;
        woei[2] = ledRigYelPin;
        break;
      case 'e':
        // right red
        woei[0] = ledLefGrePin;
        woei[1] = ledCenGrePin;
        woei[2] = ledRigRedPin;
        break;

      // Moves away from me - warning - green/yellow
      // left
      case 'h':
        woei[0] = ledCenGrePin;
        woei[1] = ledRigGrePin;
        woei[2] = ledLefYelPin;
        woei[3] = ledLefGrePin;
        break;
      // center
      case 'j':
        woei[0] = ledCenGrePin;
        woei[1] = ledRigGrePin;
        woei[2] = ledCenYelPin;
        woei[3] = ledLefGrePin;
        break;
      // right
      case 'k':
        woei[0] = ledCenGrePin;
        woei[1] = ledRigGrePin;
        woei[2] = ledRigYelPin;
        woei[3] = ledLefGrePin;
        break;

      // Moves closer to me (slowly) - yellow/read
      // left
      case 'y':
        woei[0] = ledCenGrePin;
        woei[1] = ledRigGrePin;
        woei[2] = ledLefYelPin;
        woei[3] = ledLefRedPin;
        break;
      // center
      case 'u':
        woei[0] = ledCenRedPin;
        woei[1] = ledRigGrePin;
        woei[2] = ledCenYelPin;
        woei[3] = ledLefGrePin;
        break;
      // right
      case 'i':
        woei[0] = ledCenGrePin;
        woei[1] = ledRigRedPin;
        woei[2] = ledRigYelPin;
        woei[3] = ledLefGrePin;
        break;

      // Moves alarmingly fast closer to me - red/blinking
      // left
      case '6':
        blinking = true;
        woei[0] = ledCenGrePin;
        woei[1] = ledRigGrePin;
        woei[2] = ledLefRedPin;
        break;
      // center
      case '7':
        blinking = true;
        woei[0] = ledCenRedPin;
        woei[1] = ledRigGrePin;
        woei[2] = ledLefGrePin;
        break;
      // right
      case '8':
        blinking = true;
        woei[0] = ledCenGrePin;
        woei[1] = ledRigRedPin;
        woei[2] = ledLefGrePin;
        break;

      case 's':
        // good state
        woei[0] = ledLefGrePin;
        woei[1] = ledCenGrePin;
        woei[2] = ledRigGrePin;
        break;
    }
    writeDigital(woei);
    memset(woei, 0, sizeof(woei));
  }
}

void writeDigital(int list[]) {
  //  int length = 0;
  int blinkingArray[arrayLength];
  memset(blinkingArray, 0, sizeof(blinkingArray));
  for (int i = 0; i <= arrayLength; i++) {
    int id = ledArray[i][1].toInt();
    
    if (inArrayInt(list, id)) {
      if (blinking) {
        blinkingArray[i] = id;
      } else {
        digitalWrite(id, HIGH);
      }
    } else {
      digitalWrite(id, LOW);
    }
  }

  if (blinking) {
    int var = 0;
    while (var <= 5) {
      digitalWrite(blinkingArray[0], HIGH);
      digitalWrite(blinkingArray[1], HIGH);
      digitalWrite(blinkingArray[2], HIGH);
      digitalWrite(blinkingArray[3], HIGH);
      digitalWrite(blinkingArray[4], HIGH);
      digitalWrite(blinkingArray[5], HIGH);
      digitalWrite(blinkingArray[6], HIGH);
      digitalWrite(blinkingArray[7], HIGH);
      digitalWrite(blinkingArray[8], HIGH);
      delay(50);
      digitalWrite(blinkingArray[0], LOW);
      digitalWrite(blinkingArray[1], LOW);
      digitalWrite(blinkingArray[2], LOW);
      digitalWrite(blinkingArray[3], LOW);
      digitalWrite(blinkingArray[4], LOW);
      digitalWrite(blinkingArray[5], LOW);
      digitalWrite(blinkingArray[6], LOW);
      digitalWrite(blinkingArray[7], LOW);
      digitalWrite(blinkingArray[8], LOW);
      delay(50);
      var ++;
    }
    blinking = false;
  }


}

bool inArrayInt(int check[], int value) {
  for (int x = 0; x <= arrayLength; x++) {
    if (value == check[x]) {
      return true;
    }
  }
  return false;
}

bool inArrayString(String check[], String value) {
  for (int x = 0; x < arrayLength; x++) {
    if (value == check[x]) {
      return true;
    }
  }
  return false;
}

/* Processing code for this example

  // Mouse over serial

  // Demonstrates how to send data to the Arduino I/O board, in order to turn ON
  // a light if the mouse is over a square and turn it off if the mouse is not.

  // created 2003-4
  // based on examples by Casey Reas and Hernando Barragan
  // modified 30 Aug 2011
  // by Tom Igoe
  // This example code is in the public domain.

  import processing.serial.*;

  float boxX;
  float boxY;
  int boxSize = 20;
  boolean mouseOverBox = false;

  Serial port;

  void setup() {
    size(200, 200);
    boxX = width / 2.0;
    boxY = height / 2.0;
    rectMode(RADIUS);

    // List all the available serial ports in the output pane.
    // You will need to choose the port that the Arduino board is connected to
    // from this list. The first port in the list is port #0 and the third port
    // in the list is port #2.
    // if using Processing 2.1 or later, use Serial.printArray()
    println(Serial.list());

    // Open the port that the Arduino board is connected to (in this case #0)
    // Make sure to open the port at the same speed Arduino is using (9600bps)
    port = new Serial(this, Serial.list()[0], 9600);
  }

  void draw() {
    background(0);

    // Test if the cursor is over the box
    if (mouseX > boxX - boxSize && mouseX < boxX + boxSize &&
        mouseY > boxY - boxSize && mouseY < boxY + boxSize) {
      mouseOverBox = true;
      // draw a line around the box and change its color:
      stroke(255);
      fill(153);
      // send an 'H' to indicate mouse is over square:
      port.write('H');
    }
    else {
      // return the box to its inactive state:
      stroke(153);
      fill(153);
      // send an 'L' to turn the LED off:
      port.write('L');
      mouseOverBox = false;
    }

    // Draw the box
    rect(boxX, boxY, boxSize, boxSize);
  }

*/

/* Max/MSP version 5 patch to run with this example:

  ----------begin_max5_patcher----------
  1672.3oc2ZszaaiCD9ryuBBebQVCQRYao8xhf1cQCPVfBzh8RRQ.sDsM2HSZ
  HQmlzh9eu7gjsjsEk7y0oWjiHoHm4aluYHGlueUmtiDuPy5B9Cv8fNc99Uc5
  XZR2Pm726zcF4knDRlYXciDylQ4xtWa6SReQZZ+iSeMiEQR.ej8BM4A9C7OO
  kkAlSjQSAYTdbFfvA27o2c6sfO.Doqd6NfXgDHmRUCKkolg4hT06BfbQJGH3
  5Qd2e8d.QJIQSow5tzebZ7BFW.FIHow8.2JAQpVIIYByxo9KIMkSjL9D0BRT
  sbGHZJIkDoZOSMuQT.8YZ5qpgGI3locF4IpQRzq2nDF+odZMIJkRjpEF44M3
  A9nWAum7LKFbSOv+PSRXYOvmIhYiYpg.8A2LOUOxPyH+TjPJA+MS9sIzTRRr
  QP9rXF31IBZAHpVHkHrfaPRHLuUCzoj9GSoQRqIB52y6Z.tu8o4EX+fddfuj
  +MrXiwPL5+9cXwrOVvkbxLpomazHbQO7EyX7DpzXYgkFdF6algCQpkX4XUlo
  hA6oa7GWck9w0Gnmy6RXQOoQeCfWwlzsdnHLTq8n9PCHLv7Cxa6PAN3RCKjh
  ISRVZ+sSl704Tqt0kocE9R8J+P+RJOZ4ysp6gN0vppBbOTEN8qp0YCq5bq47
  PUwfA5e766z7NbGMuncw7VgNRSyQhbnPMGrDsGaFSvKM5NcWoIVdZn44.eOi
  9DTRUT.7jDQzSTiF4UzXLc7tLGh4T9pwaFQkGUGIiOOkpBSJUwGsBd40krHQ
  9XEvwq2V6eLIhV6GuzP7uzzXBmzsXPSRYwBtVLp7s5lKVv6UN2VW7xRtYDbx
  7s7wRgHYDI8YVFaTBshkP49R3rYpH3RlUhTQmK5jMadJyF3cYaTNQMGSyhRE
  IIUlJaOOukdhoOyhnekEKmZlqU3UkLrk7bpPrpztKBVUR1uorLddk6xIOqNt
  lBOroRrNVFJGLrDxudpET4kzkstNp2lzuUHVMgk5TDZx9GWumnoQTbhXsEtF
  tzCcM+z0QKXsngCUtTOEIN0SX2iHTTIIz968.Kf.uhfzUCUuAd3UKd.OKt.N
  HTynxTQyjpQD9jlwEXeKQxfHCBahUge6RprSa2V4m3aYOMyaP6gah2Yf1zbD
  jVwZVGFZHHxINFxpjr5CiTS9JiZn6e6nTlXQZTAFj6QCppQwzL0AxVtoi6WE
  QXsANkEGWMEuwNvhmKTnat7A9RqLq6pXuEwY6xM5xRraoTiurj51J1vKLzFs
  CvM7HI14Mpje6YRxHOSieTsJpvJORjxT1nERK6s7YTN7sr6rylNwf5zMiHI4
  meZ4rTYt2PpVettZERbjJ6PjfqN2loPSrUcusH01CegsGEE5467rnCdqT1ES
  QxtCvFq.cvGz+BaAHXKzRSfP+2Jf.KCvj5ZLJRAhwi+SWHvPyN3vXiaPn6JR
  3eoA.0TkFhTvpsDMIrL20nAkCI4EoYfSHAuiPBdmJRyd.IynYYjIzMvjOTKf
  3DLvnvRLDLpWeEOYXMfAZqfQ0.qsnlUdmA33t8CNJ7MZEb.u7fiZHLYzDkJp
  R7CqEVLGN75U+1JXxFUY.xEEBcRCqhOEkz2bENEWnh4pbh0wY25EefbD6EmW
  UA6Ip8wFLyuFXx+Wrp8m6iff1B86W7bqJO9+mx8er4E3.abCLrYdA16sBuHx
  vKT6BlpIGQIhL55W7oicf3ayv3ixQCm4aQuY1HZUPQWY+cASx2WZ3f1fICuz
  vj5R5ZbM1y8gXYN4dIXaYGq4NhQvS5MmcDADy+S.j8CQ78vk7Q7gtPDX3kFh
  3NGaAsYBUAO.8N1U4WKycxbQdrWxJdXd10gNIO+hkUMmm.CZwknu7JbNUYUq
  0sOsTsI1QudDtjw0t+xZ85wWZd80tMCiiMADNX4UzrcSeK23su87IANqmA7j
  tiRzoXi2YRh67ldAk79gPmTe3YKuoY0qdEDV3X8xylCJMTN45JIakB7uY8XW
  uVr3PO8wWwEoTW8lsfraX7ZqzZDDXCRqNkztHsGCYpIDDAOqxDpMVUMKcOrp
  942acPvx2NPocMC1wQZ8glRn3myTykVaEUNLoEeJjVaAevA4EAZnsNgkeyO+
  3rEZB7f0DTazDcQTNmdt8aACGi1QOWnMmd+.6YjMHH19OB5gKsMF877x8wsJ
  hN97JSnSfLUXGUoj6ujWXd6Pk1SAC+Pkogm.tZ.1lX1qL.pe6PE11DPeMMZ2
  .P0K+3peBt3NskC
  -----------end_max5_patcher-----------

*/
