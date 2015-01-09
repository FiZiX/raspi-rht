/*
 * th.c  capture Temperature and Humidity readings, write them to sql database
 *	https://projects.drogon.net/raspberry-pi/wiringpi/

rev 1.0 12/01/2013 WPNS built from Gordon Hendersen's rht03.c
rev 1.1 12/01/2013 WPNS don't retry, takes too long
rev 1.2 12/01/2013 WPNS allow one retry after 3-second delay
rev 1.3 12/01/2013 WPNS make cycle time variable
rev 1.4 12/01/2013 WPNS add mysql stuff in
rev 1.5 12/01/2013 WPNS do 60 second cycle, cleanup, trial run
rev 1.6 12/01/2013 WPNS clean up output format
rev 1.7 12/02/2013 WPNS allow more retries, minor cleanups
rev 1.79 12/04/2013 WPNS release to instructables

 */

#include <stdio.h>

#include <wiringPi.h>
#include <maxdetect.h>
#include <time.h>

#define	RHT03_PIN	7
#define CYCLETIME       3
#define RETRIES         3


/*
 ***********************************************************************
 * The main program
 ***********************************************************************
 */

int main (void)
{
  int temp, rh ;                 // temperature and relative humidity readings
  int loop ;                      // how many times through the loop?
  int resultcntr ;               // how many results have we sent?

  time_t rawtime;

  int status;                   // how did the read go?

  temp = rh = loop = 0 ;

  wiringPiSetup () ;
  piHiPri       (55) ;
  
  // First two results from the sensor are usually inaccurate
  // Make 3 iterations and output third result
  for (resultcntr = 0; resultcntr < 3; resultcntr++ )
    {
      // wait for an interval to start
      while ((((int)time(NULL))%CYCLETIME)) delay(100);

      // read new data
      temp = rh = -1;
      loop=RETRIES;

      status = readRHT03 (RHT03_PIN, &temp, &rh);
      while ((!status) && loop--)
        {
          //printf("-Retry-");
          //fflush(stdout);
          delay(3000);
          status = readRHT03 (RHT03_PIN, &temp, &rh);
        }

      time(&rawtime);

      // Only output result if this is the 3rd loop
      if (resultcntr == 2)
        {
          // Output temperature (in Farenheit), a tab, then the humidity
          printf ("%5.2f\t%4.1f", ((temp / 10.0) * 1.8) + 32, rh / 10.0) ;
          fflush(stdout);
        }
      else
        {
          // wait for the rest of that interval to finish
          while (!(((int)time(NULL))%CYCLETIME)) delay(100);
        }
    }
  
  return 0 ;
}
