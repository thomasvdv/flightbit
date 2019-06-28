// rf95_client.pde
// -*- mode: C++ -*-
// Example sketch showing how to create a simple messageing client
// with the RH_RF95 class. RH_RF95 class does not provide for addressing or
// reliability, so you should only use RH_RF95 if you do not need the higher
// level messaging abilities.
// It is designed to work with the other example rf95_server
// Tested with Anarduino MiniWirelessLoRa, Rocket Scream Mini Ultra Pro with
// the RFM95W, Adafruit Feather M0 with RFM95

#include <SPI.h>
#include <RH_RF95.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>

// Singleton instance of the radio driver
//RH_RF95 rf95;
//RH_RF95 rf95(5, 2); // Rocket Scream Mini Ultra Pro with the RFM95W
RH_RF95 rf95(8, 3); // Adafruit Feather M0 with RFM95 

// Need this on Arduino Zero with SerialUSB port (eg RocketScream Mini Ultra Pro)
//#define Serial SerialUSB

#define BMP_SCK 13
#define BMP_MISO 12
#define BMP_MOSI 11 
#define BMP_CS 10

#define RF95_FREQ 915.0

Adafruit_BMP280 bme; // I2C

char sendBuf[RH_RF95_MAX_MESSAGE_LEN];
byte sendLen;

void setup() 
{
  // Rocket Scream Mini Ultra Pro with the RFM95W only:
  // Ensure serial flash is not interfering with radio communication on SPI bus
//  pinMode(4, OUTPUT);
//  digitalWrite(4, HIGH);
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  if (!rf95.init())
    Serial.println("init failed");
  // Defaults after init are 434.0MHz, 13dBm, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on

  // The default transmitter power is 13dBm, using PA_BOOST.
  // If you are using RFM95/96/97/98 modules which uses the PA_BOOST transmitter pin, then 
  // you can set transmitter powers from 5 to 23 dBm:
  rf95.setTxPower(23, false);
  // If you are using Modtronix inAir4 or inAir9,or any other module which uses the
  // transmitter RFO pins and not the PA_BOOST pins
  // then you can configure the power transmitter power for -1 to 14 dBm and with useRFO true. 
  // Failure to do that will result in extremely low transmit powers.
  //driver.setTxPower(14, true);
  if (!bme.begin()) {  
    Serial.println("Could not find a valid BMP280 sensor, check wiring!");
    while (1);
  }
}

void loop()
{
    digitalWrite(LED_BUILTIN, HIGH);
    float tmp = bme.readTemperature();

    Serial.print("Temperature = ");
    Serial.print(tmp);
    Serial.println(" *C");

    float pres = bme.readPressure();
    
    Serial.print("Pressure = ");
    Serial.print(pres);
    Serial.println(" Pa");

    float alt = bme.readAltitude(1013.25);

    Serial.print("Approx altitude = ");
    Serial.print(alt); // this should be adjusted to your local forcase
    Serial.println(" m");
    
    Serial.println();
  
    Serial.println("Sending to rf95_server");
    // Send a message to rf95_server
    String msg = String("A");
    msg += alt;
    msg += "P";
    msg += pres;
    msg += "T";
    msg += tmp;
    msg += "S"; // Time Stamp
    msg += millis();
    
    msg.toCharArray(sendBuf, RH_RF95_MAX_MESSAGE_LEN); 
    sendLen = msg.length();
  // Send data to reciever and print to serial
    rf95.send((const uint8_t*)sendBuf, sizeof(sendBuf));
    //rf95.waitPacketSent();
    digitalWrite(LED_BUILTIN, LOW);
    delay(1000);
}


