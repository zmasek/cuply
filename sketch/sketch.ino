#ifndef SERIAL_RATE
#define SERIAL_RATE         115200
#endif

#ifndef SERIAL_TIMEOUT
#define SERIAL_TIMEOUT      5
#endif

#include <Wire.h>

#ifdef ARDUINO_SAMD_VARIANT_COMPLIANCE
#define SERIAL SerialUSB
#else
#define SERIAL Serial
#endif
 
unsigned char low_data[8] = {0};
unsigned char high_data[12] = {0};
 
#define NO_TOUCH       0xFE
#define THRESHOLD      100
#define ATTINY1_HIGH_ADDR   0x78
#define ATTINY2_LOW_ADDR   0x77

#include <Servo.h>

Servo myservo;  // create servo object to control a servo
// twelve servo objects can be created on most boards
// pwm pin 2
int servoPin = 2;

void setup() {
    Serial.begin(SERIAL_RATE);
    Serial.setTimeout(SERIAL_TIMEOUT);
    Wire.begin();

    int cmd = readData();
    for (int i = 0; i < cmd; i++) {
        pinMode(readData(), OUTPUT);
    }
    myservo.attach(servoPin);
}

void loop() {
    switch (readData()) {
        case 0 :
            //set digital low
            digitalWrite(readData(), LOW); break;
        case 1 :
            //set digital high
            digitalWrite(readData(), HIGH); break;
        case 2 :
            //get digital value
            Serial.println(digitalRead(readData())); break;
        case 3 :
            // set analog value
            analogWrite(readData(), readData()); break;
        case 4 :
            //read analog value
            Serial.println(analogRead(readData())); break;
        case 5:
            //read i2c value
            Serial.println(check()); break;
        case 6:
            //write servo position
            myservo.write(readData()); break;
        case 7:
            //read servo position
            Serial.println(myservo.read()); break;

        case 99:
            //just dummy to cancel the current read, needed to prevent lock 
            //when the PC side dropped the "w" that we sent
            break;
    }
}

char readData() {
    Serial.println("w");
    while(1) {
        if(Serial.available() > 0) {
            return Serial.parseInt();
        }
    }
}

void getHigh12SectionValue(void) {
    memset(high_data, 0, sizeof(high_data));
    Wire.requestFrom(ATTINY1_HIGH_ADDR, 12);
    while (12 != Wire.available());
 
    for (int i = 0; i < 12; i++) {
        high_data[i] = Wire.read();
    }
    delay(10);
}
 
void getLow8SectionValue(void) {
    memset(low_data, 0, sizeof(low_data));
    Wire.requestFrom(ATTINY2_LOW_ADDR, 8);
    while (8 != Wire.available());
 
    for (int i = 0; i < 8 ; i++) {
        low_data[i] = Wire.read(); // receive a byte as character
    }
    delay(10);
}

int check() {
    int sensorvalue_min = 250;
    int sensorvalue_max = 255;
    int low_count = 0;
    int high_count = 0;
    while (1) {
        uint32_t touch_val = 0;
        uint8_t trig_section = 0;
        low_count = 0;
        high_count = 0;
        getLow8SectionValue();
        getHigh12SectionValue();

        for (int i = 0; i < 8; i++) {
            if (low_data[i] >= sensorvalue_min && low_data[i] <= sensorvalue_max) {
                low_count++;
            }
        }
        for (int i = 0; i < 12; i++) {
            if (high_data[i] >= sensorvalue_min && high_data[i] <= sensorvalue_max) {
                high_count++;
            }
        }

        for (int i = 0 ; i < 8; i++) {
            if (low_data[i] > THRESHOLD) {
                touch_val |= 1 << i;
            }
        }
        for (int i = 0 ; i < 12; i++) {
            if (high_data[i] > THRESHOLD) {
                touch_val |= (uint32_t)1 << (8 + i);
            }
        }

        while (touch_val & 0x01) {
            trig_section++;
            touch_val >>= 1;
        }
        int result;
        result = trig_section * 5;
        return result;
    }
}

