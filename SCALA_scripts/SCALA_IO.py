#!/usr/bin/python

import IO_SCALA as IOs
import sys
import time
def SafeMode(it_max=5, message="Entre a key"):
    """
    """
    key = None
    i   = 0
    while(key not in ['y','n'] and i<it_max):
        if i ==0:
            key = raw_input("%s (y/n): "%message)[0]
        else:
            key = raw_input("Sorry, %s, please entre the key again (y/n): "%message)[0]
        i+=1
        
    if key not in ['y','n']:
        print "As I didn't understood the key, NO is set (n)"
        key ="n"
        
    return key.lower()
    
##############################################################
# ---------------------------------------------------------- #
# -----------  MAIN: SCRIPT FOR SCALA  --------------------- #
# ---------------------------------------------------------- #
##############################################################
if __name__ == '__main__':
    """
    This Script allow to discuss directly with the different element of SCALA
    Notably it allow to shitch on and off the the various elements using the netIO element.

    Use list to give various order simultaneously [Mono, Xenon, Halo, Claps]
    
    """
    
    import optparse
    parser = optparse.OptionParser()
    # -------------------------- #
    # ---   OPTIONS          --- #
    # -------------------------- #
    
    # -- Options for the scala class -- #
    parser.add_option("--Check",action="store_true",
                      help="This will return the current power connexions: 1=On 0=Off "+"\n"+
                      "(Order Recall: %s)"%IOs.NET_IO_order,
                      default=False)

    parser.add_option("--On",action="store_true",
                      help="This will switch on SCALA, this is equivalent to --list 1101"+" \n "+
                      "(Order Recall: %s)"%IOs.NET_IO_order+"\n",
                      default=False)
    
    parser.add_option("--OnBackground",action="store_true",
                      help="This will switch on SCALA, BUT NOT THE LIGHTS this is equivalent to --list 1001"+" \n "+
                      "(Order Recall: %s)"%IOs.NET_IO_order+"\n",
                      default=False)
    
    parser.add_option("--Off",action="store_true",
                      help="This will switch off SCALA, this is equivalent to --list 0000"+" \n "+
                      "(Order Recall: %s)"%IOs.NET_IO_order+"\n",
                      default=False)
    # ======================= #
    # == Low Level Input   == #
    # ======================= #
    parser.add_option("--list",
                      help="Given a list corresponding to %s (1-9 for On, 0 for Off) -- MUST HAVE A LENS OF 4"+" \n "+
                      "(Order Recall: %s)"%IOs.NET_IO_order+"\n "+
                      "[*CAUTION* - USE IT CAREFULLY -  If --list runs, other options are skipped] -- default [%default]",
                      default=None)

    
    parser.add_option("--MonoChromator", action='store_true',
                      help="Sets ON the MonoChromator (set if OFF otherwise)"+" \n "
                      " -- default [%default]",
                      default=False)
    
    parser.add_option("--XenonLamp", action='store_true',
                      help="Sets ON the XenonLamp (set if OFF otherwise)"+" \n "
                      " -- default [%default]",
                      default=False)
    
    parser.add_option("--HaloLamp", action='store_true',
                      help="Set ON the HaloLamp (set if OFF otherwise)"+" \n "
                      " -- default [%default]",
                      default=False)
    
    parser.add_option("--Claps", action='store_true',
                      help="Sets ON the Claps (set if OFF otherwise)"+" \n "
                      " -- default [%default]",
                      default=False)
    
    # ------------------------- #
    # -- SAFE MODE          --- #
    # ------------------------- #
    parser.add_option("--safemove",action="store_true",
                      help="This function is asking for confirmation to switch off something except is THIS is activating",
                      default=False)
    
    parser.add_option("-V","--verbose",action="store_true",
                      help="This avoid the informative prints !",
                      default=False)
    
    parser.add_option("--snifs",action="store_true",
                      help="This option if there for print for SNIFS scripts",
                      default=False)
    opts,args = parser.parse_args()
    # -------------------------- #
    # --- SCRIPTS themself   --- #
    # -------------------------- #
    if opts.snifs:
        opts.verbose = False
        
    if opts.verbose:
        print "".center(30,'=')
        print " WELCOME THE SCALA_IO ".center(30,'=')
        print "".center(30,'=')

    net = IOs.IO_scala(verbose=opts.verbose)
    
    try:
        portList = net.GetPortList()
    except:
        time.sleep(3)
        try:
            portList = net.GetPortList()
        except:
            raise ValueError("I can't talk to the NetIO")
        
    # =================== #
    # Basic Stuff on/off  #
    # =================== #
    if opts.On:
        opts.list = "1101"
    elif opts.OnBackground:
        opts.list = "0001"
    elif opts.Off:
        opts.list = "0000"
        
    # =================== #
    # Basic Stuff on/off  #
    # =================== #
    if opts.list is not None:
        if len(opts.list) == 4:
            if opts.verbose:
                print "This will be made %s"%opts.list
            net.SetPortList(opts.list)
            print "Status 0"
            sys.exit(0)
        else:
            raise ValueError('SCALA_IO.py --list must have 4 entries (%s) - %d given (%s)'%(IOs.NET_IO_order,len(opts.list),opts.list))
    # --------------------------- #
    # -- IS THE NETIO CONNECTED ? #
    # --------------------------- #
    net = IOs.IO_scala(verbose=opts.verbose)
    
    try:
        portList = net.GetPortList()
    except:
        time.sleep(3)
        try:
            portList = net.GetPortList()
        except:
            raise ValueError("I can't talk to the NetIO")

    # -- Ok Let's go --#
    

        
    if opts.verbose:
        print "The MonoChromator is Ongoing..."
        
    if opts.Check:
        print portList
        sys.exit(0)
        
    # -- MonoChromator -- #
    if opts.MonoChromator:
        Mo = net.switch_MonoChrometor_on(wait_for_it=False)
        if opts.verbose:
            print "MONO SETS ON"
    else:
        key = 'y'
        if  opts.safemove:
            key = SafeMode(it_max=5,message="Do you want to switch the MonoChrometor off ?")
        if key == "y":
            net.switch_MonoChrometor_off()

    if opts.verbose:
        print "The Xenon Lamp is Ongoing..."
        
    # -- XenonLamp -- #
    if opts.XenonLamp:
        Xe = net.switch_XeLamp_on()
        if opts.verbose:
            print "XENO SETS ON"
    else:
        key = 'y'
        if opts.safemove:
            key = SafeMode(it_max=5,message="Do you want to switch the Xenon Lamp off ?")
        if key == "y":
            net.switch_XeLamp_off()

    if opts.verbose:
        print "The Halo Lamp is Ongoing..."
        
    # -- HaloLamp -- #
    if opts.HaloLamp:
        Ha = net.switch_HaloLamp_on()
        if opts.verbose:
            print "HALO SETS ON"
    else:
        key = 'y'
        if  opts.safemove:
            key = SafeMode(it_max=5,message="Do you want to switch the Halo Lamp off ?")
        if key == "y":
            net.switch_HaloLamp_off()

    if opts.verbose:
        print "And Finally The Calps are Ongoing..."
        
    # -- XenonLamp -- #
    if opts.Claps:
        Cl = net.switch_CLAPS_on()
        if opts.verbose:
            print "CLAPS SETS ON"
    else:
        key = 'y'
        if  opts.safemove:
            key = SafeMode(it_max=5,message="Do you want to switch the CLAPS Lamp off ?")
        if key == "y":
            net.switch_CLAPS_off()

            
    # --------------------------------------- #
    # -- SCRIPTS ENDS BY THE CURRENT STATUS - # 
    # --------------------------------------- #
    if opts.XenonLamp:
        if Xe is None:
            if opts.verbose:
                "INFO - The Xenon lamp was off. You should wait for 15 second"
            if opts.snifs:
                # Says to SNIFS: Wait 15s
                print "15"
        else:
            if opts.snifs:
                # Says to SNIFS: Wait 0s
                print "0"
        
        
    if opts.verbose:    
        IOs.Status_Test(True,"Here is the current connexion status: %s"%net.GetPortList()+
                        "\n"+"(Order Recall: %s)"%IOs.NET_IO_order)
    
