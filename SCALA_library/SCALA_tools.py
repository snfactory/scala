#!/usr/bin/python

import pyfits as F

import Monochromator_tools as Mt
import Clap_tools          as Cl
import IO_SCALA            as IOs
from General_tools import timeout

import time
import sys
import numpy as N
import warnings
warnings.filterwarnings('ignore')


"""
VERSION: 18th Octobre

What does SCALA needs to run an experiment.


SCALA:
------
   - lamda         
   - exposure time 
   
   -> MonoChrometor
   -> CLAP (number of claps)
   -> LAMP

   => Spectra (+ header)
   
Monochrometors:
   - Wavelength -- Only VARIABLE
   - Shutter (open / close)
   - Filter  (2 filters, 3 cases (case without filter))
   - Grating

CLAP:
   - Line_periods -- ONLY VARIABLE (=exposure time in an integer number of line_frequency)
   - Frequency
   - Channels (mainly gain)
   - line_frequency (number fixed 50Hz in Fr 60Hz in US)

IO:
    - Mirror_lamp (Xe or Halo)
    - On/Off (Mono/lamps/Clap)

"""


class SCALA():
    """
    """
    def __init__(self,wavelength_array,exptime_array,
                 used_clap=[True,True],safemode=False,
                 verbose=True,snifs_mode=False,
                 background_mode=False,
                 kwargs_clap={}):
        """
        """
        self.wavelength_array = wavelength_array
        self.exptime_array    = exptime_array
        self.used_clap        = used_clap
        self.safemode         = safemode
        self.verbose          = verbose
        self.snifs_mode       = snifs_mode
        self._background_mode  = background_mode
        if self.snifs_mode:
            self.verbose = False
            
        #self._test_inputs_()
        # -------------------------- #
        # -- Load the instruments -- #
        # -------------------------- #
        self._setup_scala_(kwargs_clap=kwargs_clap)
    
        self._check_up_()
        if self.snifs_mode:
            print "SCALA loaded"
            sys.stdout.flush()
            

    # ------------------------ #
    # -  Internal tools      - #
    # ------------------------ #
    ################
    #  SETUPS      #
    ################
    #@timeout(IOs.SCALA_max_loading_time)
    def _setup_scala_(self,kwargs_clap = {}):
        """
        """
        self._setup_MonoChromator_()
        self._setup_Claps_(**kwargs_clap)
        self._setup_IO_()
        self.Key_is_scala_ready = False
        
    def _setup_MonoChromator_(self,lbda=None):
        """
        This Will define "self.Mono"
        """
        if self._background_mode:
            self.Mono = None
        else:
            self.Mono = Mt.MonoChromator(lbda,verbose=self.verbose)

    def _setup_Claps_(self,line_periods=None,**kwargs):
        """
        This Will define "self.Clap0" and "self.Clap1"
        --> see used_clap to know which is/are used
        
        **kwargs = {frequency=250,Line_frequency=None,
                    channels="b0",auto_connexion=True,
                    verbose=True}
                    
        --> see Clap_tools.CLAP.__init__()
        
        """
        # Default Line_periods = Line_frequency, i.e. 1 second #
        if line_periods is None:
            line_periods = IOs.Line_frequency

        # --- CLAP 0 --- #
        if self.used_clap[0]:
            self.Clap0 = Cl.CLAP(0,line_periods,
                                 verbose=self.verbose,
                                 **kwargs)
        else:
            self.Clap0 = None
            
        # --- CLAP # --- #            
        if self.used_clap[1]:
            self.Clap1 = Cl.CLAP(1,line_periods,
                                 verbose=self.verbose,
                                 **kwargs)
        else:
            self.Clap1 = None

    def _setup_IO_(self):
        """
        """
        self.IO = IOs.IO_scala(verbose=self.verbose)
        
    ##############################
    #  SCALA CHECK UPS           #
    ##############################
    def _check_up_(self):
        """
        """
        if self.safemode is False:
            if self.verbose:
                print "No Check up"
                sys.stdout.flush()
                
            self.Key_is_scala_ready = True
            return
        
        if self.verbose:
            print "*** SCALA._check_up_: WARNING THE IO TEST IS NOT COMPLET YET ***"
        
        if self.IO.Is_MonoChrometor_on is False:
            if self.snifs_mode:
                sys.exit(IOs.Error_status_Mono)
            else:
                print "SCALA._check_up_(): The MonoChromator is off"
                self.Key_is_scala_ready = False
                return
            
        if self.IO.Is_XeLamp_on is False and self._background_mode is False:
            if self.snifs_mode:
                sys.exit(IOs.Error_status_Xe)
            else:
                print "SCALA._check_up_(): The Xenon Lamp is off"
                self.Key_is_scala_ready = False
                return
        # ------------------------ #
        # MonoChromator          - #
        # ------------------------ #
        if self._background_mode is False:
            if self.Mono.Is_Ready() is False:
                if self.Mono.Is_Ready() is False:
                    if self.snifs_mode:
                        print "Status %d"%IOs.Error_status_Mono
                        sys.exit(IOs.Error_status_Mono)
                    else:
                        print "SCALA._check_up_(): The MonoChromator is not ready"
                        self.Key_is_scala_ready = False
                        return

        # ------------------------ #
        # CLAP                   - #
        # ------------------------ #
        if self.verbose:
            print "*** SCALA._check_up_: WARNING: No Test for Clap ***"
        if self.Clap0 is None and self.Clap1 is None:
            print "SCALA._check_up_(): No Clap avialable, both are None"
            self.Key_is_scala_ready = False
            return
        
        self.Key_is_scala_ready = True
        
    ##############################
    #  Internal CLAP functions   #
    ##############################
    def _Set_claps_observation_time_(self,new_observation_time_in_sec):
        """
        """
        new_line_periods = new_observation_time_in_sec*IOs.Line_frequency
        
        if self.Clap0 is not None:
            self.Clap0.change_observation_time( int(new_line_periods))
            self.Effective_clap_exposure_time = self.Clap0.exposure_time_in_second
            
        if self.Clap1 is not None:
            self.Clap1.change_observation_time( int(new_line_periods))
            self.Effective_clap_exposure_time = self.Clap1.exposure_time_in_second
            
    def _Prepare_claps_(self):
        """
        """
        if self.Clap0 is None and self.Clap1 is None:
            print "SCALA._Prepare_claps_(): No Clap avialable, both are None"
            self.Key_is_scala_ready = False
            
        if self.Clap0 is not None:
            self.Clap0.prepare_the_ADC()
            
        if self.Clap1 is not None:
            self.Clap1.prepare_the_ADC()

    def _read_out_claps_ADC_(self,wait_unit_the_end=True):
        """
        """
        if self.Clap0 is not None:
            self.Clap0.read_out_ADC()
            
        if self.Clap1 is not None:
            self.Clap1.read_out_ADC()
            
        if wait_unit_the_end:
            # -- Do not do anything until the clap did the exposure -- #
            time.sleep(self.Effective_clap_exposure_time)
        

    ############################
    # -  SCALA METHODS       - #
    ############################
    def Disconnect_claps(self):
        """
        """
        if self.Clap0 is not None:
            self.Clap0.disconnect_me()
            self.Clap0 = None
            
        if self.Clap1 is not None:
            self.Clap1.disconnect_me()
            self.Clap1 = None
        
        if self.Clap0 is None and self.Clap1 is None:
            if self.verbose:
                print "WARNING --  No Clap avialable, both are None"
                
            self.Key_is_scala_ready = False
            
    def Connect_claps(self,used_clap,**kwargs):
        """
        used_clap must be [bool,bool]
        """
        self.Disconnect_claps()
        self.used_clap=used_clap
        self._setup_Claps_(**kwargs)
        
    def _Reformate_data_(self,data_):
        """
        """
        max_size = N.max([len(d) for d in data_])
        Nbins    = len(data_)
        Formated_data = N.ones((Nbins,max_size))*N.NaN
        for i in range(Nbins):
            Formated_data[i][:len(data_[i])] = data_[i]
            
        return Formated_data
        
    def _writeto_clap_(self,Nclap, savefile,clobber=True):
        """
        """
        clap = eval("self.Clap%d"%Nclap)
        hdu = F.PrimaryHDU(self._Reformate_data_(eval("self.Data_Clap%d"%Nclap)))
        
        T_Cstarts,T_swon,T_soff,T_Cstop = N.asarray(self.Data_times).T
        t_zero = T_Cstarts[0]
        col_lbda      = F.Column(name='LBDA',      format='E', array=self.Observed_lbda, unit="Angstrom")
        col_expo      = F.Column(name='EXPTIME',   format='E', array=self.Exposure_times,unit="second")
        col_TimeStar  = F.Column(name='TIMESTAR',  format='E', array=N.asarray(T_Cstarts) - t_zero,  unit="second")
        col_TimeOn    = F.Column(name='TIMEON',    format='E', array=N.asarray(T_swon   ) - t_zero,  unit="second")
        col_TimeOff   = F.Column(name='TIMEOFF',   format='E', array=N.asarray(T_soff   ) - t_zero,  unit="second")
        col_TimeStop  = F.Column(name='TIMESTOP',  format='E', array=N.asarray(T_Cstop  ) - t_zero,  unit="second")
        
        tbhdu         = F.new_table([col_lbda,col_expo,col_TimeStar,col_TimeOn,col_TimeOff,col_TimeStop])
        # ------------------- #
        # -- Primery HDU   -- #
        # ------------------- #
        hdu.header.update("NAXIS",1,"Number of dimension per HDU")
        hdu.header.update('NAXIS1',len(self.Observed_lbda),"Number of Wavelength bins, see 'WAVELENGTH' Table")
        if len(self.Observed_lbda)>1:
            hdu.header.update("CDELT1",self.Observed_lbda[1]-self.Observed_lbda[0],"CAUTION COULD BE VARIABLE, see 'WAVELENGTH' Table")
        else:
            hdu.header.update("CDELT1",None,"Only 1 Wavelength taken")
            
        hdu.header.update("CRVAL1",N.min(self.Observed_lbda),"Smaller wavelength, see 'WAVELENGTH' Table")
        hdu.header.update("UNITS","ADU","Analog to Digital Unit (integers)")
        
        # -- SNIFS related information -- #
        hdu.header.update("SFCLASS", 1 ,"To bypass the check of production")
            
        # -- Tables information -- #
        hdu.header.update("TABLES" ,6          ,"Number of tables associated to the PrimaryHDU")
        hdu.header.update("TABLES1","WAVELENGTH","Proper Wavelength array used")
        hdu.header.update("TABLES2","EXPTIME"   ,"Proper Exposure time array used (in second)")
        hdu.header.update("TABLES3","TIME_START","time.time() just *before* the ADC read_out")
        hdu.header.update("TABLES4","TIME_ON",   "time.time() just *before* swtiching On the Mono Shutter")
        hdu.header.update("TABLES5","TIME_OFF",   "time.time() just *after* swtiching Off the Mono Shutter")
        hdu.header.update("TABLES6","TIME_STOP","time.time() just *after* the ADC read_out")
        hdu.header.update("LOGTZERO","%.14f"%N.log10(t_zero),"log10(Time_zero), time registered have been subtracted bythis number ")
        hdu.header.update("CLAP_ID", clap.device_number,"Clap device 0 or 1")
        hdu.header.update("CLAPFREQ",clap.frequency,"Number of points per second taken by the CLAP (in kHz)")
        hdu.header.update("LINEFREQ",clap.Line_frequency,"Frequency of the electric Lines (50Hz=EU / 60Hz=US)")
        hdu.header.update("CLAPCHAN",clap.channels,"b0 = gain of 1;b0 = gain of 32, ... see Clap_tools ")
        # --------------- #
        # -- Clap info -- #
        if self.Clap0 is None:
            hdu.header.update("CLAP0",0,"1 if used, 0 if not")
        else:
            hdu.header.update("CLAP0",1,"1 if used, 0 if not")
        if self.Clap1 is None:
            hdu.header.update("CLAP1",0,"1 if used, 0 if not")
        else:
            hdu.header.update("CLAP1",1,"1 if used, 0 if not")
                
        # ------------------- #
        # -- DataFormat    -- #
        # ------------------- #
        hdu.header.update("DATAFMT","bkg_DATA_bkg","You record 1 background point after and before the exposure")
        # ------------------- #
        # -- MonoChromator -- #
        # ------------------- #
        hdu.header.update("MONOGRAT",None,"Variable, See 'WAVELENGTH' table and MonoChromator_tools.py")
        hdu.header.update("MONOFILT",None,"Variable, See 'WAVELENGTH' table and MonoChromator_tools.py")
        hdu.header.update("LAMP",    None,"Variable, Xenon Lamp if lbda smaller than 7000 / Halo otherwise")
        # ------------------- #
        # -- General_Run   -- #
        # ------------------- #
        hdu.header.update("FAILURE",self._Failure_flag_,"None = All went Fine, Wavelengths show which failed, -1 Means Epic Failure")
        ###############
        #  END        #
        ###############
        hdulist = F.HDUList([hdu, tbhdu])
        if len(savefile.split(".")) >1 and savefile.split(".")[-1]=="fits":
            savefile_name = "scala_clap%d_%s"%(clap.device_number,savefile)
        else:
            savefile_name = "SC%d_%s.fits"%(clap.device_number,savefile)

        print "Data are saved in %s"%savefile_name
        hdulist.writeto(savefile_name, clobber=clobber)
            
    def writeto(self,savefile,clobber=True):
        """
        savefile add the ".fits"
        """
        import pyfits as F
        
        if ("Data_Clap0" not in dir(self)):
            if self.snifs_mode:
                sys.exit(IOs.Error_status_Scala)
            else:
                print "ERROR [SCALA.writeto] you never run 'do_exposures', NO DATA TO SAVE"
                return

        # ========================== #
        # === SAVING OF THE DATA === #
        # ========================== #            
        [self._writeto_clap_(Nclap, savefile,clobber=clobber) for Nclap in range(2)]

        
            
    ############################
    # -  SCALA MAIN TOOLS    - #
    ############################
    def Take_background(self,exposure_time,try_again_if_fails=True):
        """
        """
        if self.Key_is_scala_ready is False:
            if try_again_if_fails:
                self.Take_background(exposure_time,try_again_if_fails=False)
                
            if self.snifs_mode:
                sys.exit(IOs.Error_status_Scala)
                
            if self.verbose:
                print "ERROR [SCALA.Expose]: Apparently, Scala is not ready (self.Key_is_scala_ready is False) -- Check_up Scala !"
                return
            
        self._exposure_time         = exposure_time
        # --- Update the Claps for the given exposure time --- #
        self.TIME_Stars_CLAP = time.time()
        self._Set_claps_observation_time_(exposure_time)
        self._Prepare_claps_()
        # -- EXPOSURE WITHOUT OPENING THE SHUTTER
        self.TIME_Stars_Exposure = time.time()
        
        self._read_out_claps_ADC_(wait_unit_the_end=True)
        
        self.TIME_Ends_Exposure = time.time()
        self.TIME_Ends_CLAP = time.time()
        # -------------------------------- #
        # -- Start collecting the data  -- #
        self.save_continuous_data()
        print "   (Data saved)"
        sys.stdout.flush()

    def do_backgrounds(self,exptime_array=None,
                       savefile=None):
        """
        This function takes a background for each given exposureTime in  exptime_array.
        if savefile is not None, This calls self.writeto(savefile+".fits") 
        
        --------
        Clap data are registered in             
        """
        # --------- INPUTS --------- #
        if exptime_array is not None:
            self.exptime_array = exptime_array
            
        ##############################
        # --     So let's go      -- #
        ##############################
        self._Failure_flag_ = None
        # ----------------- #
        # -- Da BKGD LOOP - #
        # ----------------- #
        for i,etime in enumerate(self.exptime_array):
            print "ongoing background of %.1f secondes (%d/%d)"%(etime,i+1,len(self.exptime_array))
            try:
                self.Take_background(etime)
            except:
                print "  This exposure loop %d/%d FAILED. Data of this loop not recorded."%(i+1,len(self.exptime_array))
                if hasattr(self._Failure_flag_, '__iter__'):
                    self._Failure_flag_.append(i)
                else:
                    self._Failure_flag_ = [i]
        
        # ----------------- #
        # -- SAVING DATA -- #
        # ----------------- #
        if savefile is False:
            print "WARNING [SCALA.do_exposures] -- No Fits file has been registered, savefile is False"
            return
        
        if savefile is None:
            if self.verbose:
                print "INFORMATION [SCALA.do_backgounds] -- Default savefile value assigned to the fits file"
            savefile= IOs.assign_prod_name()
            print "       --> %s"%savefile
            
        self.writeto(savefile)

        
        
    def do_exposures(self,wavelength_array=None,exptime_array=None,
                     background_time=2,
                     savefile=None,
                     force_filter=None,force_grating=None, force_lamp=None):
        """
        This function scans the wavelength_array and exptime_array and "Expose" if time.
        if savefile is not None, This calls self.writeto(savefile+".fits")
        
        --------
        Clap data are registered in 
        """
        # --------- INPUTS --------- #
        if wavelength_array is not None:
            self.wavelength_array = wavelength_array
            
        if exptime_array is not None:
            self.exptime_array = exptime_array

        # -- Does it make sense ? -- #
        if N.shape(self.wavelength_array) != N.shape(self.exptime_array) or N.shape(self.exptime_array) ==():
            if self.snifs_mode:
                print "Wavelength--Exposure time issue"
                print "Status %d"%IOs.Error_status_Scala
                sys.exit(IOs.Error_status_Scala)
            else:
                raise ValueError("Either wavelength_array does not have the same shape as exptime_array, or both are None...")
        ##############################
        # --     So let's go      -- #
        ##############################
        self._Failure_flag_ = None
        
        for i,lbda in enumerate(self.wavelength_array):
            expo = self.exptime_array[i]
            print "%d/%d - %.1f A - %d second expo"%(i+1,len(self.wavelength_array),lbda,expo)
            sys.stdout.flush()
            # ------------------------ #
            # -- Check if Mono Ready - #
            # ------------------------ #
            if self.Mono.Is_Ready() is False:
                if self.Mono.Is_Ready() is False:
                    print " ERROR -- The MonoChromator is not ready (Twice)"
                    print "Status %d"%IOs.Error_status_Mono
                    print "  I stop the function. Data will be saved."
                    break
            # --------------------- #
            # -- Loop with saving - #
            # --------------------- #
            try:
                self.Continuous_exposure(lbda,expo,background_time,
                                         force_filter=force_filter,
                                         force_grating=force_grating,
                                         force_lamp=force_lamp)
                
            except:
                print "  This exposure loop %d/%d FAILED. Data of this loop not recorded."%(i+1,len(self.wavelength_array))
                if hasattr(self._Failure_flag_, '__iter__'):
                    self._Failure_flag_.append(lbda)
                else:
                    self._Failure_flag_ = [lbda]
                # -- Better to restore the MonoChromator -- #
                print "   I am running the recovery of the monochromator"
                sys.stdout.flush()
                try:
                    self.Mono._restore_MonoChromator_(self.wavelength_array[i])
                except:
                    print "MAJOR FAILURE... I Quite the Exposure loop and register what we already have !"
                    self._Failure_flag_ = -1
                    break
                continue
            
            # -- If everything went well, record the data -- #
            self.save_continuous_data()
            print "   (Data saved)"
            sys.stdout.flush()
        
        # ----------------- #
        # -- SAVING DATA -- #
        # ----------------- #
        if savefile is False:
            print "WARNING [SCALA.do_exposures] -- No Fits file has been registered, savefile is False"
            return
        
        if savefile is None:
            if self.verbose:
                print "INFORMATION [SCALA.do_exposures] -- Default savefile value assigned to the fits file"
            savefile= IOs.assign_prod_name()
            print "       --> %s"%savefile
            
        self.writeto(savefile)


    def Continuous_exposure(self,lbda,
                              exposure_time,background_time=2,
                              verbose=True,**kwargs):
        """
        **kwargs goes to change wvalength like force_blabla
        """
        Success = self.Check_SCALA(True)
        if Success is False:
            self.Check_SCALA(False)
        
        # -- Go to the good Wavelength -- #
        self.Mono.change_wavelength(lbda,**kwargs)

        Success = self.Check_SCALA(True)
        if Success is False:
            self.Check_SCALA(False)
            
        # -- Prepare the CLAPS -- #
        # -- Timing 
        self._max_shutter_time      = 1 # 1 second
        self._background_time       = background_time
        self._exposure_time         = exposure_time
        self._total_continuous_time = self._exposure_time + self._background_time*2 + self._max_shutter_time * 2
        # -- Settings 
        self._Set_claps_observation_time_(self._total_continuous_time)
        
        self._Prepare_claps_()
        
        if verbose:
            print "The Clap start their exposures. %.1f s in total"%self.Effective_clap_exposure_time

        # -- The Clap Starts their recording -- #
        self.TIME_Stars_CLAP = time.time()
        self._read_out_claps_ADC_(wait_unit_the_end=False)
        
        # -- FIRST BACKGROUD 
        time.sleep(self._background_time)
        print "   (Background taken - Exposure ongoing)"
        sys.stdout.flush()
        
        # -- THE EXPOSURE ITSELF
        self.TIME_Stars_Exposure = time.time()
        self.Mono.switch_on_shutter()
        
        time.sleep(self._exposure_time)

        self.Mono.switch_off_shutter()
        self.TIME_Ends_Exposure = time.time()

        remaining_time = self._total_continuous_time - (time.time() - self.TIME_Stars_CLAP)
        
        if remaining_time<0:
            raise ValueError("FATAL ERROR, Not enough time for the last background. ")
        
        print "   (Exposure taken - 2nd Background ongoing (%.1f s))"%remaining_time
        sys.stdout.flush()

        # -- Second BACKGROUD
        
        time.sleep(remaining_time)
        print "   (2nd Background taken -> Data saving)"
        sys.stdout.flush()
        self.TIME_Ends_CLAP = time.time()

        
    def save_continuous_data(self):
        """
        """
        if "Data_Clap0" not in dir(self):
            self.Data_Clap0 = []
        if "Data_Clap1" not in dir(self):
            self.Data_Clap1 = []
        if "Data_times" not in dir(self):
            self.Data_times = []
        if "Observed_lbda" not in dir(self):
            self.Observed_lbda = []
        if "Exposure_times" not in dir(self):
            self.Exposure_times = []
            
        # === CLAP 0 === #    
        if self.Clap0 is not None:
            self.Clap0.get_data_from_ADC()
            self.Data_Clap0.append(self.Clap0.data)
        else:
            self.Data_Clap0.append(None)
            
        # === CLAP 1 === #    
        if self.Clap1 is not None:
            self.Clap1.get_data_from_ADC()
            self.Data_Clap1.append(self.Clap1.data)
        else:
            self.Data_Clap1.append(None)

        # == Wavelength == #
        if self._background_mode:
            self.Observed_lbda.append(0)
        else:
            self.Observed_lbda.append(self.Mono.wavelength)
        
        # === TIMING === #
        self.Data_times.append([self.TIME_Stars_CLAP,self.TIME_Stars_Exposure,
                                self.TIME_Ends_Exposure,self.TIME_Ends_CLAP])
        
        # === Exposure Time == #
        self.Exposure_times.append(self._exposure_time)
        
    def Check_SCALA(self,try_again_if_fails):
        """
        """
        # ------------------------ #
        # -- Check if Mono Ready - #
        # ------------------------ #
    
        # -- Mono, Are you ready ? -- 
        if self.Mono.Is_Ready() is False:
            self.Mono.CS_sleep(3)
            if self.Mono.Is_Ready() is False:
                print "".center(75,"*")
                print " SCALA [Expose]: MonoChromator is not ready. I am stoping the function ".center(75,"*")
                print "".center(75,"*")
                print "Status %d"%IOs.Error_status_Mono
                sys.exit(IOs.Error_status_Scala)
                
        if self.Key_is_scala_ready is False:
            if try_again_if_fails:
                return False
                
            if self.snifs_mode:
                sys.exit(IOs.Error_status_Scala)
                
            if self.verbose:
                print "ERROR [SCALA.Expose]: Apparently, Scala is not ready (self.Key_is_scala_ready is False) -- Check_up Scala !"
                return
