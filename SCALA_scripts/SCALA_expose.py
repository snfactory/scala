#!/usr/bin/python

import sys

import numpy       as N
import SCALA_tools as St
import SNIFS_Exposure_tools as SEt
from General_tools import make_me_iterable
import time


def Exposure_run(Wavelengths_array,Expo_time_array,
                 snifs_mode,savefile,
                 use_clap=[True,True],verbose=True,
                 kwargs_clap={},force_filter=None,
                 force_grating=None,force_lamp=None,
                 ):
    """
    """
    
    if verbose:
        print "".center(50,'*')
        print Wavelengths_array,Expo_time_array
        print "".center(50,'*')

    if type(Wavelengths_array) !=float and   type(Wavelengths_array)!= int:
        if len(Wavelengths_array) != len(Expo_time_array) or len(Wavelengths_array)==0:
            error_message = "ERROR SCRIPT INPUT [SCALA_test] -- opts.test_wavelengthes and opts.test_exposure_times must have the same size and by greater than 0"
            if erbose:
                print error_message
            if snifs_mode:
                print "Status 1"
                sys.exit(1)
            else:
                raise ValueError(error_message)
    else:
        Wavelengths_array = N.asarray([Wavelengths_array],dtype='float')
        Expo_time_array   = N.asarray([Expo_time_array],  dtype='float')
    
    # ----------------------- #
    # -- SCALA RUN ITSELF  -- #
    # ----------------------- #
    Scala = St.SCALA(Wavelengths_array,Expo_time_array,used_clap=[True,True],
                     verbose=verbose,snifs_mode=snifs_mode,
                     kwargs_clap=kwargs_clap,)
    
    Scala.do_exposures(savefile=savefile,
                       force_filter=force_filter,
                       force_grating=force_grating,
                       force_lamp=force_lamp)
    
    Scala.Disconnect_claps()
    print "Status 0"
    sys.exit(0)


    
    
    
    
##############################################################
# ---------------------------------------------------------- #
# ----------- MAIN SCALA's SCRIPT      --------------------- #
# ---------------------------------------------------------- #
##############################################################

