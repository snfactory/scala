#!/usr/bin/python

import numpy as N
import SCALA_tools as St
import pyNetIO as net
import Monochromator_tools as Mt
#import IO_SCALA as io
import optparse
import random
import time

"""
Turn on everything(How??)
"""
nio = net.NetIO( SerPort = '/dev/ttyUSB1') 
nio.SetPortList(List='1101')
time.sleep(20)
#input_output = io.IO_scala()

#input_output.switch_XeLamp_on()
#if input_output.Is_XeLamp_on()== False:
#    input_output.switch_XeLamp_on()

#input_output.switch_MonoChrometor_on()
#if input_output.Is_MonoChrometor_on()== False:
#    input_output.switch_MonoChrometor_on()

#input_output.switch_CLAPS_on()
#if input_output.Is_CLAPS_on()== False:
#    input_output.switch_CLAPS_on()

Mt.Clear_MonoChromator()


if __name__=='__main__':

    wavelength = []
    exposure_time = []
    parser = optparse.OptionParser()
    parser.add_option("-t" , "--timerun", help="Give a total time for SCALA run in min", default=None)
    opts,args = parser.parse_args()
    """
    in the total time check
    there is (float(opts.timerun)-15)*60.
    where the 15 min are considered as the part 
    of the total run time to change wavelengths
    change grating and filters, etc.
    """
    while N.sum(exposure_time)<=((float(opts.timerun)-(float(opts.timerun)*0.6))*60.):
        wavelength    = N.append(wavelength,random.randrange(3200,10000,30))
        exposure_time = N.append(exposure_time,random.randrange(1,30))

    Scala = St.SCALA(wavelength, exposure_time,used_clap=[True,True])
    Scala.do_exposures(savefile="test_run_4")
    Scala.Disconnect_claps()
    

    """
    Turn off everything maybe using SCALA_Clear.py??
    """
    nio.SetPortList(List='0000')
    #input_output.switch_XeLamp_off()
    #if input_output.Is_XeLamp_on()== True:
    #    input_output.switch_XeLamp_off()

    #input_output.switch_HaloLamp_off()
    #if input_output.Is_HaloLamp_on()== True:
    #    input_output.switch_HaloLamp_off()
    
    #input_output.switch_MonoChrometor_off()
    #if input_output.Is_MonoChrometor_on()== True:
    #    input_output.switch_MonoChrometor_off()

    #input_output.switch_CLAPS_off()
    #if input_output.Is_CLAPS_on()== True:
    #    input_output.switch_CLAPS_off()


    print "SCALA is done!!"
