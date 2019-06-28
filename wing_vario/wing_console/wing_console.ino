// rf95_server.pde
// -*- mode: C++ -*-
// Example sketch showing how to create a simple messageing server
// with the RH_RF95 class. RH_RF95 class does not provide for addressing or
// reliability, so you should only use RH_RF95  if you do not need the higher
// level messaging abilities.
// It is designed to work with the other example rf95_client
// Tested with Anarduino MiniWirelessLoRa, Rocket Scream Mini Ultra Pro with
// the RFM95W, Adafruit Feather M0 with RFM95

#include <SPI.h>
#include <RH_RF95.h>
#include <Adafruit_DotStar.h>

// Singleton instance of the radio driver
//RH_RF95 rf95;
//RH_RF95 rf95(5, 2); // Rocket Scream Mini Ultra Pro with the RFM95W
RH_RF95 rf95(8, 3); // Adafruit Feather M0 with RFM95 

#define RF95_FREQ 915.0

// Need this on Arduino Zero with SerialUSB port (eg RocketScream Mini Ultra Pro)
//#define Serial SerialUSB

#define NUMPIXELS 144
#define DATAPIN    5
#define CLOCKPIN   6
Adafruit_DotStar strip = Adafruit_DotStar(
  NUMPIXELS, DATAPIN, CLOCKPIN, DOTSTAR_BRG);

int led = 9;
int grnd = -1;

void setup() 
{
  // Rocket Scream Mini Ultra Pro with the RFM95W only:
  // Ensure serial flash is not interfering with radio communication on SPI bus
//  pinMode(4, OUTPUT);
//  digitalWrite(4, HIGH);

  pinMode(led, OUTPUT);     
  Serial.begin(9600);
  //while (!Serial) ; // Wait for serial port to be available
  Serial.println("Starting...");
  if (!rf95.init())
    Serial.println("init failed");
  rf95.setTxPower(23, false);
  // Defaults after init are 434.0MHz, 13dBm, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on

  // The default transmitter power is 13dBm, using PA_BOOST.
  // If you are using RFM95/96/97/98 modules which uses the PA_BOOST transmitter pin, then 
  // you can set transmitter powers from 5 to 23 dBm:
//  driver.setTxPower(23, false);
  // If you are using Modtronix inAir4 or inAir9,or any other module which uses the
  // transmitter RFO pins and not the PA_BOOST pins
  // then you can configure the power transmitter power for -1 to 14 dBm and with useRFO true. 
  // Failure to do that will result in extremely low transmit powers.
//  driver.setTxPower(14, true);

  strip.begin(); // Initialize pins for output
  strip.show();  // Turn all LEDs off ASAP
  strip.setBrightness(8);
}

int center_led = 42;
float last = 0;
long pts = 0; // Previous Time Stamp

void loop()
{
  
  if (rf95.available())
  {
    // Should be a message for us now   
    uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
    uint8_t len = sizeof(buf);
    if (rf95.recv(buf, &len))
    {
      strip.setPixelColor(center_led, 0, 255, 0);
      strip.show();
      digitalWrite(led, HIGH);
//      RH_RF95::printBuffer("request: ", buf, len);
      //Serial.print("got request: ");
      
      String msg = (char*)buf;
      int idx_A = msg.indexOf("A");
      int idx_P = msg.indexOf("P");
      int idx_T = msg.indexOf("T");
      int idx_S = msg.indexOf("S"); // Time Stamp
      float alt = msg.substring(idx_A+1,idx_P).toFloat();
      float tmp = msg.substring(idx_T+1, idx_S).toFloat();
      int ts = msg.substring(idx_S+1).toInt();

      int elapsed = pts-ts;

      if (grnd == -1) {
        grnd = alt;
        last = alt;
      }

      float vario = (alt - last)*1000/elapsed;
      int leds = abs(8 * vario);

      //reset
      for (int i = center_led-1; i >= 0; i--) {
          strip.setPixelColor(i, 0, 0, 0);
      }

      if (vario >= 0) {
        for (int i = center_led-1; i > center_led-leds; i--) {
          strip.setPixelColor(i, 0, 0, 255);
        }
      } else {
        for (int i = center_led-1; i > center_led-leds; i--) {
          strip.setPixelColor(i, 0, 255, 0);
        }
      }
      strip.show();
      last = alt;

      Serial.print("Altitude: ");
      Serial.println(alt-grnd);

      Serial.print("Vario: ");
      Serial.println(vario);


      Serial.print("Elapsed Time: ");
      Serial.println(elapsed);
      pts = ts;
      
      digitalWrite(led, LOW);
    }
    else
    {
      Serial.println("recv failed");
      strip.setPixelColor(center_led, 0, 0, 0);
      strip.show();
    }
  }
}


