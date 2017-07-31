###########################################################
#  LOWER LEVEL LIBRARY THAT TALKS TO THE MONOCHROMATON    #
###########################################################
import subprocess
import time
# -- See pyserial
import serial

class CornerStone260:
    """This class controlls the Cornerstone 260 monochromator"""
    def __init__(self, port='/dev/ttyUSB1'):
        self.serialport = port  #windows: 'COMx', Linux: '/dev/<your_device_file>'
        self.baud = 9600
        self.sendtermchar = "\r\n"
        self.rectermchar = "\r\n"
        self.timeout = 10

    def SerialCommand(self,command):
        #setup - if a Serial object can't be created, a SerialException will be raised.
        while True:
            try:
                ser = serial.Serial(self.serialport, self.baud, timeout=self.timeout)
                #break out of while loop when connection is made
                break
            except serial.SerialException:
                print 'waiting for device ' + self.serialport + ' to be available'
                self.CS_Sleep(3)
                
        ser.flushInput()        
        ser.write(command + self.sendtermchar)
        answer = ser.readline()
        ser.close()
        return answer.upper()[:-2] == command.upper()
        
    def SerialQuery(self,command):
        #setup - if a Serial object can't be created, a SerialException will be raised.
        while True:
            try:
                ser = serial.Serial(self.serialport, self.baud)
                #break out of while loop when connection is made
                break
            except serial.SerialException:
                print 'waiting for device ' + self.serialport + ' to be available'
                self.CS_Sleep(3)
                
        ser.flushInput()        
        ser.write(command + self.sendtermchar)
        answer1 = ser.readline()
        answer2 = ser.readline()
        ser.close()
        return answer2[:-2]

    def CS_Sleep(self,timesleep_in_second):
        """
        """
        time.sleep(timesleep_in_second)
        
    def CS_Units_NM(self):
        """Specifies the operational units: nanometer"""
        return self.SerialCommand('UNITS NM')
        
    def CS_Units_UM(self):
        """Specifies the operational units: micrometer"""
        return self.SerialCommand('UNITS UM')
    
    def CS_Units_WN(self):
        """Specifies the operational units: wavenumbers (1/cm)"""
        return self.SerialCommand('UNITS WN')
    
    def CS_GetUnits(self):
        """Returns the operational units: NM, UM, WN"""
        return self.SerialQuery('UNITS?')[0:2]
 
    def CS_GoWave(self, position):
        """Moves the wavelength drive to the specified position (see units!)"""
        return self.SerialCommand('GOWAVE %f' % (position))
    
    def CS_GetWave(self):
        """Returns the wavelength drive position (see units!)"""
        return self.SerialQuery('WAVE?') 
 
    def CS_Calibrate(self, cal):
        """Define the current position as the wavelength specified in the numeric parameter"""
        return self.SerialCommand('CALIBRATE %f' % (cal))

    def CS_Abort(self):
        """Stops any wavelength motion immediately"""
        return self.SerialCommand('ABORT')   

    def CS_Step(self, n):
        """Moves the wavelength drive by the integer number of n"""
        return self.SerialCommand('STEP %d' % (n))
    
    def CS_GetStep(self):
        """Returns the wavelength drive position in steps"""
        return self.SerialQuery('STEP?')
        
    def CS_Grat(self,n):
        """Selects the grating Nr. 'n' """
        return self.SerialCommand('GRAT %d' % (n))
    
    def CS_GetGrat(self):
        """Returns the grating parameters"""
        return self.SerialQuery('GRAT?') 
        
    def CS_GratLabel(self,n,label=' '):
        """Defines the label of the grating Nr. 'n' """
        return self.SerialCommand('GRAT%dLABEL %s' % (n, label[:8]))
    
    def CS_GetLabel(self,n):
        """Returns the label of the grating"""
        return self.SerialQuery('GRAT%dLABEL?' % (n)) 

    def CS_GratZero(self,n,zero):
        """Defines the zero of the grating Nr. 'n' """
        return self.SerialCommand('GRAT%dZERO %f' % (n, zero))
    
    def CS_GetZero(self,n):
        """Returns the zero of the grating"""
        return self.SerialQuery('GRAT%dZERO?' % (n)) 	
        
    def CS_GratLines(self,n,lines):
        """Defines the lines of the grating Nr. 'n' """
        return self.SerialCommand('GRAT%dLINES %d' % (n, lines))
    
    def CS_GetLines(self,n):
        """Returns the label of the grating"""
        return self.SerialQuery('GRAT%dLINES?' % (n)) 

    def CS_GratFactor(self,n,factor):
        """Sets the calibration factor of the grating Nr. 'n' """
        return self.SerialCommand('GRAT%dFACTOR %f' % (n, factor))
    
    def CS_GetFactor(self,n):
        """Returns the calibration factor of the grating"""
        return self.SerialQuery('GRAT%dFACTOR?' % (n)) 

    def CS_GratOffset(self,n,offset):
        """Sets the calibration offset of the grating Nr. 'n' """
        return self.SerialCommand('GRAT%dOFFSET %f' % (n, offset))
    def CS_GetOffset(self,n):
        """Returns the calibration offset of the grating"""
        return self.SerialQuery('GRAT%dOFFSET?' % (n))     

    def CS_ShutterOpen(self):
        """Opens the shutter"""
        return self.SerialCommand('SHUTTER O')
    
    def CS_ShutterClose(self):
        """Closess the shutter"""
        return self.SerialCommand('SHUTTER C')
    
    def CS_GetShutter(self):
        """Returns the shutter state"""
        return self.SerialQuery('SHUTTER?')        

    def CS_Filter(self,n):
        """Moves the filter wheel to the position specified in 'n' """
        return self.SerialCommand('FILTER %d' % (n))
    
    def CS_GetFilter(self):
        """Returns the current filter position"""
        return self.SerialQuery('FILTER?')    

    def CS_OutPort(self,n):
        """Selects the output port"""
        return self.SerialCommand('OUTPORT %d' % (n))
    def CS_GetOutPort(self):
        """Returns the current out port"""
        return self.SerialQuery('OUTPORT?')             
    
    def CS_FilterLabel(self,n,label):
        """Defines the label of the filter Nr. 'n' """
        return self.SerialCommand('FILTER%dLABEL %s' % (n, label[:8]))
    def CS_GetFilterLabel(self,n):
        """Returns the label of the filter"""
        return self.SerialQuery('FILTER%dLABEL?' % (n))     

    def CS_GetInfo(self):
        """Returns the system info"""
        return self.SerialQuery('INFO?')   
    def CS_GetStatus(self):
        """Returns the status byte"""
        return self.SerialQuery('STB?') 
 
    def CS_GetError(self):
        """Returns the error code"""
        return self.SerialQuery('ERROR?')         
    
    def CS_GetSerialPort(self):
        return self.serialport
    
    def CS_SetSerialPort(self, port):
        self.serialport = port


   
if __name__ == '__main__':
    cs = CornerStone260( port = '/dev/ttyUSB1')
    print cs.GetInfo()
    
