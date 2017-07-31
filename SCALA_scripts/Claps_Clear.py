#!/usr/bin/python

import Clap_tools as C


    
    
    
##############################################################
# ---------------------------------------------------------- #
# ----------- Cleaning of MonoChromator--------------------- #
# ---------------------------------------------------------- #
##############################################################

if __name__ == '__main__':
    import optparse
    parser = optparse.OptionParser()
    
    parser.add_option("--snifs",action="store_true",
                      help="This option if there for print for SNIFS scripts",
                      default=False)

    opts,args = parser.parse_args()


        
    if opts.snifs:
        verbose= False
    for i in range(3):
        C.disconnect_all_the_claps()

    # -- Test on the claps -- #
    clap0 = C.Read_DC(device_number=0,line_periods=60,channels="b1")
    clap1 = C.Read_DC(device_number=1,line_periods=60,channels="b1")
    
    
    
