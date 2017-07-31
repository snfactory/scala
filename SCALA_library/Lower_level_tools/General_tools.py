#!/usr/bin/python

import matplotlib.pyplot as P
import numpy as N
# --------------------------------------- #
# -- This is for the timeout function --- #
from functools import wraps
import errno
import os
import signal
import sys
def make_me_iterable(a):
    """This makes sure the given value is an array. 
    """
    if hasattr(a,'__iter__'):
        return a
    else:
        return [a]

def savefile_reader(fig,savefile,dpi=500):
    """
    save in png and pdf is savefile is not none, show otherwise
    """
    if savefile is not None:
        fig.savefig(savefile+'.png',dpi=dpi)
        fig.savefig(savefile+'.pdf')
        
    else:
        fig.canvas.draw() # most of the tim, this is useless
        fig.show()
    


def sigma_clipped_array(array,sigma=5):
    """
    """
    array = N.asarray(array)

    std_    = array.std()
    mean_   = array.mean()
    flagout = N.abs(array-mean_)>sigma*std_
    array_clipped = array[-flagout]
    while(len(array_clipped)!=len(array)):
        array = array_clipped
        std_    = array.std()
        mean_   = array.mean()
        flagout = N.abs(array-mean_)>sigma*std_
        array_clipped = array[-flagout]

    return array_clipped
    
#######################################
# -- TIMEOUT FUNCTION              
#######################################
class TimeoutError(Exception):
    pass

def timeout(seconds=10, Status_out=1, error_message=os.strerror(errno.ETIME)):
    
    def decorator(func):
        
        def _handle_timeout(signum, frame,snifs_mode=True):
            print "timeout - Loading Failed"
            print "    %s"%error_message
            print "Status %d"%Status_out
            sys.exit(Status_out)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator
