#!/usr/bin/python


import SCALA_tools as St



##############################################################
# ---------------------------------------------------------- #
# -----------  MAIN: SCRIPT FOR SCALA  --------------------- #
# ---------------------------------------------------------- #
##############################################################
if __name__ == '__main__':

    import optparse
    parser = optparse.OptionParser()
    # -------------------------- #
    # ---   OPTIONS          --- #
    # -------------------------- #
    
    # -- Options for the scala class -- #
    
    parser.add_option("-W","--wave_range",
                      help="Wavelength range: min_wavelength,max_wavelength (in Angstrom) (e.g. 3500,5000)"+" \n "
                      "[Caution options needed ! no None accepted] -- default [%default]",
                      default=None)
    
    parser.add_option("-N","--npoints", type='int',
                      help="number of intermediate wavelength range (e.g. if 3 [Min, Medium, Max], using linspace) "+" \n "
                      " -- default [%default]",
                      default=3)

    parser.add_option("-E","--expo_time",type='float',
                      help="Exposure time per observation (in second)"+" \n "
                      " [Information, same exposure time per observation] -- default [%default]",
                      default=1.0)

    parser.add_option("--claps",
                      help="Which Clap do you want to use: [Clap0,Clap1] (e.g. 1,1  for both)"+" \n "
                      " [Caution ',' between them] -- default [%default]",
                      default="1,1")
    # --- Output
    parser.add_option("-S","--savefile",
                      help="output fits file. Where you are going to save the clap results"+" \n "
                      "-- default [%default]",
                      default="SCALA_script_Clap_output.fits")
    # -- Options for the scala class -- #

    
    opts,args = parser.parse_args()
    # -------------------------- #
    # --- SCRIPTS themself   --- #
    # -------------------------- #
    
    
