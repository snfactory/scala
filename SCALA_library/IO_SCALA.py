#!/usr/bin/python

import pyNetIO  as lower_IO
import time
from General_tools import *

SCALA_root = "/home/scala1/SCALA/"
INPUT_data = SCALA_root+"SCALA_library/INPUTS/"

#########################
# --------------------- #
# - TEST & CONNEXION  - #
# --------------------- #
#########################
def Status_Test(Bool, message=""):
    """
    """
    print "".center(70,"*")
    if Bool:
        print "Status - Ok"
        print message
    else:
        print "Status - Problem"
        print message
        
    print "".center(70,"*")

#########################
# --------------------- #
# -  SCALA            - #
# --------------------- #
#########################
Error_status_Scala = 1
SCALA_max_loading_time = 30 # in second
SCALA_channel = "0"
SCALA_fclass  = "000"
SCALA_xfclass = "000"
SCALA_prod    = "00-00"
def assign_prod_name():
    """
    """
    loc = time.localtime()
    year    = str(loc.tm_year)[-2:]
    day     = str(loc.tm_yday)
    obsnum  = '001'
    runnum  = '001'
    savefile= "Default_SCALA_fitsfile"
    #savefile = "%s_%s_%s_%s_%d_%s_%s_00-000.fits"%(year,day,obsnum,runnum,
    #                                                  SCALA_channel,SCALA_fclass,SCALA_xfclass,
    #                                                  )
    return savefile
            
#########################
# --------------------- #
# -  MONOCHROMATOR    - #
# --------------------- #
#########################
Error_status_Mono = 2
SCALA_COMPUTER_IP = "128.171.72.168"#"131.220.162.112"
SCALA_netmask     = "255.255.255.224"
# ------------------- #
# - Serial_function - #
# ------------------- #
Serial_port = '/dev/ttyUSB0' # windows: 'COMx', Linux: '/dev/<your_device_file>'
Serial_baud = 9600
# -- Times took by _load_current_status_ -- # 
IO_timer_max_loading = 20 # in Second

#########################
# --------------------- #
# -  CLAPS            - #
# --------------------- #
#########################
Error_status_clap = 3
IO_timer_max_loading_Clap = 20
# ------------------- #
# - Earth location  - #
# ------------------- #
Line_frequency = 60 # must be 50/60 in the EU/US


#########################
# --------------------- #
# -  Lamp Switch      - #
# --------------------- #
#########################
Error_status_Xe = 5
Error_status_Halo = 6
Serial_port_lampSwitch = '/dev/ttyACM0'
baud_lampSwtich = 9600

#########################
# --------------------- #
# -  NET I/O          - #
# --------------------- #
#########################
Error_status_NetIO = 6
switch_max_time    = 5 
NET_IO_port = '/dev/ttyUSB1'
NET_IO_port_backup = '/dev/ttyUSB2'

NET_IO_order= 'MonoChromator,XeLamp,HaloLamp,Claps'

