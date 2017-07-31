#!/usr/bin/python


"""
 * pyNetIO.py
 * Python module for the Koukaam Netio-230C power supply controller
 *
 * Author: Akos Hoffmann <akos.hoffmann@gmail.com>
 * 
 * 
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 """
 
__version__ = '1.1.0'
__date__ = '2014-10-24'
__all__ = ["NetIOtn"]

import telnetlib
import hashlib
import serial
import time
import sys

from General_tools import timeout
 

class NetIO:
    """This class controlls the Netio-230C power supply controller via Telnet"""
    def __init__(self, HOST='192.168.10.100', PORT = '1234', USER = 'admin', PWD = 'admin',
                 SerPort='',SerPort_backup=None):
        """
        """
        self.host = HOST
        self.port = PORT
        self.user = USER
        self.pwd = PWD
        self.baud = 19200
        self.sendtermchar = "\r\n"
        self.rectermchar = "\r\n"
        self.timeout = 10

        self.serialport_main   = SerPort
        self.serialport_backup = SerPort_backup
        if self._select_port_() is False:
            print "*** MAJOR ERROR *** Can't initiate the netIO, most likely a python bug none of the USB are the good ones"
            sys.exit(6)

        
   
    #####################################
    #  --  RECOVERY AND SERPORT TOOLS --#
    #####################################
    def recover_netIO(self):
        """
        Try harder, then try the various USB port
        return True if it worked, False otherwise
        """
        print "netIO is sleepy... wait for it."
        time.sleep(2)
        try:
            portlist = self._GetPortList_()
            return True
        except:
            print "netIO is not responding... let's Try the other USB port"
        
        if self._select_port_():
                return True
        else:
            print "netIO recovery failed"
            print "Status 6"
            sys.exit(6)

    def _is_port_ok_(self,serport):
        """
        """
        self.serialport = serport
        try:
            p = self.GetPortList()
            return True
        except:
            return False

    def _select_port_(self):
        """
        This tools enqble to switch between _main and _backup in order to fix the USB issue 
        """
        self.serialport = self.serialport_main
        for p in [self.serialport_main,self.serialport_backup]:
            if self._is_port_ok_(p):
                return True

        return False

    #####################################
    #  ---  GENERAL FUNCTIONS       --- #
    #####################################      
    def SendCommandTn(self, CStr='alias'):
        """
        Send a command to the Netio-230C power supply controller via Telnet and return the answer.
        """
        m = hashlib.md5()
        tn = telnetlib.Telnet(self.host,self.port)
        hashstr = tn.read_until("\n", 2.0)[10:18]
        m.update(self.user+self.pwd+hashstr)
        tn.write('clogin '+ self.user + ' ' + m.hexdigest()+"\n")
        tn.read_until("\n", 2.0)
        tn.write(CStr+"\n")
        answer = tn.read_until("\n", 2.0).rstrip()[4:]
        tn.write("quit\n")
        #print answer
        tn.close()   
        return answer   

    def SendCommandRS232(self, command='alias'):
        """Send a command to the Netio-230C power supply controller via RS232 and return the answer."""
        #setup - if a Serial object can't be created, a SerialException will be raised.
        while True:
            try:
                ser = serial.Serial(self.serialport, self.baud)
                #break out of while loop when connection is made
                break
            except serial.SerialException:
                print 'waiting for device ' + self.serialport + ' to be available'
                time.sleep(3)
        #print 'connected...'
        ser.flushInput()  
 
        ser.write('login '+ self.user+ ' '+ self.pwd + ' ' + self.sendtermchar)
        answer = ser.readline()
        answer2 = ser.readline()
        answer3 = ser.readline()
        #print 'A1: '+answer
        #print 'A2: '+answer2  
        #print 'A3: '+answer3  
        if answer2[:3]  == '250' :
            ser.write(command + self.sendtermchar)
            answer = ser.readline()
            answer2 = ser.readline()
        #    print 'B1: '+answer
        #    print 'B2: '+answer2
        else: answer = 'ERROR'
        ser.write('quit' + self.sendtermchar)
        ser.close()
        return answer2.rstrip()[4:]  
    
    def SendCommand(self, CommandStr='alias'):
        if self.serialport == '':
            aa = self.SendCommandTn(CStr=CommandStr)
        else:
            aa = self.SendCommandRS232(command=CommandStr)
        return aa
    

    def GetPortList(self):
        """
        This function try to call _GetPortList_. If it fails, have some sleep and retry again
        """
        try:
            return self._GetPortList_()
        except:
            Is_recovered = self.recover_netIO()

        if Is_recovered:
            try:
                return self._GetPortList_()
            except:
                print "ERROR, you should not see that... The script said it recovered...."
                sys.exit(6)
        else:
            print "Sorry recovery Failed... I can't help... YOU SHOULD NOT SEE THAT"
            sys.exit(6)


    def SetPortList(self,List='uuuu'):
        """
        This function try to call _SetPortList_. If it fails, have some sleep and retry again
        """
        try:
            return self._SetPortList_(List)
        except:
            Is_recovered = self.recover_netIO()

        if Is_recovered:
            try:
                return self._SetPortList_(List)
            except:
                print "ERROR, you should not see that... The script said it recovered...."
                sys.exit(6)
        else:
            print "Sorry recovery Failed... I can't help..."
            sys.exit(6)
    
    
    def GetPortState(self):
        """
        This function try to call _GetPortState_. If it fails, have some sleep and retry again
        """
        try:
            return self._GetPortState_()
        except:
             Is_recovered = self.recover_netIO()

        if Is_recovered:
            try:
                return self._GetPortState_()
            except:
                print "ERROR, you should not see that... The script said it recovered...."
                sys.exit(6)
        else:
            print "Sorry recovery Failed... I can't help..."
            sys.exit(6)



    def SetPortState(self,PortNr=0, State=0):
        """
        This function try to call _GetPortState_. If it fails, have some sleep and retry again
        """
        try:
            return self._SetPortState_(PortNr=PortNr, State=State)
        except:
            Is_recovered = self.recover_netIO()
        
        if Is_recovered:
            try:
                return self._SetPortState_(PortNr=PortNr, State=State)
            except:
                print "ERROR, you should not see that... The script said it recovered...."
                sys.exit(6)
        else:
            print "Sorry recovery Failed... I can't help..."
            sys.exit(6)


    
    @timeout(7,Status_out=6,error_message="SetPortState is not responding...")
    def _SetPortState_(self, PortNr=0, State=0):
        """Change the Port state: 1 = turn on, 0 = turn off the power."""    
        return self.SendCommand(CommandStr='port %d %d' % (PortNr, State))


    
    @timeout(7,Status_out=6,error_message="SetPortList is not responding...")
    def _SetPortList_(self, List='uuuu'):
        """Change the state of all Port: 1=on, 0=off, u=no change."""        
        return self.SendCommand(CommandStr='port list ' +List)


    @timeout(7,Status_out=6,error_message="GetPortState is not responding...")
    def _GetPortState_(self, PortNr=0):
        """Ask for the Port state: 1=power is on, 0 = power is off."""    
        return self.SendCommand(CommandStr='port %d' % (PortNr,))
    
    
    @timeout(7,Status_out=6,error_message="GetPortList is not responding...")
    def _GetPortList_(self):
        """Ask the state of all Port: 1=on, 0=off, u=no change."""      
        return self.SendCommand(CommandStr='port list ')     

       
#if __name__ == '__main__':
    #nio = NetIO( HOST='192.168.178.44', PORT = '1234', USER = 'scala1', PWD = 'scala2013')
#    nio = NetIO( SerPort = '/dev/ttyUSB0')
#    print 'Device: '+ nio.SendCommand()
#    print 'Port state: '+ nio.GetPortList() 

    #print nio.SetPortList(List='1000') 
    #print nio.SetPortState(PortNr=1, State=1)
    
    #print nio.GetPortState(PortNr=1) 
    #print nio.GetPortState(PortNr=2) 
    #print nio.GetPortState(PortNr=3) 
    #print nio.GetPortState(PortNr=4) 
    #print nio.SetPortList(List='0000') 
    #print nio.GetPortList() 

"""
From the Koukaam user manual:
For login with secure password, you must first get the hash code from the device.
You get this either in the return code after connection via KSHELL or the CGI 
command hash. For calculation, the MD5 sum is used that has been calculated as 
the following sum <name><password><hash>. This is a 128b number (32 characters)
transmitted in a hexadecimal format.
The login command is: "clogin <name> <MD5sum>"
"""
