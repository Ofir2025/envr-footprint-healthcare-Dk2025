# -*- coding: utf-8 -*-
"""
The environmental footprint of the Dutch healthcare sector: beyond environmental impact (in press)
Steenmeijer MA, Rodrigues JFD, Zijp MC, Waaijers-van der Loop SL
The Lancet Planetary Health

Tasks exiobase_3_7-process.py:

    1. Assemble MRIO
    2. Merge in dictionary and store as pickle

@author: Joao F. D. Rodrigues
minor additions by Michelle A. Steenmeijer
"""

import numpy as np
import os
import time
import pickle as pkl
import sys
np.set_printoptions(precision = 2)

tstart = time.time()
year = '2016'
##############################################
##############################################
#TASK 1: Load Exiobase v3.7 and calibrate MRIO


##############################################
# Folder settings: Change to reflect the location in your computer relative to the current working directory (run os.getcwd() to find out whatthat is)
# Set working directory to envr-footprint-healthcare2025 folder
if str(os.getcwd()).endswith('envr-footprint-healthcare2025'):
    print("Starting to read files..\n")
else:
    print("Please set working directory to envr-footprint-healthcare2025 folder")
    sys.exit()
    
# Folder to read MRIO from
mrio_dir = os.getcwd() + '\\data\\bg\\pickled_mrio\\'


##############################################
#Load MRIO

tstart = time.time()

mrio_str = 'exio'+ year +'.pkl'  
pkl_in = open(mrio_dir + mrio_str,"rb")
mrio = pkl.load(pkl_in)
pkl_in.close()

mrio_str = 'leontief'+ year +'.pkl'  
pkl_in = open(mrio_dir + mrio_str,"rb")
L = pkl.load(pkl_in)
pkl_in.close()

tend = time.time()
print('Done reading in %5.2f s\n'% (tend - tstart))
tstart = time.time()


# Number of..
nr = mrio['label']['region'].count()[0]  # number of regions
ns = mrio['label']['industry'].count()[0]  # number of sectors

# Calculation x (total output)
x = np.dot(L, mrio['Y'].sum(1).reshape((nr*ns,1)))    # x = L*y
# Calculation Z matrix (intermediate demand matrix/transaction matrix)
Z = np.dot(mrio['A'], np.diag(x[:,0]))  # Z = A*diagn(x)

tend = time.time()
print('Done calculating interindustry transactions in %5.2f s\n'% (tend - tstart))
tstart = time.time()

mrio['Z'] = Z
mrio['x'] = x

#############################################
# save to pickle
mrio_str = 'mrio'+ year +'.pkl'  
pkl_out = open(mrio_dir + mrio_str,"wb")
pkl.dump(mrio, pkl_out)
pkl_out.close()

tend = time.time()
print('Done writing in %5.2f s\n'% (tend - tstart))
tstart = time.time()