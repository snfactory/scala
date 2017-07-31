#!/usr/bin/python


import SCALA_tools as St
# -- Not that those are also imported by St...
import Monochromator_tools as Mt
import Clap_tools          as Cl
import IO_SCALA            as IOs
import General_tools       as Gt


##############################################################
# ---------------------------------------------------------- #
# ----------- TEST: SCRIPTS FOR SCALA  --------------------- #
# ---------------------------------------------------------- #
##############################################################
if __name__ == '__main__':

    import optparse
    parser = optparse.OptionParser()
    # -------------------------- #
    # ---   OPTIONS          --- #
    # -------------------------- #
    # --- General Test --- #
    parser.add_option("--scala", action="store_false",
                      help="This function loads SCALA and do 2 random wavelength 1 second exposure"+" \n "+
                      "[*Information* - This function is set off if any other option is on]",
                      default=True)
    
    # --   Individual test    -- #
    parser.add_option("--IO", action="store_true",
                      help="This function returns the IO, to know which instrument is connected "+" \n "+
                      "[*Information* -- (%s)]"%IOs.NET_IO_order,
                      default=False)
    
    parser.add_option("--MonoChromator", action="store_true",
                      help="This function Checks if the monochromator is ready "+" \n "+
                      "[*Information* - Loads the Class, Change to a random wavelength and 'check_up']",
                      default=False)
    
    parser.add_option("--Claps", action="store_true",
                      help="This function Checks if the Claps looks good "+" \n "+
                      "[IMPORTANT - This do a 1 second exposure for both claps.]",
                      default=False)
    
    
    opts,args = parser.parse_args()
    # -------------------------- #
    # --- SCRIPTS themself   --- #
    # -------------------------- #
    # --------- #
    # - IO test #
    # --------- #
    if opts.IO:
        opts.scala = False
        net = IOs.IO_scala()
        try:
            portList = net.GetPortList()
        except:
            IOs.Status_Test(False,"** ERROR ** -- Most likely the Given port (%s) is not the good one..."%IOs.NET_IO_port)
            
        
        IOs.Status_Test(True,"Here is the current connexion status: %s"%portList+
                    "\n"+"(Order Recall: %s)"%IOs.NET_IO_order)
        

    # -------------------- #
    # - MonoChromator test #
    # -------------------- #
    if opts.MonoChromator:
        opts.scala = False
        try:
            Mono = Mt.MonoChromator(4000) # None means it goes to the latest Wavelength
        except:
            IOs.Status_Test(False,"** WARNING **: The MonoChromator test FAILED")
            raise Gt.TimeoutError("Time Out ??? (__init__ function could have take more than %.1s second)"%IOs.IO_timer_max_loading+
                                  "\n"+ "--> Check if this power is ON (--IO)")
        
        # -- None means a random wavelength between 3500 and 8000 A -- #
        Mono.expose__test_function(None)
        if Mono.Is_Ready():
            IOs.Status_Test(True,"The MonoChromator test went just Fine")
        else:
            IOs.Status_Test(False,"** WARNING **: The MonoChromator test FAILED")
            

    # -------------------- #
    # - MonoChromator test #
    # -------------------- #
    if opts.MonoChromator:
        opts.scala = False
        print "TBD"
            
    