class IO_scala(lower_IO.NetIO):
    """    
    """
    def __init__(self,SerPort=None,verbose=True):
        """
        """
        if SerPort is None:
            SerPort = NET_IO_port
            
        lower_IO.NetIO.__init__(self,SerPort=SerPort,SerPort_backup=NET_IO_port_backup)
        
        self.verbose= verbose
        
    ###########################################
    #   MonoChromator                         #
    ###########################################
    @timeout(switch_max_time,Error_status_NetIO)
    def Is_MonoChrometor_on(self):
        """
        """
        print "Is Mono On ?"
        if self.GetPortList()[0] == "1":
            return True
        
        time.sleep(0.2)
        # Sometimes they False negatives happend
        if self.GetPortList()[0] == "1":
            return True
        return False
    
    @timeout(switch_max_time,Error_status_NetIO)
    def switch_MonoChrometor_on(self,wait_for_it=False):
        """
        """
        if self.Is_MonoChrometor_on():
            return "Was on"
        
        if self.SetPortState(PortNr=1, State=1) == "OK":
            if self.verbose:
                print "SCALA.IO : The MonoChromator supply is On. Please wait 3 second for it to wake up"
            if wait_for_it:
                time.sleep(3)
                
    @timeout(switch_max_time,Error_status_NetIO)
    def switch_MonoChrometor_off(self):
        """
        """
        if self.Is_MonoChrometor_on():
            if self.SetPortState(PortNr=1, State=0) == "OK":
                if self.verbose:
                    print "SCALA.IO : The MonoChromator supply is now Off"
            else:
                raise ValueError("SCALA.IO : I've *FAILED* switching off the MonoChromator" )
        else:
            if self.verbose:
                print "SCALA.IO : The MonoChromator was already Off"


    ###########################################
    #   Xenon Lamp                            #
    ###########################################
    @timeout(switch_max_time,Error_status_NetIO)
    def Is_XeLamp_on(self):
        """
        """
        print "Is XeLamp On ?"
        if self.GetPortList()[1] == "1":
            return True

        time.sleep(0.2)
        # Sometimes they False negatives happend
        if self.GetPortList()[1] == "1":
            return True
        
        return False
    
    @timeout(switch_max_time,Error_status_NetIO)
    def switch_XeLamp_on(self):
        """
        """
        if self.Is_XeLamp_on():
            return "Was on"
        
        if self.SetPortState(PortNr=2, State=1) == "OK":
            if self.verbose:
                print "SCALA.IO : The XeLamp supply is On. You should wait for the lamp to warm up (not forced here)"

    @timeout(switch_max_time,Error_status_NetIO)
    def switch_XeLamp_off(self):
        """
        """
        if self.Is_XeLamp_on():
            if self.SetPortState(PortNr=2, State=0) == "OK":
                if self.verbose:
                    print "SCALA.IO : The Xenon Lamp supply is now Off"
            else:
                raise ValueError("SCALA.IO : I've *FAILED* switching off the Xenon Lamp" )
        else:
            if self.verbose:
                print "SCALA.IO : The Xenon Lamp was already Off"
                
    ###########################################
    #   Halogen Lamp                          #
    ###########################################
    @timeout(switch_max_time,Error_status_NetIO)
    def Is_HaloLamp_on(self):
        """
        """
        print "Is Halo On ?"
        if self.GetPortList()[2] == "1":
            
            return True
        time.sleep(0.2)
        # Sometimes they False negatives happend
        if self.GetPortList()[2] == "1":
            return True
        
        return False

    def switch_HaloLamp_on(self):
        """
        """
        try:
            self._switch_HaloLamp_on_()
        except:
            try:
                [self.GetPortList() for i in range(3)]
                self.SetPortList('1111')
            except:
                sys.exit(Error_status_NetIO)
    def switch_HaloLamp_off(self):
        """
        """
        try:
            self._switch_HaloLamp_off_()
        except:
            try:
                [self.GetPortList() for i in range(3)]
                self.SetPortList('1101')
            except:
                sys.exit(Error_status_NetIO)

    
    @timeout(switch_max_time,Error_status_NetIO)
    def _switch_HaloLamp_on_(self):
        """
        """
        if self.Is_HaloLamp_on():
            return "Was on"
        
        if self.SetPortState(PortNr=3, State=1) == "OK":
            if self.verbose:
                print "SCALA.IO : The Halo Lamp supply is On. You should wait for the lamp to warm up (not forced here)"
    
    @timeout(switch_max_time*2,Error_status_NetIO)
    def _switch_HaloLamp_off_(self,try_again=True):
        """
        """
        if self.Is_HaloLamp_on():
            if self.SetPortState(PortNr=3, State=0) == "OK":
                if self.verbose:
                    print "SCALA.IO : The Halo Lamp supply is now Off"
            else:
                try:
                    time.sleep(2)
                    self.switch_HaloLamp_off(try_again=False)
                except:
                    raise ValueError("SCALA.IO : I've *FAILED* switching off the Halo Lamp" )
        else:
            if self.verbose:
                print "SCALA.IO : The Halo Lamp was already Off"

        
    ###########################################
    #   CLAPS                                 #
    ###########################################
    @timeout(switch_max_time*3,Error_status_NetIO)
    def Is_CLAPS_on(self,try_again=True):
        """
        """
        print "Is Clap On ?"
        if self.GetPortList()[3] == "1":
            return True
        # Sometimes they False negatives happend
        time.sleep(0.2)
        if self.GetPortList()[3] == "1":
            return True
        time.sleep(1)
        self.GetPortList()
        self.Is_CLAPS_on(try_again=False)
        return False
    
    @timeout(switch_max_time,Error_status_NetIO)
    def switch_CLAPS_on(self):
        """
        """
        if self.Is_CLAPS_on():
            return "Was on"
        
        if self.SetPortState(PortNr=4, State=1) == "OK":
            if self.verbose:
                print "SCALA.IO : The CLAPS supply is now On. Ready to go"
                
    @timeout(switch_max_time,Error_status_NetIO)   
    def switch_CLAPS_off(self):
        """
        """
        if self.Is_CLAPS_on():
            if self.SetPortState(PortNr=4, State=0) == "OK":
                if self.verbose:
                    print "SCALA.IO : The CLAPS supply is now Off"
            else:
                raise ValueError("SCALA.IO : I've *FAILED* switching off the CLAPS" )
        else:
            if self.verbose:
                print "SCALA.IO : The CLAPS were already Off"
                

# ------------------------ #
