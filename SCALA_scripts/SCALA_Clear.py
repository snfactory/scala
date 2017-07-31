#!/usr/bin/python

import time
import SCALA_tools as St
# -- Note: those are also imported by St...
import Monochromator_tools as Mt
import Clap_tools          as Cl
import IO_SCALA            as IOs
import General_tools       as Gt

def Clean_up(verbose=True,snifs_mode=False,switch_off=True):
    """
    """
    if snifs_mode:
        verbose=False
        
    if verbose:
        print "".center(30,"-")
        print " SHUTING DOWN SCALA ".center(30,"-")
        print "".center(30,"-")

    
    if verbose:
        print "Moving the MonoChromator back to 4000 A"
    # --------------------- #
    # - BASICS BACK      -- #
    # --------------------- #
    Mt.Force_Wavelength_change(4000)
    if verbose:
        print "Disconnecting the CLAPS"

    Cl.disconnect_all_the_claps()
    net = IOs.IO_scala()
    if switch_off:
        if verbose:
            print "Switching OFF both CLAPS' and MonoChromator's power..."
        # -- Just to be sure -- #
        time.sleep(1)
        net.switch_MonoChrometor_off()
        net.switch_CLAPS_off()
        # -- Just to be sure -- #
        time.sleep(1)
        # ------------- #
        # -- RESTART -- #
        if verbose:
            print "Switching ON both CLAPS's and MonoChromator's power..."
        
    net.switch_MonoChrometor_on(wait_for_it=True)
    net.switch_CLAPS_on()
    if verbose:
        print "Loading the MonoChromator the 4000 A..."
    M = Mt.MonoChromator(4000)
    if verbose:
        print "Testing the MonoChromator with an exposure"
        
    M.expose__test_function(None)
    
    if verbose:
        print "Testing the CLAPS"
        
    if verbose:
        print " ---- Claps 0 ----"
        
    clap0 = Cl.Read_DC(device_number=0,line_periods=IOs.Line_frequency,
                       channels="b0")
    clap0.do_observation()
    
    if verbose:
        print " ---- Claps 1 ----"
        
    clap1 = Cl.Read_DC(device_number=1,line_periods=50,channels="b0")
    clap1.do_observation()
    if verbose:
        print "".center(30,"-")
        print " You are Good to Go ".center(30,"-")
        print "".center(30,"-")
        

    

    
##############################################################
# ---------------------------------------------------------- #
# ----------- SAVEUP: RESTARST THINGS THAT LOOKS STRANGE --- #
# ---------------------------------------------------------- #
##############################################################
if __name__ == '__main__':

    import optparse
    parser = optparse.OptionParser()
    # -------------------------- #
    # ---   OPTIONS          --- #
    # -------------------------- #
    
    parser.add_option("--no_power_restart",action="store_false",
                      help="TO NOT restart Both the CLAP and the MonoChromator power supply ",
                      default=True)
    
    parser.add_option("-V","--verbose",action="store_false",
                      help="This avoid the informative prints !",
                      default=True)
    
    parser.add_option("--snifs",action="store_true",
                      help="This option if there for print for SNIFS scripts",
                      default=False)
    
    opts,args = parser.parse_args()

    
        # -- Confusing name because by default, no_power_restart is True, which means
        #    that the power will be restart. It is as such to allow SCALA_restart --no_power_restart
    Clean_up(verbose=opts.verbose,snifs_mode=opts.snifs,
             switch_off=opts.no_power_restart)
        
    
