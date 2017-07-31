#!/usr/bin/python

import numpy       as N
import IO_SCALA    as IOs

#################################
# -- BASICS INPUT           --- #
#################################

# --- WARNING SCALA_expose options WINS
IntraRun_Incremantation = 500. # Next wavelength step inside the same run (i.e., before SNIFS' readout)
ExtraRun_Incremantation = 180. # Next wavelength step for the next run (i.e., after SNIFS' readout)
# -- SNIFS B channel -- #
B_channel_first_lbda    = 3330.
B_channel_last_lbda     = 5200.
# -- SNIFS R channel -- #
R_channel_first_lbda    = 5000.
R_channel_last_lbda     = 10000.

# -- Calibration Wavelengths -- #
BlueCalibrationWavelength = N.asarray([3510, 3690, 4290, 4890])
RedCalibrationWavelength  = N.asarray([5490, 6510, 7110, 8100, 9010, 9900])

#################################
# -- ARRAY GENERATIONS      --- #
#################################
# ------------------- #
# -- Wavelength    -- #
# ------------------- #
def get_ExtraRunStep(ExtraRunStep_In=None):
    """
    This function define the Extra-Interpolation run. e.g. when b1->b2
    ----
    return float
    """
    if ExtraRunStep_In is None:
        return ExtraRun_Incremantation
    
    return ExtraRunStep_In

def get_IntraRunStep(IntraRunStep_In=None):
    """
    This function define the Intra-Interpolation run. e.g. inside b1
    ----
    return float
    """
    if IntraRunStep_In is None:
        return IntraRun_Incremantation
    
    return IntraRunStep_In


def Read_wavelength_input(wavelength_input,verbose=True,
                          ExtraRunStep=None,
                          IntraRunStep=None,
                          start_offset = 0,
                          addCalibrationRun=False):
    """

      -- wavelength_input [string]: == Various parsing Format allowed ==
           -> 1 string of a float   [e.g., '3452.3']
           -> 2 values split by ':' ['lbda_min:lbda_max'] (see IntraRunStep f)
           -> N values split by ',' ['lbda_1,lbda_2,lbda_3,...lbda_N']
           -> keywords starting with b or r (see parse_SNIFS_BR_input/Get_ith_array)
               ** This last is for SNIFS usage **
           
      -- ExtraRunStep [float in AA]: for keywords (SNIFS)
          Step between 2 runs (not inside a run). e.g. between b1 and b2

          
      -- IntraRunStep [float in AA]: for keywords (SNIFS) or min:max options
           Step between 2 wavelengths inside the same run.
           ** WARNING: Change that with great CAUTION **

      -- start_offset [float in AA]: for keywords (SNIFS)
           Do not start the run at the given default value (see B(R)_channel_first_lbda) but
           add this offset to it.
           (e.g. if blue is 3330 and start_offset=90, this will actually starts at 3330+90=3420)
    
      -- addCalibrationRun [bool]: for keywords (SNIFS)
          This will add, at the end of the keyword loop (like b1,b2...) an extra run
          with the wavelength registered in Blue(Red)CalibrationWavelength.
          
    -----
    returns float-array [of wavelength in AA]
    """
    ExtraRunStep = get_ExtraRunStep(ExtraRunStep)
    IntraRunStep = get_IntraRunStep(IntraRunStep)
    
    # ----------------------- #
    # - N listed Wavelengths  #
    # ----------------------- #
    if ',' in wavelength_input:
        if verbose:
            print "INFO [SCALA_expose.Read_wavelength_input] you give manual Wavelengths (',')"
        try:
            wavelength_array = N.asarray(wavelength_input.split(','),dtype="float")
        except:
            raise ValueError("The Manual Wavelength input is unparsable in float. It shoud be lbda1,lbda2,..,lbdaN [in Angstrom]")
        return wavelength_array
    
    # ----------------------- #
    # - Min:Max Wavelengths   #
    # ----------------------- #
    if ':' in wavelength_input:
        if verbose:
            print "INFO [SCALA_expose.Read_wavelength_input] you give range Wavelengths ('Min:Max')"
        try:
            wavelength_array = N.asarray(wavelength_input.split(':'),dtype="float")
        except:
            raise ValueError("The Manual Wavelength input is unparsable in float. It shoud be lbda_min:lbda_max [in Angstrom]")
        if len(wavelength_array)!=2:
            raise ValueError("The Manual Wavelength input is unparsable MUST BE 2 WAVELENGTHS: lbda_min:lbda_max [in Angstrom]")

        minW,maxW = N.min(wavelength_array),N.max(wavelength_array)
        wavelength_array = N.linspace(minW,maxW,(maxW-minW)/IntraRunStep+1)
        
        return wavelength_array

    # --------------------------- 
    # - Updated parse version   - 
    # - Allow any kind of b/r*ith 
    # ith don't have limited size
    # --------------------------- 
    # -------------------------- #
    # - SNIFS do_scala PARSING   #
    # -------------------------- #
    if wavelength_input[0].lower() == 'b' or wavelength_input[0].lower() =='r':
        channel,ith = parse_SNIFS_BR_input(wavelength_input)
        return Get_ith_array(channel,ith,ExtraRunStep,IntraRunStep,
                             start_offset = start_offset,
                             addCalibrationRun=addCalibrationRun)

    # ----------------------- #
    # - Unique Wavelength     #
    # ----------------------- #
    if type(wavelength_input) == str:
        return N.float(wavelength_input)
    
    print "wavelength_input",wavelength_input,len(wavelength_input)
    raise ValueError("Sorry I do not understand the given wavelength input")