if __name__ == '__main__':

    import optparse
    parser = optparse.OptionParser()

    # ---------------------- #
    # -- Run options      -- #
    parser.add_option("-w","--wavelengths", 
                      help="Give a wavelengths or a parsable input like b1 or r5...",
                      default=None)
    
    parser.add_option("-e","--exposure_times", 
                      help="The exposure time associated to the wavelength [array or the same size as --wavelengths / unique float / None]",
                      default=None)

    parser.add_option("--shorten_exposures_by", type="float", # -- ToBeTested
                      help="Divide the default exposure_time (i.e. -e is None) by that much: =1: unchange ; >1: shorter ; <1: longer ",
                      default=1.)
    
    parser.add_option("-s","--savefile", 
                      help="Name of the fits file where this SCALA's run will be registered. If None, SCALA_YY_DDD_HH_MM.fits ",
                      default='SAVE_FILE_default_SCALA')
	
	#new option for repeating a measurement n times
    parser.add_option("-n","--number_measurements",type='int',
                      help="Number of repetitions of one measurement", 
                      default=1)

    # ---------------------- #
    # - Forcing things     - #
    parser.add_option("-g","--grating",
                      help="CAREFUL HERE: this enables you to force the used grating (should be 1 or 2) [%default]",
                      default = None)
    
    parser.add_option("-f","--filter",
                      help="CAREFUL HERE: this enables you to force the used filter (should be 1,2,3,4,5,6) [%default]",
                      default = None)
    
    parser.add_option("-l","--lamp",
                      help="CAREFUL HERE: this enables you to force the used lamp (should be ha/halo or xe/xenon) [%default]",
                      default = None)
    # ---------------------- #
    # -- SCALA options    -- #
    parser.add_option("--stepRun", type="float",
                      help="Set the amplitude [in Angstrom] of the step between two SNIFS run [%default]",
                      default = 180)
    # -- This is a doublon : See also SNIFS_Exposure_tools that will be use if, and only if, this is None
    
    parser.add_option("--intra_stepRun", type="float", # -- ToBeTested
                      help="*CAREFUL with that* Set the amplitude [in Angstrom] between 2 wavelengths inside a run",
                      default = 500)
    # -- This is a doublon : See also SNIFS_Exposure_tools that will be use if, and only if, this is None

    parser.add_option("--start_offset", type="float", # -- ToBeTested
                      help="Change this to give an offset to the starting wavelength (SNIFS option) <0 starts bluer >0 starts redder",
                      default=0.)

    parser.add_option("-C","--addCalibration", action="store_true", # -- ToBeTested
                      help="Set this option to force a Calibration run at the end of you runs (SNIFS)",
                      default=False)
    
    parser.add_option("--clapfrequency", type="float",
                      help="The frenquency of datataking [in kHz] default (default %default) ",
                      default=1.)

    parser.add_option("--maxtime", type="int",
                      help="Maxiumum time allowed for that run, time in seconds",
                      default=None)
    
    # ---------------------- #
    # -- Printing outputs -- #
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
    # -- INPUTS           -- #
    # ---------------------- #
    if opts.savefile is None or opts.savefile=="None":
        loc        = time.localtime()
        savefile   = "SCALA_test_%s_%d_%d_%d.fits"%(str(loc.tm_year)[-2:], loc.tm_yday,loc.tm_hour, loc.tm_min)
    else:
        savefile = opts.savefile
    
    # ---------------------- #
    # -- OUTPUTS          -- #
    # ---------------------- #  
    Wavelengths_array  = SEt.Read_wavelength_input(opts.wavelengths,
                                                   verbose=opts.Verbose,
                                                   ExtraRunStep = opts.stepRun,
                                                   IntraRunStep = opts.intra_stepRun,
                                                   start_offset = opts.start_offset,
                                                   addCalibrationRun = opts.addCalibration
                                                   )

    if opts.number_measurements is None or opts.number_measurements != opts.number_measurements:
        opts.number_measurements=1
    if opts.number_measurements < 1:
        raise ValueError('Number of measurements must be >=1 (given %d)' %opts.number_measurements)
    if opts.number_measurements > 1:
        Wavelengths_array = N.asarray(make_me_iterable(Wavelengths_array))
        Wavelengths_array = Wavelengths_array.tolist() * opts.number_measurements
    
    # -- This is None is Nothing else has to be done 
    if Wavelengths_array is None:
        # --- No need for new wavelength -- #
        #    SCALA's jobs is done           #
        print "Status 10"
        sys.exit(0)

    
    Expo_time_array    = SEt.Read_exposure_input(opts.exposure_times,
                                                 wavelength_array=Wavelengths_array,
                                                 verbose=opts.Verbose,
                                                 shorten_default_exposures_by=opts.shorten_exposures_by)

    #check  whether the run will be longer than the maximum allowed time   

    if opts.maxtime is not None:
        Expo_time_array = make_me_iterable(Expo_time_array)
        total_time=N.sum(Expo_time_array)+len(Expo_time_array)*(opts.number_measurements-1)*8 # time in seconds
        if total_time > opts.maxtime:
            raise ValueError('The estimated time for the run is longer than the maximum runtime allowed')


    kwargs_clap = {'frequency':opts.clapfrequency}


    # =============== #
    # = Forced stuff  #
    force_grating = None if (opts.grating is None or opts.grating in ["None","none"]) else\
      int(opts.grating)

    force_filter = None if (opts.filter is None or opts.filter in ["None","none"]) else\
      int(opts.filter)
      
    force_lamp = None if (opts.lamp is None or opts.filter in ["None","none"]) else\
      str(opts.lamp)
      
    # -- Ok do exposures -- #
    Exposure_run(Wavelengths_array,Expo_time_array,
                 opts.snifs,savefile,
                 use_clap=[True,True],
                 verbose=opts.Verbose,
                 kwargs_clap=kwargs_clap,
                 force_filter=force_filter,
                 force_grating=force_grating,
                 force_lamp=force_lamp
                 )
