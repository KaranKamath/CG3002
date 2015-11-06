#include <LSM303.h>
#include "Wire.h"

//HMC5883L compass; //Copy the folder "HMC5883L" in the folder "C:\Program Files\Arduino\libraries" and restart the arduino IDE.
LSM303 compass;
float xv, yv, zv;
LSM303::vector<float> calibrated;
float newHeading(LSM303::vector<float> from);
void setup()
{   
  Serial.begin(9600);
  Wire.begin();  
  //compass = HMC5883L();  
  //setupHMC5883L(); 
  compass.init(LSM303::device_D, LSM303::sa0_low);
  compass.enableDefault();  
}



void loop()
{
  //getHeading();
  float heading;
  compass.read();
  Serial.print("Before:");
  Serial.print(compass.m.x); 
  Serial.print(",");
  Serial.print(compass.m.y);
  Serial.print(",");
  Serial.println(compass.m.z);
  heading = compass.heading(LSM303::vector<int>{0,0,-1});
  Serial.println(heading);
  LSM303::vector<float> bias, transx, transy, transz;
  bias = (LSM303::vector<float>){-171.524,-261.43,-404.003};
  transx = (LSM303::vector<float>){9.578,-1.035,-3.597};
  transy = (LSM303::vector<float>){-5.67,6.852,2.744};
  transz = (LSM303::vector<float>){1.82,-0.84,8.638};
  
  LSM303::vector<float> minus;
  minus.x = compass.m.x-bias.x;
  minus.y = compass.m.y-bias.y;
  minus.z = compass.m.z-bias.z;
  
  calibrated.x = LSM303::vector_dot(&transx, &minus);
  calibrated.y = LSM303::vector_dot(&transy, &minus);
  calibrated.z = LSM303::vector_dot(&transz, &minus);
 
  Serial.flush();
//  Serial.println(heading);
  
  Serial.print(calibrated.x); 
  Serial.print(",");
  Serial.print(calibrated.y);
  Serial.print(",");
  Serial.println(calibrated.z);
  float nheading = newHeading(LSM303::vector<float>{0,0,-1});
  Serial.println(nheading);
  delay(500); 
} 

//void setupHMC5883L()
//{  
  //compass.SetScale(0.88);
  //compass.SetMeasurementMode(Measurement_Continuous);
//}
 
//void getHeading()
//{ 
  //MagnetometerRaw raw = compass.ReadRawAxis();
  //xv = (float)raw.XAxis;
  //yv = (float)raw.YAxis;
  //zv = (float)raw.ZAxis;
//}

float newHeading(LSM303::vector<float> from) {
  LSM303::vector<float> E;
  LSM303::vector<float> N;
  LSM303::vector_cross(&calibrated, &compass.a, &E);
  LSM303::vector_normalize(&E);
  LSM303::vector_cross(&compass.a, &E, &N);
  LSM303::vector_normalize(&N);
  
  float nheading = atan2(LSM303::vector_dot(&E,&from), LSM303::vector_dot(&N,&from))*180/M_PI;
  if (nheading < 0) nheading += 360;
  return nheading;
}
