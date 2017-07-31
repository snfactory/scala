#!/usr/bin/python

# ========================================= #
# ==      Rigault - Version 1.0           = #
# ========================================= #
import sys
import time
# -----  General Library  ------ #
import numpy as N
# ----- Low Level Library ------ #
from General_tools import timeout
import pyCorner260 as Corner
# ----- Scala Main Library ----- #
import IO_SCALA    as IOs
import LampSwitch  as LS

# ========================= #
# = MONOCHROMATOR LIMITS  = #
# ========================= #
MonoChromator_Wavelength_boundaries = [0,10020]



def Force_Wavelength_change(New_lbda):
    """
    """
    c= Corner.CornerStone260()
    c.CS_GoWave(New_lbda/10.)

def Clear_MonoChromator(verbose=True):
    """
    """
    M = MonoChromator(None,verbose=verbose,
                      check_up=False)
    M.CS_GoWave(400)
    M.change_wavelength(4000,check_up=False)
    try:
        M.change_wavelength(4300)
    except:
        try:
            M.change_wavelength(4300)
        except:
            print "MonoChromator stuck"
            sys.exit(1)
    
############################################
# - THIS CONTROLS THE MONOCHROMATOR      - #
############################################
class MonoChromator(Corner.CornerStone260):
    """
    This enhirate from the CornerStone260 that has all the basic control methods
    -> methods from Corner.CornerStone260 start with "CS_"
    -> example: CS_GoWave(lbda_in_nm) moves to the lbda_in_nm wavelength

    ** UNITS **: The basic unit is ANGSTROM, except for lower level functions (CS_...). 
    """
    # Note that the timeout return an error is more than
    # `IO_timer_max_loading` passes before the end of the function
    # It *usually* means that the MonoChromator is off or disconnected

    
    def __init__(self,wavelength,
                 verbose=True,snifs_mode=False,
                 starts_shutter_off=True,
                 check_up=True):
        """
        Wavelength in Angstrom. if None given, the current MonoChromator wavelength is used
        starts_shutter_off means that the shutter is closed at the end of the __init__.
        -> if False, nothing is done, i.e. The current shutter position is kept
        ----------
        - Loading time -- If more than `IOs.IO_timer_max_loading` is spent
        - to load this function, an error is returned. It *usually means that
        - the monochromator is off/disconnected.
        ----------
        """
        # - Technical setups - #
        self._setup_the_intrument_()
        self._load_current_status_()
        self._LampSwitch = LS.LSSM()
        self._IO_scala   = IOs.IO_scala(verbose=False)
        # - Generic stuff - #
        self.wavelength_boundaries = N.sort(MonoChromator_Wavelength_boundaries)
        self.verbose    = verbose
        self.snifs_mode = snifs_mode
        if self.snifs_mode:
            self.verbose = False
            
        # - Changes the wavelength to what have been requested
        self.change_wavelength(wavelength,check_up=check_up)
        
        if starts_shutter_off:
            self.switch_off_shutter()
        
    # ------------------------ #
    # -  Internal tools      - #
    # ------------------------ #
    @timeout(IOs.IO_timer_max_loading,Status_out=IOs.Error_status_Mono)
    def _load_current_status_(self):
        """
        This function loads the current_`$i` and `$i` to the current monochromator values
        -> $i={wavelength [\AA], grating, filter}
        The shutter status is also loaded (open/close/problem)
        """
        self.current_wavelength = N.float(self.CS_GetWave())*10
        self.wavelength         = self.current_wavelength
        self.current_grating    = int(self.CS_GetGrat().split(",")[0])
        self.Grating            = self.current_grating
        self.current_filter     = int(self.CS_GetFilter())
        self.Filter             = self.current_filter

        self.current_lamp       = "Unknown"
        
        if self.CS_GetShutter() == "O":
            self.shutter = "open"
        elif self.CS_GetShutter() == "C":
            self.shutter = "close"
        else:
            if self.snifs_mode:
                print "MonoChromator shutter"
                sys.exit(1)
            else:
                print "SCALA.MonoChromator._load_current_status_ : CS_GetShutter is nethier O or C.... strange"
                self.shutter = "problem"
            
                
    def _test_inputs_(self):
        """
        """
        if self.verbose:
            print "No Test inputs ready"

    def _setup_the_intrument_(self):
        """
        Port and setup definition are registered in IO_SCALA.py
        They are loading to the object
        """
        self.serialport   = IOs.Serial_port
        self.baud         = IOs.Serial_baud
        self.sendtermchar = "\r\n"
        self.rectermchar  = "\r\n"
        self.timeout      = 10

    def _restore_MonoChromator_(self,lbda):
        """
        """
        if self.snifs_mode or self.verbose:
            print "MonoChromator failed changing wavelength... Recovering ongoing..."


        self.Grating = 1
        self._change_Grating_(1)
        self.Filter = 4
        self._change_Filter_(4)

        self.CS_GoWave(500)
        self.wavelength = self.current_wavelength = 5000.
        
        self.change_wavelength(lbda,check_up=False)
        
        
    ##########################
    #  UPDATE THE INSTRUMENT #
    ##########################
    def _change_Wavelength_(self,lbda):
        """
        ** THIS FUNCTION SHOULD NOT BE USED BY ITSELF **
        (see change_wavelength and update_monochromator)
        
        This function tests and changes the current monocromator wavelength
        It has to be used together with _change_Grating_ and _change_Filter_
        
        """
        # - CS_* in nanometer, not Angstrom
        if lbda is None:
            if self.verbose:
                print "INFO SCALA.MonoChromator._change_Wavelength_: lbda is None, Class parameter set to current MonoChromator values"
            self.current_wavelength = N.float(self.CS_GetWave())*10
            
        else:
            self.CS_GoWave(lbda/10.)
            
            Lbda_Mono_AA = N.float(self.CS_GetWave())*10
            Delta_wave = N.abs(lbda-Lbda_Mono_AA)
            # -- FAILURE TEST -- #
            if Delta_wave>5:
                if self._change_failed_once_ is False:
                    if self.verbose:
                        print "Wavelength issue, let's retry %.1f"%lbda
                    self._change_failed_once_ = True
                    self._restore_MonoChromator_(lbda-10)
                    self._change_Wavelength_(lbda)
                    
            if Delta_wave>2 and Delta_wave<5:
                print N.round(lbda),N.round(Lbda_Mono_AA)
                # -- This "int" because the MonoChromator is not perfect,
                # -- so it do not exactly go where you asked -- #
                if self.verbose:
                    print "WARNING [SCALA.MonoChromator._check_up_] the current wavelengths are more than 2 AA away"%(self.lbda,Lbda_Mono_AA)
                    
            elif Delta_wave>5:
                if self.snifs_mode:
                    # -- Died because of the Wavelength shift -- #
                    sys.exit(2)
                    
                raise ValueError("The requested and current wavelengths are more than 5 AA away"%(self.lbda,Lbda_Mono_AA))
            
            self.current_wavelength = Lbda_Mono_AA
        
            if self.verbose and Lbda_Mono_AA != lbda:
                print "INFO SCALA.MonoChromator -- This MonoChromator reach the following wavelength %.1f (%.1f requested)."%(self.current_wavelength,lbda)
                print "--> Class parameters updated as such"
                
        self._change_failed_once_ = False
        self.wavelength = self.current_wavelength
        
    def _change_Grating_(self,Grating):
        """
        """
        self.CS_Grat(Grating)
        self.current_grating = Grating
        
    def _change_Filter_(self,Filter):
        """
        """
        if Filter is None:
            if verbose:
                print "You should now be using the Halogen lamp"
                print "ASK SIMONA if not"
        else:
            self.CS_Filter(Filter)
            
        self.current_filter = Filter

    def _check_up_(self):
        """
        The test that the current parameters match with the MonoChrometor ones
        """
        if N.round(self.current_wavelength/10.) != N.round(N.float(self.CS_GetWave())):
            raise ValueError("[SCALA.MonoChromator._check_up_] the current wavelength do not matchs (%d vs. %d)"%(self.current_wavelength,N.float(self.CS_GetWave())*10))
        
        if int(self.current_grating) != int(self.CS_GetGrat().split(",")[0]):
            raise ValueError("[SCALA.MonoChromator._check_up_] the current gratings do not matchs (%d vs. %d)"%(self.current_grating,int(self.CS_GetGrat())))
        
        if int(self.current_filter)  != int(self.CS_GetFilter()):
            raise ValueError("[SCALA.MonoChromator._check_up_] the current filters do not matchs (%d vs. %d)"%(self.current_filter,int(self.CS_GetFilter())))
            
    #########################
    #  GRATINGS AND FILTERS #
    #########################
    def _set_Grating_(self,update_monochromator=False, force_grating=None):
        """
        The Grating is changed as a function of the wavelength (self.wavelength)
        Grating 1 if <5220 AA. Grating 2 otherwise
        ---
        force_grating must be a integer (or None) within [1,2]
        
        See newport catalog
        """
        # === Force it 
        if force_grating is not None and force_grating in [1,2]:
            self.Grating = force_grating
        elif force_grating is not None:
            print "ERROR WRONG GRATING FORCED, should be 1 or 2 %s given"%force_grating
            raise ValueError("ERROR WRONG GRATING FORCED, should be 1 or 2 %s given"%force_grating)
        # === or not force it, that is the question
        else:
            # - Not that the wavelength test is made earlier - #
            if self.wavelength <5220:
                self.Grating = 1
            else:
                self.Grating = 2
            
        if update_monochromator:
            self.update_monoChromator()
            
        
    def _set_Filter_(self,update_monochromator=False, force_filter=None):
        """
        The Filter is changed as a function of the wavelength (self.wavelength)
        ---
        
        See newport catalog

        force_filter must be a integer (or None) within [1,2,3,4,5,6]
        """
        # === Force it 
        if force_filter is not None and force_filter in [1,2,3,4,5,6]:
            self.Filter = force_filter
            
        elif force_filter is not None:
            print "ERROR WRONG FILTER FORCED, should be in [1,2,3,4,5,6] %s given"%force_filter
            raise ValueError("ERROR WRONG GRATING FORCED, should be 1 or 2 %s given"%force_filter)
        
        # === or not force it, that is the question
        else:
            if self.wavelength <4500:
                self.Filter = 3
            #elif self.wavelength <5220:
            #    self.Filter = 4
            # - The grating changes in between, not the filter
            elif self.wavelength <6240:
                self.Filter = 4
            elif self.wavelength <7020:
                self.Filter = 1
            else:
                # -- the lamp should have change anyways... -- #
                self.Filter = 1
            
        if update_monochromator:
            self.update_monoChromator()
        
    def _set_Lamp_(self,force_lamp=None):
        """
        """
        # - forceing lamp?
        if force_lamp is not None:
            lamp_to_use = force_lamp.lower()
            if lamp_to_use not in  ["ha","halo","xe","xenon"]:
                raise ValueError("The force_lamp entry must be 'ha'/'halo' or 'xe'/'xenon' %s given"%force_lamp)
        # - If not which is your wavelength ?
        elif self.wavelength >=7020:
            lamp_to_use = "ha"
            
        else:
            lamp_to_use = "xe"

        # - Let's change the lamp
        if lamp_to_use in ["ha","halo"]:
            if self.verbose:
                print "HaloLamp asked"
                
            if self.current_lamp == "HaloLamp":
                if self.verbose:
                    print "HaloLamp already on"
                return
            
            # -------------------- #
            # -- SWITCH HALO ON -- #
            if self._IO_scala.SetPortList('1111') !="OK":
                print "SetPortList Failed Once... Let's try again by first calling GetPortList"
                sys.stdout.flush()
                time.sleep(1)
                try:
                    portlist = self._IO_scala.GetPortList()
                except:
                    print "GetPortList Failed too... let's try again SetPortList"
                    sys.stdout.flush()
                    time.sleep(3)
                
                if self._IO_scala.SetPortList('1111') != "OK":
                    print "Status %s"%IOs.Error_status_NetIO
                    sys.exit(IOs.Error_status_NetIO)
                    
            self._LampSwitch.SelectHalogen()
            self.current_lamp = "HaloLamp"
            
        else:                
            if self.verbose:
                print "XenonLamp asked"
                
            if self.current_lamp == "XenonLamp":
                if self.verbose:
                    print "XenonLamp already on"
                return
            
            # -- SWITCH HALO OFF -- #
            # -- HaloGene Issues  -- #
            if self._IO_scala.SetPortList('1101') !="OK":
                print "SetPortList Failed Once... Let's try again by first calling GetPortList"
                time.sleep(1)
                try:
                    portlist = self._IO_scala.GetPortList()
                except:
                    print  "GetPortList Failed too... let's try again SetPortList"
                    sys.stdout.flush()
                    time.sleep(3)
                    
                if self._IO_scala.SetPortList('1101')!="OK":
                    print "   WARNING: I can't Switch off the HaloLamp for now. It will stay on... Sorry"
                    sys.stdout.flush()
                    
            self._LampSwitch.SelectXeArc()
            self.current_lamp = "XenonLamp"
            
    ############################
    # ------------------------ #
    # - General tools        - #
    # ------------------------ #
    ############################
    def Is_Ready(self,try_again=True):
        """
        """
        self._check_up_()
        self.Status = self.CS_GetStatus()
        if self.Status == "00":
            return True
        
        time.sleep(3)
        if self.Is_Ready(try_again=False):
            return True
            
        print "Twice the MonoChromator said it wasn't ready"
        sys.exit(IOs.Error_status_Mono)
    
    def update_monoChromator(self,check_up=True,
                             force_grating=None, force_filter=None, force_lamp=None):
        """
        changes the Grating and the Filter if necessary

        check_up look for the values the grating, the filter and the wavelength registered
        in the MonoChromators it self (using lower_level tools) and check is things match.
        
        """
        self._set_Grating_(update_monochromator=False,force_grating=force_grating)
        self._set_Filter_( update_monochromator=False,force_filter=force_filter)
        self._set_Lamp_(force_lamp=force_lamp)
                   
        # -- Change the grating if needed -- #
        if int(self.current_grating) != int(self.Grating):
            if self.verbose:
                print "SCALA.Monochromator is changing the Grating"
                sys.stdout.flush()
            self._change_Grating_(self.Grating)

        # -- Change the filter if needed -- #
        if (self.Filter is None and self.current_filter is not None)  or \
            int(self.current_filter) != int(self.Filter):
            if self.verbose:
                print "SCALA.Monochromator is changing the Filter"
            self._change_Filter_(self.Filter)
            
        # -- Change the wavelength if needed -- #
        if int(self.current_wavelength) != int(self.wavelength):
            if self.verbose:
                print "SCALA.Monochromator is changing the wavelength"
            self._change_Wavelength_(self.wavelength)
            
        # ------------------ #
        # Is everything Ok ? #
        # ------------------ #
        if check_up and self.Is_Ready() is False:
            raise ValueError('Something is Wrong, status not equal to 00 %s (maybe check the wavelength)'%self.Status)
        
        # -- If you are here, then everything went well and the MonoChromator is ready to go -- #
        if self.verbose:
            print "SCALA.Monochromator I am ready !"
            
    def change_wavelength(self,new_lbda,check_up=True,
                          force_grating=None, force_filter=None, force_lamp=None):
        """
        USE THAT TO CHANGE WAVELENGTH
         
        it checks that the new wavelength is within the boundaries of the MonoC.
        then it calls update_monoChromator() that changes, the grating and filter (that you could force)
        and finally the 
        
        
        """
        self._change_failed_once_ = False
        if new_lbda is None:
            self.wavelength = self.current_wavelength
            if  self.verbose:
                print "SCALA.Monochromator No wavelength specified (None), current monochromator values have been set..."
                
        else:
            if new_lbda != 0  and new_lbda <self.wavelength_boundaries[0]:
                print "ERROR [MonoChromator.change_wavelength] the requested wavelength is lower than 3100 Angstrom"
                return
            if new_lbda != 0 and new_lbda >self.wavelength_boundaries[-1]:
                print "ERROR [MonoChromator.set_Grating] the current wavelength is greater than 10020 Angstrom"
                return
            if  self.verbose:
                print "SCALA.Monochromator You ask for a new wavelength..."
            
            self.wavelength = new_lbda
            
        self.update_monoChromator(check_up=check_up,
                                  force_grating=force_grating,
                                  force_filter=force_filter,
                                  force_lamp=force_lamp)

    def switch_on_shutter(self):
        """
        """
        if self.CS_GetShutter() == "O":
            self.shutter = "open"
            return
        # -- CS_ShutterOpen() change the shutter and returns True if things are Ok -- #
        if self.CS_ShutterOpen():
            self.shutter = "open"
        else:
            print "**ERROR** [SCALA.MonoChromator.switch_on_shutter] Something went wrong, the Shutter did not open"
            self.shutter = "problem"
            raise ValueError("The MonoChromator's shutter FAILED OPENING ")
        
    def switch_off_shutter(self):
        """
        """
        if self.CS_GetShutter() == "C":
            self.shutter = "close"
            return
        # -- CS_ShutterOpen() change the shutter and returns True if things are Ok -- #
        if self.CS_ShutterClose():
            self.shutter = "close"
        else:
            print "**ERROR** [SCALA.MonoChromator.switch_on_shutter] Something went wrong, the Shutter did not open"
            self.shutter = "problem"
            raise ValueError("The MonoChromator's shutter FAILED CLOSING ")
            
    ###################################
    # ------------------------------- #
    # - MAIN FUNCTION               - #
    # ------------------------------- #
    ###################################
    def expose__test_function(self,wavelength=None,exptime=0.5,verbose=True):
        """
        if wavelength is None, it gives a random value between 3500 and 8000 A
        """
        
        if wavelength is None:
            wavelength = (N.random.rand(1)*(9000-3500)+3500)[0]
            if verbose:
                print "To Test Go Wavelength %.1f"%wavelength
            
        self.change_wavelength(wavelength)

            
        # ---------------- #
        # -- MAIN Tools -- #
        # ---------------- #
        self.switch_on_shutter()
        # ----   Do your stuff    ---- #
        # here, for the example, sleep #
        self.CS_Sleep(exptime)
        # --  Once done, switch off -- #
        self.switch_off_shutter()

        
        

