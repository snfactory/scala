#!/usr/bin/python

import sys
import numpy as N
    

    
##############################################################
# ---------------------------------------------------------- #
# ----------- MAIN SCALA's SCRIPT      --------------------- #
# ---------------------------------------------------------- #
##############################################################

if __name__ == '__main__':

    import optparse
    parser = optparse.OptionParser()
    
    opts,args = parser.parse_args()
    max_run = 50
    Nrand = N.random.rand(1)[0]*max_run
    for i in range(max_run):
        print "%.1f"%N.random.rand(1)[0]
        if i == int(Nrand):
            print "Status 10"
        
    
