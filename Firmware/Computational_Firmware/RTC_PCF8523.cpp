/*********************************************************************\
 * File:      RTC_PCF8523.cpp
 * Date:      04/17/2019
 * Authors:   Joshua Tracy and Daniel Henshaw
 * Hardware:  Pololu LIS3MDL 3-Axis magnetometer 
 *********************************************************************/
 
 #include "RTC_PCF8523.h"

/************************************************\
 * Name:    rtcTransfer
 * Purpose: Transfer data over TWI to an RTC
 *          Address is 0x68
 * Inputs:  reg
 *            -- value of the register to access
 *          flag
 *            -- read or write flag
 *          value
 *            -- if writing, the value to write
 * Outputs: returns a byte read from the register
 *          "reg" if doing a read.
 *      
 * Pseudocode:
 *   Power on the TWI interface
 *   Begin a transmission to the RTC
 *   Write the register number
 *   If writing,
 *     write the value to write
 *   If reading,
 *     request one byte from the RTC
 *     assign the byte to value
 *   Power down the TWI interface
 *   Return value
\************************************************/

byte rtcTransfer(byte reg, byte flag, byte value)
{
  twiPowerUp();
  
  Wire.beginTransmission(deviceAddr);
  Wire.write(reg);
  if(flag == WRITE)
    Wire.write(value);
  Wire.endTransmission();
  
  if(flag == READ)
  {
    Wire.requestFrom(deviceAddr, byte(1));
    value = Wire.read();
  }

  twiPowerDown();
  
  return value;
}

/*********************************************\
 * Function Name: loadDateTime
 * Purpose:       Loads date and time info
 *                from RTC into Date_t struct
 * Inputs:        Pointer to Date_t struct
 * Outputs:       None (modifes Date_t struct)
 * Pseudocode:
 *  Read seconds from RTC
 *  Convert from BCD to Binary byte
 *  Store in Date_t struct
 *  
 *  Read minutes from RTC
 *  Convert from BCD to Binary byte
 *  Store in Date_t struct
 *  
 *  Read hours from RTC
 *  Convert from BCD to Binary byte
 *  Store in Date_t struct
 *  
 *  Read days from RTC
 *  Convert from BCD to Binary byte
 *  Store in Date_t struct
 *  
 *  Read months from RTC
 *  Convert from BCD to Binary byte
 *  Store in Date_t struct
 *  
 *  Read years from RTC
 *  Convert from BCD to Binary byte
 *  Store in Date_t struct
 *  
 *  Return
\*********************************************/

void loadDateTime(Date_t* Date)
{
  byte seconds  = rtcTransfer(reg_Seconds, READ, 0);
  byte second10 = (seconds >> 4) & 0x07;
  byte second1  = seconds & 0x0F;
  Date->seconds = ((second10 * 10) + second1);
  
  byte minutes  = rtcTransfer(reg_Minutes, READ, 0);
  byte minute10 = (minutes >> 4) & 0x07;
  byte minute1  = minutes & 0x0F;
  Date->minutes = ((minute10 * 10) + minute1);
  
  byte hours    = rtcTransfer(reg_Hours, READ, 0);
  byte hour10   = (hours >> 4) & 0x03;
  byte hour1    = hours & 0x0F;
  Date->hours   = ((hour10 * 10) + hour1);
  
  byte days     = rtcTransfer(reg_Days, READ, 0);
  byte day10    = (days >> 4) & 0x03;
  byte day1     = days & 0x0F;
  Date->days    = ((day10 * 10) + day1);
  
  byte months   = rtcTransfer(reg_Months, READ, 0);
  byte month10  = (months >> 4) & 0x01;
  byte month1   = months & 0x0F;
  Date->months  = ((month10 * 10) + month1);
  
  byte years    = rtcTransfer(reg_Years, READ, 0);
  byte year10   = years >> 4;
  byte year1    = years & 0x0F;
  Date->years   = ((year10 * 10) + year1);

  return;
}

/***********************************************\
 * Name:    copyDateTime
 * Purpose: Copies data from one Date_t struct
 *          to another.
 *
 * Pseudocode:
 *   Copy years data
 *   Copy months data
 *   Copy days data
 *   Copy hours data
 *   Copy minutes data
 *   Copy seconds data
\***********************************************/

void copyDateTime(Date_t* Date1, Date_t* Date2)
{
  Date2->years   = Date1->years;    // Copy years data
  Date2->months  = Date1->months;   // Copy months data
  Date2->days    = Date1->days;     // Copy days data
  Date2->hours   = Date1->hours;    // Copy hours data
  Date2->minutes = Date1->minutes;  // Copy minutes data
  Date2->seconds = Date1->seconds;  // Copy seconds data
}

/***********************************************\
 * Name:    setClockPeriod
 * Purpose: Changes the output clock period
 *          of the Real Time Clock, which
 *          controls the frequency at which the
 *          datalogger writes data to the SD.
 * Inputs:  8-bit clock period in seconds.
 * Outputs: No function outputs.
 *          
 * Pseudocode:
 *   Power on TWI interface
 *   Begin a transmission to the RTC
 *   Write the register number
 *   Write the value to write
 *   Power down TWI interface
\***********************************************/

void setClockPeriod(uint8_t period)
{
  twiPowerUp();
  
  Wire.beginTransmission(deviceAddr);
  Wire.write(reg_Tmr_A_reg);
  Wire.write(period);
  Wire.endTransmission();

  twiPowerDown();

  return;
}
