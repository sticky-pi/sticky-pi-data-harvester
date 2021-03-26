
#include <SoftwareSerial.h> 
#include <TinyGPS++.h>
#include <RTClib.h>
#include <Wire.h>
#include <EEPROM.h>
#include <hd44780.h>
#include <hd44780ioClass/hd44780_I2Cexp.h> // include i/o class header

hd44780_I2Cexp lcd; // declare lcd object: auto locate & config display for hd44780 chip
//float lat = 0.0,lon = 0.0; // create variable for latitude and longitude object  
SoftwareSerial gpsSerial(2,3);//(tx,rx)

TinyGPSPlus gps; // create gps object 
RTC_DS3231 RTC;

bool standalone = true;
unsigned int display_select = 1;
String lcd_rows[4];
unsigned long set_up_done_time;
unsigned int standalone_display_select;

struct GPSData {
  float lng;
  float lat;
  float alt;
  uint32_t last_updated;
  
};    

GPSData gps_data{0.0,0.0,-1e3, 0};  

static void smartDelay(unsigned long ms)
{
  unsigned long start = millis();
  do 
  {
    while (gpsSerial.available())
      gps.encode(gpsSerial.read());
  } while (millis() - start < ms);

}

void setup() { 
  Serial.begin(9600); // connect serial 
  Wire.begin();
  RTC.begin();
  lcd.begin(20, 4);                      // initialize the lcd 
  lcd.backlight();
  for (int i=0; i !=4; ++i){
    lcd_rows[i] = String("");
  }  
  
  gpsSerial.begin(9600); // connect gps sensor 
  
  lcd.clear(); 
  lcd.setCursor(0,0); 
  lcd.print(String(F("STICKY PI")));
  lcd.setCursor(0,1);
  lcd.print(String(F("WAITING FOR DEV")));

  String str("");
  Serial.println("READY");
  while(millis() < 5000){
    str = Serial.readStringUntil('\n');
    if(str == "BEGIN"){
      standalone = false;
      break;
      }
     delay(100);
    }
    
  String hello_message;
  if(!standalone)
    hello_message = String(F("CONNECTED!"));
  else
    hello_message = String(F("STANDALONE"));
  
  lcd.clear(); 
  lcd.setCursor(0,0); 
  lcd.print(String(F("STICKY PI")));
  lcd.setCursor(0,1);
  lcd.print(hello_message);
  delay(1500); 
  set_up_done_time = millis();

  
  
  EEPROM.get(0, gps_data);
  // invalidate gps data if is was not updated recently 600s!
  if(RTC.now().unixtime() - gps_data.last_updated > 600){
    gps_data = {0.0,0.0,-1e3, 0};
    Serial.println("# TOO LONG SINCE LAST DATA");
    }
  // lat is NaN if EEPROM was cleared/ new board  
  else if(gps_data.lat != gps_data.lat || RTC.now().unixtime() < gps_data.last_updated){
    Serial.println("# Inconsistent past gps data");
    gps_data = {0.0,0.0,-1e3, 0};  
    }
 else{
  Serial.println("# Loaded past GPS data");
  }
 
}

void loop() { 
  bool  available = false;
  while(gpsSerial.available()){ // check for gps data    
    available = true;
    char stream = gpsSerial.read();
    if(gps.encode(stream)){   
        Serial.print("# N_sat ");
        Serial.println(gps.satellites.value());
     } 
     if (millis() - set_up_done_time > 5000 && gps.charsProcessed() < 10){
        Serial.println(F("# No GPS detected: check wiring."));
        while(true);
    }
  }

  String gps_or_rtc("RTC");
  
  
  if (gps.date.isValid() & gps.time.isValid()){
    DateTime gps_time(gps.date.year(),gps.date.month(), gps.date.day(),
                  gps.time.hour(), gps.time.minute(), gps.time.second());
    

    char gps_datetime[20];
    sprintf (gps_datetime, "%04d-%02d-%02dT%02d:%02d:%02dG",gps_time.year(),gps_time.month(),gps_time.day(), gps_time.hour(), gps_time.minute(), gps_time.second());
    if(gps_time.year() >= 2020){
//      Serial.print("# Adjusting RTC: ");
//      Serial.println(gps_datetime);
      
      gps_or_rtc = "GPS";
      RTC.adjust(gps_time); 
    }      
      gps_data.lat = gps.location.lat();
      gps_data.lng = gps.location.lng();
      gps_data.alt = gps.altitude.meters();
      gps_data.last_updated=RTC.now().unixtime();
      EEPROM.put(0, gps_data);      
    }
  
  
  String latitude = String(gps_data.lat,6); 
  String longitude = String(gps_data.lng,6); 
  String altitude = String(gps_data.alt,0); 
  
  DateTime now = RTC.now();
  char datetime[20];
  sprintf (datetime, "%04d-%02d-%02dT%02d:%02d:%02dZ",now.year(),now.month(),now.day(), now.hour(), now.minute(), now.second());
  String datetime_str = String(datetime);
  
  String str("");
  if(!standalone){
    Serial.println(latitude + ";" + longitude + ";" + altitude + ";" + datetime_str);
       str = Serial.readStringUntil('\n');
  }
  else{
    switch( standalone_display_select++ % 5){
      case 1:
          str = latitude + "," + longitude; // todo, trim the last couple of digits?
          break;
      case 2:
          str = altitude +" m|(" + gps_or_rtc + ")" ;
          break;
      case 4:
          if(available)
            str = "GPS available";
          else
            str = "GPS UNavailable";
          break;
      case 0:
          str = datetime_str.substring(0,10) + " " + datetime_str.substring(11,19)+"Z";
          break;
      case 3:
          int v =  analogRead(A0);
          int percent = (100.0 * (float) v * 5.0) / (1027.0 * 4.3);
          String percent_str = String(percent);
          str = "BAT " + percent_str + "%";
          break;
    }
    smartDelay(1000);
    }
    
  if(str != ""){
    for(int i=0; i!=3; ++i){
      lcd_rows[i] = lcd_rows[i+1];
      lcd_rows[i+1] = str.substring(0,20);
    }
    lcd.clear(); 
    for(int i=0; i!=4; ++i){
      lcd.setCursor(0,i); 
      lcd.print(lcd_rows[i]);
    }
    }
    
    
  
  delay(250); 
  }
