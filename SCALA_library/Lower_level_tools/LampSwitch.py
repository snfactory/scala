#! /usr/bin/env python

import serial
import time
import sys

import IO_SCALA as IOs


class LSSM:
    """This class controlls the Light Source Selecting Mirror"""
    #def __init__(self, port='COM4'):
    def __init__(self):
        self.serialport = IOs.Serial_port_lampSwitch  #windows: 'COMx', Linux: '/dev/<your_device_file>'
        self.baud = IOs.baud_lampSwtich
        self.sendtermchar = "\r\n"
        self.rectermchar = "\r\n"
        self.timeout = 10
        self.dsrdtr = False,
        self.xonxoff = False,
        self.rtscts = False
        # -- I need the power -- #
        self._IO_scala = IOs.IO_scala()
        
                
        
    def SerialCommand(self,command):
        #setup - if a Serial object can't be created, a SerialException will be raised.
        while True:
            try:
                ser = serial.Serial(self.serialport, self.baud, timeout=self.timeout)
                #break out of while loop when connection is made
                break
            except serial.SerialException:
                print 'INFO [LampSwitch] waiting for device ' + self.serialport + ' to be available'
                time.sleep(3)
        ser.flushInput()        
        ser.write(command + self.sendtermchar)
        ser.close()
        return
        
    def SerialQuery(self,command):
        #setup - if a Serial object can't be created, a SerialException will be raised.
        while True:
            try:
                ser = serial.Serial(self.serialport, self.baud)
                #break out of while loop when connection is made
                break
            except serial.SerialException:
                print 'INFO [LampSwitch] waiting for device ' + self.serialport + ' to be available'
                time.sleep(3)
        ser.flushInput()        
        ser.write(command + self.sendtermchar)
        answer = ser.readline()
        ser.close()
        return answer[:-2]        

    def SelectHalogen(self):
        """Select the Halogen Tungsten Lamp"""
        try:
            if self._IO_scala.Is_CLAPS_on() is False:
                print "WARNING [LampSwitch.__init__] -- The CLAPS power is off, this is needed for the LampSwitch, I TURN CLAPS ON"
                self._IO_scala.switch_CLAPS_on()
        except:
            print "GetPortList failed... HaloGen thus forced to be switched on..."
            self._IO_scala.SetPortList("1111")
            
        return self.SerialCommand('1')
        
    def SelectXeArc(self):
        """Select the Xe Arc Lamp"""
        try:
            if self._IO_scala.Is_CLAPS_on() is False:
                print "WARNING [LampSwitch.__init__] -- The CLAPS power is off, this is needed for the LampSwitch, I TURN CLAPS ON"
                self._IO_scala.switch_CLAPS_on()
        except:
            print "GetPortList failed... HaloGen thus forced to be switched off..."
            self._IO_scala.SetPortList("1101")
            
        return self.SerialCommand('0')
        
    def GetInfo(self):
        """Return the system info"""
        return self.SerialQuery('*IDN?')   

    def GetSerialPort(self):
        return self.serialport
    
    def SetSerialPort(self, port):
        self.serialport = port
