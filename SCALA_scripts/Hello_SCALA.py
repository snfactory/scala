#!/usr/bin/python
import sys

import numpy       as N
import SCALA_tools as St

    

    
##############################################################
# ---------------------------------------------------------- #
# ----------- MAIN SCALA's SCRIPT      --------------------- #
# ---------------------------------------------------------- #
##############################################################

if __name__ == '__main__':

    import optparse
    parser = optparse.OptionParser()

    parser.add_option("-V","--Verbose",action="store_true", 
                      help="If you want all the additional prints",
                      default=False)
    parser.add_option("--snifs",action="store_true",
                      help="This option if there for print for SNIFS scripts",
                      default=False)
    
    opts,args = parser.parse_args()

    
    Scala = St.SCALA([3500,4000],[3,3],used_clap=[True,True],
                     verbose=opts.Verbose,snifs_mode=opts.snifs)

    
