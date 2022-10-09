# -*- coding: utf-8 -*-
"""
Script for:
The environmental footprint of the Dutch healthcare sector: beyond environmental impact (in press)
Steenmeijer MA, Rodrigues JFD, Zijp MC, Waaijers-van der Loop SL
The Lancet Planetary Health

Tasks:

    1. Import aggregation labels and concordance
    2. Merge in dictionary and store as pickle

@author: Joao F. D. Rodrigues
minor additions by Michelle Steenmeijer
# Eventually unused
"""

import pandas as pd
import numpy as np
import os
import sys
import time
import pickle as pkl
np.set_printoptions(precision=2)

tstart = time.time()
year = '2016'
##############################################
##############################################
#TASK 1: Load data from excel

##############################################
# Folder settings: Change to reflect the location in your computer relative to the current working directory (run os.getcwd() to find out whatthat is)
# Set working directory to envr-footprint-healthcare folder
if str(os.getcwd()).endswith('envr-footprint-healthcare'):
    print("Starting to read files..\n")
else:
    print("Please set working directory to envr-footprint-healthcare folder")
    sys.exit()
    
# Folder to read Excel from
exio_dir = os.getcwd() + '\\data\\exiobase_v3.7\\'  
# Folder to write/read pickle
pkl_dir = os.getcwd() + '\\data\\bg\\pickled_mrio\\' 



##############################################
#Load Exiobase industry classification

#Load rest of the system
mrio_str = 'mrio'+ year +'.pkl'  
pkl_in = open(pkl_dir + mrio_str,"rb")
mrio = pkl.load(pkl_in)
pkl_in.close()


#labels
exio = list(mrio['label']['industry'].index)
del mrio


##############################################
#Load aggregate classification and concordance

tstart = time.time()

excel_str = 'aggregation_industries.xlsx' 
sheet_str = 'Disaggregate'  
label = pd.read_excel(exio_dir + excel_str, sheet_name = sheet_str, index_col=[0], header=[0])

sheet_str = 'Concordance'  
conc = pd.read_excel(exio_dir + excel_str, sheet_name = sheet_str, index_col=[], header=[0], usecols = 'C:D')

vjdx = np.array(conc['Aggregate'])

exiopos = np.zeros((conc.shape[0],1))
for k in range(conc.shape[0]):
    exiopos[k] = int(exio.index(conc['Disaggregate'].iloc[k]))

g = np.zeros((label.shape[0], conc.shape[0]))
for k in range(conc.shape[0]):
    jdx = int(exiopos[k])    
    idx = vjdx[k]
    g[idx, jdx] = 1
    
agg = {'code': list(label['Code']), 'label': list(label['Label']), 'g': g}
##############################################
#Save as pickle

pkl_str = 'aggregation.pkl'  
pkl_out = open(pkl_dir + pkl_str,"wb")
pkl.dump(agg, pkl_out)
pkl_out.close()


