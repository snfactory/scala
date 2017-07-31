#!/usr/bin/python

import sys
import time
import numpy       as N
import SCALA_tools as St

from SCALA_expose import Exposure_run


    
    
    
##############################################################
# ---------------------------------------------------------- #
# ----------- MAIN SCALA's SCRIPT      --------------------- #
# ---------------------------------------------------------- #
##############################################################

if __name__ == '__main__':

    import optparse
    parser = optparse.OptionParser()
    parser.add_option("-t","--time", type="float",
                      help="Give the time (in minutes) that SCALA has to run [%default]",
                      default=None)
    # -------  FOR THE RANDOMIZATION -------- #
    parser.add_option("--Time_Max", type="float" ,
                      help="Maximum time (in minute) allow in the randomization [%default]",
                      default=2.)
    
    parser.add_option("--Time_Min", type="float" ,
                      help="Min time (in minutes) allow in the randomization [%default]",
                      default=0.2)

    parser.add_option("--Wave_Max", type="float" ,
                      help="Maximum Wavelength (in Angstrom) allow in the randomization [%default]",
                      default=9000.)
    
    parser.add_option("--Wave_Min", type="float" ,
                      help="Maximum Wavelength (in Angstrom) allow in the randomization [%default]",
                      default=3300.)
    
    # -------  GENERIC STUFF  -------- #
    parser.add_option("-s","--savefile", 
                      help="Name of the fits file where this SCALA's run will be registered. \n If None, SCALA_Time_Limited_TIME_IN_MINUTE_YY_DDD_HH_MM.fits [%default]",
                      default=None)

    parser.add_option("-V","--Verbose",action="store_true", 
                      help="If you want all the additional prints",
                      default=False)
    
    parser.add_option("--snifs",action="store_true",
                      help="This option if there for print for SNIFS scripts",
                      default=False)
    

    opts,args = parser.parse_args()

    if opts.snifs:
        opts.verbose=False


    # ---------------------- #
    # -- INPUT            -- #
    # ---------------------- #
    if opts.time is None:
        error_message = "ERROR SCRIPT INPUT [SCALA_test] -- opts.time YOU MUST GIVE AN INPUT -t YOU_TIME_IN_MINUT"
        if opts.snifs:
            print "Status 10"
            sys.exit(10)
        else:
            raise ValueError(error_message)
        
    TimeMinute = opts.time
    TimeSec = opts.time*60
    TimeSec_Per_lost_per_Exposure = 10
    
    TimeSec_Max_randomiation = opts.Time_Max *60.
    TimeSec_Min_randomiation = opts.Time_Min *60.
    TimeSec_Range_randomisation = TimeSec_Max_randomiation-TimeSec_Min_randomiation

    Wave_Rand_randomisation = opts.Wave_Max - opts.Wave_Min
    # ---------------------- #
    # -- OUTPUTS          -- #
    # ---------------------- #
    if opts.savefile is None:
        loc        = time.localtime()
        savefile   = "SCALA_Time_Limited_%dmin_%s_%d_%d_%d.fits"%(TimeMinute,str(loc.tm_year)[-2:], loc.tm_yday,loc.tm_hour, loc.tm_min)
    else:
        savefile = opts.savefile
    
    # ---------------------- #
    # -- MANUAL MODE      -- #
    # ---------------------- #
    Expo_time_array = []
    while (N.sum(Expo_time_array) < (TimeSec - len(Expo_time_array)*TimeSec_Per_lost_per_Exposure)):
           Expo_time_array.append(  N.random.rand(1)[0]*TimeSec_Range_randomisation + TimeSec_Min_randomiation)
           

    Expo_time_array = N.asarray(Expo_time_array)
    Wavelengths_array  = N.random.rand(len(Expo_time_array))*Wave_Rand_randomisation + opts.Wave_Min

    Exposure_run(Wavelengths_array,Expo_time_array,
                 opts.snifs,savefile,
                 use_clap=[True,True],verbose=opts.Verbose)

    