def Get_ith_array(channel,ith_incrementation,ExtraRunStep_,
                  IntraRunStep_,
                  start_offset = 0,
                  addCalibrationRun=False):
    """
    """
    if ith_incrementation*ExtraRunStep_ >= IntraRunStep_:
        # -- This means that the calibration of this wavelength has already been made -- #
        # -     but do you want a Calibration Run ?
        if addCalibrationRun and (ith_incrementation-1)*ExtraRunStep_ <= IntraRunStep_:
            if channel.lower() == 'b':
                return BlueCalibrationWavelength
            else:
                return RedCalibrationWavelength
            
        return None
    
    if channel.lower() == 'b':
        first_lbda = B_channel_first_lbda + start_offset
        NumPoints = N.ceil((B_channel_last_lbda- first_lbda )/IntraRunStep_)
        
    else:
        first_lbda = R_channel_first_lbda + start_offset
        NumPoints = N.ceil((R_channel_last_lbda- first_lbda )/IntraRunStep_)
    
    return (N.arange(NumPoints))*IntraRunStep_ + first_lbda +(ith_incrementation*ExtraRunStep_)

    
def parse_SNIFS_BR_input(BRinput):
    """
    This function understands and parse the do_scala (SNIFS) wavelengths requestes
    adn returns with runs is requered to feed `Get_ith_array`
    ------
    return string [channel], int [iteration]za
    """
    channel,info_ith = BRinput[0],BRinput[1:]
    for i in range(len(info_ith)):
        try:
            ith = int(info_ith[-(i+1):])
        except:
            break
        
    return channel.lower(),ith

#######################
# -- Exposure time -- #
#######################

def Read_exposure_input(exposure_input,
                        wavelength_array=None,
                        verbose=True,
                        shorten_default_exposures_by=1.):
    """
      -- exposure_input [string / None]: == Various parsing Format allowed ==
           -> None : the function will use a predefined (optimized) exposure time per wavelength
                (see get_wavelength_exposure_time)
           -> 1 string of a float : All wavelength will have this unique wavelength
           -> N values split by ',' ['lbda_1,lbda_2,lbda_3,...lbda_N']
                (Caution -- N is the same size as `wavelength_array`)

                     
      -- wavelength_array: array of N float in AA
           (Caution -- same size as exposure_input if exposure_input is not None or 1)

    
      -- shorten_default_exposures_by [float]:
          If exposure_input is None this will load a default (optimized) value.
          This enable to reduce (>1) or increase (<1) these exposure time
          (default_expo / shorten_default_exposures_by)
          
    -----
    returns float-array [of exposure time in seconde]
    """
    # ------------------------------- #
    # -- Pre defined Exposure times - #
    # ------------------------------- #
    if exposure_input is None:
        if wavelength_array is None:
            raise ValueError("If exposure_input is None, you need to give a wavelength_array so I can measure the exposure time")
        return get_wavelength_exposure_time(wavelength_array) / shorten_default_exposures_by
    
    # ------------------------------- #
    # -- Force input exposure times - #
    # ------------------------------- #
    if ',' in exposure_input:
        if verbose:
            print "INFO [SCALA_expose.Read_exposure_input] you give manual Exposure time (',')"
        try:
            exposure_array = N.asarray(exposure_input.split(','),dtype="float")
        except:
            raise ValueError("The Manual exposure time input is unparsable in float. It shoud be expo1,expo2,..,expoN [in seconde]")
        return exposure_array
    
    # ------------------------------- #
    # --  Constant exposure times  -- #
    # ------------------------------- #
    if type(exposure_input) == float or type(exposure_input) == int or type(exposure_input) == str or len(exposure_input) == 1:
        if type(exposure_input) == str:
            exposure_input = N.float(exposure_input)
        elif type(exposure_input) == float or type(exposure_input) == int:
            exposure_input = float(exposure_input)
        else:
            exposure_input = exposure_input[0]
            
        if verbose:
            print "INFO [SCALA_expose.Read_exposure_input] You requested *one constant* exposure time"
        if wavelength_array is None:
            if verbose:
                print "INFO [SCALA_expose.Read_exposure_input] You requested *one constant* exposure time but no wavelength array, so a float is returned"
            return exposure_input
        if type(wavelength_array) == float:
            return N.float(exposure_input)
        
        return N.ones(len(wavelength_array)) * N.float(exposure_input)
    
    
    
   

    
def get_wavelength_exposure_time(wavelengths):
    """
    """
    fileExpo = N.asarray( [l.split() for l in open(IOs.INPUT_data+"exposure_time.txt").read().splitlines()
                           if l[0]!="#"],dtype='float').T
    
    if type(wavelengths) == float:
        i = N.argmin(N.abs(fileExpo[0]*10-wavelengths))
        return fileExpo[1][i]
    # -- its an array then -- #
    return N.asarray( [ fileExpo[1][N.argmin(N.abs(fileExpo[0]*10-lbda))] for lbda in wavelengths])
