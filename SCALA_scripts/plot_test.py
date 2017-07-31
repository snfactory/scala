#! /usr/bin/env python
# -*- #! /usr/bin/env python
# -*- coding: utf-8 -*-

import pyfits as F
import matplotlib.pyplot as P
import numpy as N

#filename1="scala_clap0_calibration_mirror_G1_new2.fits"
filename1="scala_clap0_calibration_mirror_A1_3nm.fits"
filename3="scala_clap1_calibration_mirror_C3.fits"
filename2="scala_clap0_calibration_mirror_A2.fits"

Fits1     = F.open(filename1)
Fits2     = F.open(filename2)
Fits3     = F.open(filename3)
#Fits4     = F.open(filename4)


raw_mc1 = Fits1[1].data["MEAN_CLIP"]
raw_mc2 = Fits2[1].data["MEAN_CLIP"]
raw_mc3 = Fits3[1].data["MEAN_CLIP"]
raw1  = Fits1[0].data
raw2  = Fits2[0].data
#raw3  = Fits3[0].data
#raw4  = Fits4[0].data
#raw5  = F.open("scala_clap0_calibration_mirror_C2.fits")[0].data
#raw6  = F.open("scala_clap1_calibration_mirror_C2.fits")[0].data

lbda1       = Fits1[1].data["WAVELENGTH"][::3]
lbda2       = Fits2[1].data["WAVELENGTH"][::3]
#lbda3       = Fits3[1].data["WAVELENGTH"][::3]
#lbda4       = Fits4[1].data["WAVELENGTH"][::3]
#lbda5       = F.open("scala_clap0_calibration_mirror_C2.fits")[1].data["WAVELENGTH"][::3]
#lbda6       = F.open("scala_clap1_calibration_mirror_C2.fits")[1].data["WAVELENGTH"][::3]

bkgd_mc1 = N.mean([raw_mc1[::3],raw_mc1[2::3]],axis=0)
bkgd_mc2 = N.mean([raw_mc2[::3],raw_mc2[2::3]],axis=0)
bkgd_mc3 = N.mean([raw_mc3[::3],raw_mc3[2::3]],axis=0)
bkgd1        = N.mean([raw1[::3],raw1[2::3]],axis=0)     
bkgd2        = N.mean([raw2[::3],raw2[2::3]],axis=0)   
#bkgd3        = N.mean([raw3[::3],raw3[2::3]],axis=0)   
#bkgd4        = N.mean([raw4[::3],raw4[2::3]],axis=0)
#bkgd5        = N.mean([raw5[::3],raw5[2::3]],axis=0)   
#bkgd6        = N.mean([raw6[::3],raw6[2::3]],axis=0)

data1        = -(raw_mc1[1::3] - bkgd_mc1)
data2        = -(raw_mc2[1::3] - bkgd_mc2)
data3        = -(raw_mc3[1::3] - bkgd_mc3)
#data4        = -(raw4[1::3] - bkgd4)
#data5        = -(raw5[1::3] - bkgd5)
#data6        = -(raw6[1::3] - bkgd6)



fig  = P.figure(figsize=[7,4])
ax = P.axes([0.13,0.13,0.8,0.8])

ax.plot(lbda2,data1,marker="o")
#ax.plot(lbda2,data2,marker="x")
#ax.plot(lbda2,data3,marker="+")
#ax.plot(lbda4,bkgd4,marker="*") 
#ax.plot(lbda5,bkgd6,marker="o")
fig.show()  


