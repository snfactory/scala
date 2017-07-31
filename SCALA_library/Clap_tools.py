#!/usr/bin/python

import numpy             as N
import matplotlib.pyplot as P

import scala.control.utils.bytes as scub
import scala.control.backend as scb
import struct
import time
import IO_SCALA         as IOs
import General_tools    as Gt
from General_tools    import timeout



############################################
# - THIS CONTROLS THE CLAPS              - #
############################################

###############################
# Procedure to use the CLAP   # 
#   - setup_clap              #
#   - prepare_the_ADC    #
#   - read_out_ADC (CAUTION here) #



Frequency_range = [0.06,500] # in kHz

def disconnect_all_the_claps():
    """
    """
    scb.close(0)
    scb.close(1)


    
###############################
# Simona's function. TBR      #
###############################
def Read_DC(**kwargs):
    """
    This is basically a example function
    """
    clap = CLAP(**kwargs)
    # -- here you setup the connection including the wordcount parameter
    clap.prepare_the_ADC()
    clap.read_out_ADC()
    clap.get_data_from_ADC()
    return clap

    
class CLAP():
    """
    """
    def __init__(self,device_number,
                 line_periods,frequency=1.,
                 channels="b1",auto_connexion=True,
                 Line_frequency=None,clipping_sigma=5,
                 verbose=True,debug=False):
        """
        Watch out the strength of the light for the channel
        Line_frequency is in Hz (50=europe / 60=US)

        line_periods = exptime(second) * 50Hz, must be a integer
        """
        # -- WHICH CLAP IT IS ? -- #
        # ---- General Variables --- #
        self.channels       = channels
        self.verbose        = verbose
        self.debug          = debug
        self.clipping_sigma = clipping_sigma
        # --------------------------------------- #
        # -- INPUTS                           --  #
        # --------------------------------------- #
        self.Frequency_range = Frequency_range
        if Line_frequency is None:
            if self.verbose:
                print "Default line frequency of %d Hz, see IO_SCALA"%IOs.Line_frequency
            self.Line_frequency = IOs.Line_frequency

        # ---- Device Number ---- #
        if device_number not in [0,1]:
            raise ValueError("The device number must be either 0 or 1 (%s)"%device_number)
    
        self.device_number          = int(device_number)
        
        # ---- Observation Frequency --- #
        self._setup_observation_frequency_(frequency)
        
        # ------------------------- #        
        # -- Constructor things  -- #
        # ------------------------- #        
        self.blocksize     = 32768
        self.clock_period  = 20.0e-9  # 20 ns
        self.FIFO_max_size =  8387583
        self.period        = int(self.period_second / self.clock_period)
    
        # ------------------------- #
        # -- Observation time    -- #
        # --   i.e. wordcount    -- #
        # ------------------------- #
        self._setup_observation_time_(line_periods)
        
        # -- Connexion -- #
        if auto_connexion:
            self.setup_clap()

        # -- Let's go Marko -- #
        if self.verbose:
            print "CLAP %d: Ready to go"%self.device_number
            
    # ------------------------ #
    # - Internal tools       - #
    # ------------------------ #
    def _load_channel_mask_(self):
        """
        This have to be changed - Not clean
        """
        self.channel_mask = 0x00
        if self.channels   in ["b0","g1","gain1"]:
            self.channel_mask |= 0x01
        elif self.channels in ["b1","g32","gain32"]:
            self.channel_mask |= 0x02
        elif self.channels in ["b2","tclap0","tempclap0"]:
            self.channel_mask |= 0x04
        elif self.channels in ["b3","tclap1","tempclap1"]:
            self.channel_mask |= 0x08
        elif self.channels in ["b4","tbe","tempbe"]:
            self.channel_mask |= 0x10
        elif self.channels in ["b5","lemo"]:
            self.channel_mask |= 0x20
        elif self.channels in ["b6","biasout","bias"]:
            self.channel_mask |= 0x40
        elif self.channels in ["b7","gndfe","groundfe"]:
            self.channel_mask |= 0x80
        else:
            raise ValueError("Sorry, I do not understand the given channel (%s) -- loop tool has been removed"%channem)
        
        # --- It used to have this shape --- #
        #if ("b0" in channels) or ("g1" in channels) or ("gain1" in channels):
        #    channel_mask |= 0x01

    @timeout(IOs.IO_timer_max_loading_Clap,Status_out=IOs.Error_status_clap)
    def _setup_connexion_(self):
        """
        """
        self._load_channel_mask_()
        
        # -- USB port -- #
        if self.device_number==0:
            
            scb.open(clapnum=self.device_number,
                     devsernum = '04 A',
                     debug = self.debug)
            
        elif self.device_number==1:
            scb.open(clapnum=self.device_number,
                            devsernum = '05 A',
                            debug = self.debug)
            
        else: # -- This should not happened -- #
            raise ValueError("Clap device should be either 0 or 1. At this stage, this error should not exist")
        if self.verbose:
            print "Claps Opened"
        # -- Reset HARD -- #
        scb.write(self.device_number,
                  0x1b, bytearray([1]))
        
        scb.write(self.device_number,
                  0x1c, bytearray([self.channel_mask]))
        # -- If you want loop to work, this should be 0x01 -- #
        scb.write(self.device_number,
                   0x1d, bytearray([0x00]))

    def _setup_observation_frequency_(self,frequency_in_kHz):
        """
        Frenquency *must be given* in kHz
        """
        if ("frequency" in dir(self)):
            if self.verbose:
                print "INFORMATION [CLAP (%d)._setup_observation_frequency_] -- You are changing the observation frequency"%self.device_number

        # -- FREQUENCY BOUNDARIES
        if frequency_in_kHz < self.Frequency_range[0] or frequency_in_kHz > self.Frequency_range[1]:
            raise ValueError("frequency should be between 1kHz and 500kHz (specified in kHz). %.1f given"%frequency_in_kHz)
        
        self.frequency              = frequency_in_kHz
        self.period_second          = 1./(1000.*self.frequency)
        self.samples_in_line_period = self.frequency*1000./self.Line_frequency
        
    def _setup_observation_time_(self,line_periods):
        """
        """
        if ("_wordcount" in dir(self)) and line_periods != self.line_periods:
            if self.verbose:
                print "INFORMATION [CLAP (%d)._setup_observation_time_] -- You are changing _wordcount (=number of observations)"%self.device_number
                
        if type(line_periods) != int:
            print "WARNING: CLAP(%s)._setup_observation_time_:  `line_periods` is not an integer, it is converted as such"
            line_periods = int(line_periods)
            
        self.line_periods            = line_periods
        # -- This "exposure_time_in_second" is only for user content -- #
        self.exposure_time_in_second = N.float(self.line_periods)/self.Line_frequency
        _wordcount_tmp    = int((self.line_periods+1) * self.samples_in_line_period+1)

        # -- Test the word counts --- #
        if _wordcount_tmp > self.FIFO_max_size:
            raise ValueError("wordcount (%d) too large (FIFO max size is %d)."%(self._wordcount,self.FIFO_max_size))
        
        self._wordcount = _wordcount_tmp
        
    def _remaining_(self):
        """
        """
        return scb.read_at(self.device_number,
                           0x17, 0x19)

    # ---- INTERNAL STEP FOR THE OBSERVATIONS ---- #
    def _ADC_to_FIFO_(self):
        """
        """
        self.time_ADC_to_FIFO_starts = time.time()

        daq_not_ready = True
        while daq_not_ready :
            daq_not_ready = scb.read(self.device_number, 0x0A)[0] & 0x01
            time.sleep(0.1)
        self.time_ADC_to_FIFO_ends = time.time()
        
    def _read_out_FIFO_(self):
        """
        """
        self.raw_data = bytearray()

        self.time_read_out_FIFO_starts = time.time()
        if self.verbose:
            print "INFO, CLAP %d -- Starting FIFO readout..."%self.device_number
        while (scb.read(self.device_number, 0x0A)[0] & 0x04):
            # How many remain to be read ?
            amount = self._remaining_()
            #print "remains: %d 2-byte words" % amount
            if amount <= 0:
                break
            if amount >= self.blocksize:
                size = 2 * self.blocksize
            else:
                size = 2 * amount
                
            rd = scb.read(self.device_number, 0x08, size)
            
            self.raw_data.extend(rd)
            # latency (is it useful ???) -- ask Simona or Arkos
            time.sleep(0.05)
            amount = self._remaining_()
            
        self.time_read_out_FIFO_ends = time.time()

    def _convert_raw_data_(self):
        """
        """
        fmt = "<%dh" % (len(self.raw_data) / 2)
        # -- These uncut_data have issue at the edge
        self.uncut_data = struct.unpack(fmt, str(self.raw_data))
        # -- Simona's hacking for edge correction -- #
        self.data = self.uncut_data[1: int(self.line_periods * self.samples_in_line_period+2)]
        # -------------------------------- #
        # - Useful parameters            - #
        # -------------------------------- #
        self.mean_data   = N.mean(self.data)
        self.median_data = N.median(self.data)
        
        self.nMAD_data   = N.median(N.abs(self.data - self.median_data)) * 1.4826
        self.std_data    = N.std(self.data)
        
        self.npts_data   = len(self.data)
        
        self.dmean_data  = self.std_data/N.sqrt(len(self.data)-1)
        
        # -------------------- #
        # -- sigma clipping -- #
        self.data_clipped = Gt.sigma_clipped_array(self.data,sigma=self.clipping_sigma)
        self.mean_clipped = N.mean(self.data_clipped)
        
                   
    # ------------------------ #
    # - General tools        - #
    # ------------------------ #
    def setup_clap(self):
        """
        """
        self._setup_connexion_()
        
        scb.write_at(self.device_number,
                     0x04, 0x05, self.period)
        
        scb.write(self.device_number,
                  0x06, bytearray([0]))
        scb.write_at(self.device_number, 0x14, 0x16,
                     self._wordcount)
        if self.verbose:
            print "Clap %s is connected "%self.device_number
    
    def disconnect_me(self):
        """
        """
        scb.close(self.device_number)
        
    def prepare_the_ADC(self):
        """
        """
        # -- How Many (How long) Observations -- #
        scb.write_at(self.device_number, 0x14, 0x16,
                     self._wordcount)
        
        scb.write(self.device_number,
                   0x1a, bytearray([1]))
        
    def read_out_ADC(self):
        """
        If several clap are used together, you have to do
        CLAP1.read_out()
        CLAP2.read_out()

        Nothing in between
        """
        self.time_readout = time.time()
        scb.write(self.device_number,
                   0x03, bytearray([0x02]))

    def get_data_from_ADC(self):
        """
        This will create the self.data file
        """
        self._ADC_to_FIFO_()
        self._read_out_FIFO_()
        self._convert_raw_data_()

    # ------------------------------- #
    # --  HIGH LEVEL FUNCTIONS     -- #
    # ------------------------------- #
    def get_mean_data(self):
        """
        """
        return self.mean_data,self.dmean_data

    def change_observation_time(self,new_line_periods):
        """
        """
        self._setup_observation_time_(new_line_periods)

    def change_observation_frequency(self,new_frequency_in_kHz):
        """
        """
        self._setup_observation_frequency_(new_frequency_in_kHz)
        # -- You have to change the wordcount then -- #
        self._setup_observation_time_(self.line_periods)
        # -- Everything is Ok -- #
        
    # -- This is what you need to get data informations
    def do_observation(self):
        """
        CAUTION, use this only if One clap is connected 
        """
        if self.verbose:
            print "CAUTION CLAP %d -- This must be used only if you observe with 1 CLAP"%self.device_number
            
        self.prepare_the_ADC()
        self.read_out_ADC()
        self.get_data_from_ADC()

    # --- OUTPUTS ---- #
    def write_data(self,fileout):
        """
        """
        print  "To Be Done"

        
    def Plot_data(self,savefile=None,dpi=150):
        """
        """
        fig = P.figure(figsize=[6,4])
        ax  = fig.add_axes([0.15,0.15,0.75,0.75])
        
        ax.plot(N.arange(len(self.data))*self.period_second,
                 self.data,'.k',zorder=3)
        ax.axhline(self.mean_data,ls="-",color=P.cm.Blues(0.8))
        ax.axhspan(self.mean_data-self.std_data,self.mean_data+self.std_data,
                   color=P.cm.Blues(0.5),alpha=0.6)
        
        ax.set_xlabel(r"$\mathrm{second}$",fontsize="large")
        ax.set_ylabel(r"$\mathrm{Analog\ to\ Digital\ Unit\; (ADU)}$",fontsize="large")
        ax.set_title(r"$\mathrm{Clap_%d\; ;\; %d\ line\ periods\ (%d\ Hz)\; ;\; channel %s}$"%(
            self.device_number,self.line_periods,self.Line_frequency,self.channels))
        
        Gt.savefile_reader(fig,savefile,dpi=dpi)
