#!/usr/bin/python

import Monochromator_tools as Mt



    
    
    
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
    else:
        verbose = True
    Mt.Clear_MonoChromator(verbose=verbose)
