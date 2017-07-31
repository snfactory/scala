#!/usr/bin/python

import sys

import numpy       as N
import SCALA_tools as St
import SNIFS_Exposure_tools as SEt

def Background_run(Expo_time_array,
                   snifs_mode,savefile,
                   use_clap=[True,True],verbose=True,
                   kwargs_clap={}
                    ):
    """
    """
    Expo_time_array   = N.asarray(Expo_time_array,  dtype='float')
    if verbose:
        print "".center(50,'*')
        print Expo_time_array
        print "".center(50,'*')
        

    # ----------------------- #
    # -- SCALA RUN ITSELF  -- #
    # ----------------------- #
    Scala = St.SCALA(None,Expo_time_array,used_clap=use_clap,
                     verbose=verbose,snifs_mode=snifs_mode,
                     background_mode=True,
                     kwargs_clap=kwargs_clap)
    
    Scala.do_backgrounds(savefile=savefile)
    
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
    
    parser.add_option("-e","--exposure_times", 
                      help="The exposure time of backgrounds [can be a unique float or a list of float]",
                      default=None)
    
    parser.add_option("-n","--n_times", type="int",
                      help="This will multiply by n_times the exposure sequence you gave [default %default]",
                      default=1)
        
    parser.add_option("-s","--savefile", 
                      help="Name of the fits file where this SCALA's run will be registered. If None, SCALA_YY_DDD_HH_MM.fits ",
                      default='SAVE_FILE_default_SCALA')

    # ---------------------- #
    # -- SCALA options    -- #
    
    parser.add_option("--clapfrequency", type="float",
                      help="The frenquency of datataking [in kHz] default (default %default) ",
                      default=1.)
    
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
    if opts.savefile is None:
        loc        = time.localtime()
        savefile   = "SCALA_test_%s_%d_%d_%d.fits"%(str(loc.tm_year)[-2:], loc.tm_yday,loc.tm_hour, loc.tm_min)
    else:
        savefile = opts.savefile
    
    # ---------------------- #
    # -- OUTPUTS          -- #
    # ---------------------- #  

    
    Expo_time_array    = SEt.Read_exposure_input(opts.exposure_times,
                                                 wavelength_array=None,
                                                 verbose=opts.Verbose)
    Expo_time_array    = N.concatenate([Expo_time_array for i in range(opts.n_times)])

    
    kwargs_clap = {'frequency':opts.clapfrequency}
    
    # -- Ok do exposures -- #
    Background_run(Expo_time_array,
                 opts.snifs,opts.savefile,
                 use_clap=[True,True],
                 verbose=opts.Verbose,
                 kwargs_clap=kwargs_clap)
