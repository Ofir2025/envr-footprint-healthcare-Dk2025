# -*- coding: utf-8 -*-
"""
RIVM GDDZ project: May-July 2020

Tasks:

    1. Import waste from excel
    2. Convert to dictionary and store as pickle

@author: Joao F. D. Rodrigues
Minor revisions by Michelle Steenmeijer
"""
# pandas 23.4

import pandas as pd
import numpy as np
import os
import time
import pickle as pkl
np.set_printoptions(precision=2)
#import pyxlsb
import sys
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
mrio_str = 'mrio' + year +'.pkl'  
pkl_in = open(pkl_dir + mrio_str,"rb")

mrio = pkl.load(pkl_in)
pkl_in.close()

#labels
region = mrio['label']['region']
final = mrio['label']['final']
industry = mrio['label']['industry']
del mrio

##############################################
#Load source objects

tstart = time.time()

#to read pyxlsb file need to:
#pip3 install pandas --upgrade
#pip3 install pyxlsb

excel_str = 'MR_HSUT_2011_v3_3_17_extensions.xlsb'  

sheet_str = 'waste_sup_FD'  
waste_final = pd.read_excel(exio_dir + excel_str, sheet_name = sheet_str, index_col=[0,1], header=[0,1,2,3], engine='pyxlsb')

sheet_str = 'waste_from_stock'  
waste_tmp = pd.read_excel(exio_dir + excel_str, sheet_name = sheet_str, index_col=[0,1], header=[0,1,2,3], engine='pyxlsb')
waste_final = waste_final + waste_tmp

sheet_str = 'waste_sup_act'  
waste_industry = pd.read_excel(exio_dir + excel_str, sheet_name = sheet_str, index_col=[0,1], header=[0,1,2,3], engine='pyxlsb')

##############################################
# this SUT has 164 industries, 48 countries, 6 final demand categories
# Processing to correspond with Exiobase v3.7  163 industries 49 countries, 7 final demand categories

# Fill in right places
nreg = region.shape[0]
nreg_waste = nreg - 1
nfin = final.shape[0]
nfin_waste = nfin - 1
nind = industry.shape[0]
nind_waste = nind + 1

#position of regions
print('concordance of regions')
reg_exio = list(region.index)
reg_pos = -1 * np.ones((nreg_waste,1))

reg_waste = []
reg_waste_alt = []
for i in range(nreg_waste):
    val = waste_final.columns[i * nfin_waste][0]
    print(val)
    reg_waste.append(val)
    pos = reg_exio.index(val)
    reg_pos[i] = pos
    val_alt = waste_industry.columns[i * nind_waste][0]
    reg_waste_alt.append(val_alt)
    if(val_alt != val):
        print(i, val, val_alt)


#position of industries
print('concordance of industries')
ind_exio = list(industry.index)
ind_pos = -1 * np.ones((nind_waste,1))

ind_waste = []
for i in range(nind_waste):
    val = waste_industry.columns[i][3]
    ind_waste.append(val)
    if(val == 'A_MGWG'):
        ind_pos[i] = 109
    else:     
        try:
            pos = ind_exio.index(val)
            ind_pos[i] = pos
        except:
            print(i, val)

#109 A_MGWG
#In [85]: waste_industry.columns[i]
#Out[85]: ('AU', 'Manufacture of gas;', 'i40.2.a', 'A_MGWG')

#A_GASD   Manufacture of gas; distribution of gaseous fu...     i40.2
#In [92]: ind_exio.index('A_GASD')
#Out[92]: 109

# Fill in values: final demand
h = np.zeros((1, nreg * nfin))
for i in range(nreg_waste):
    for j in range(nfin_waste):
        val = waste_final.iloc[:, i * nfin_waste + j].sum()
        ipos = int(reg_pos[i])
        jpos = int(j)
        h[0, ipos * nfin + jpos] = val

# Fill in values: industry
r = np.zeros((1, nreg*nind))
for i in range(nreg_waste):
    for j in range(nind_waste):
        val = waste_industry.iloc[:,i * nind_waste + j].sum()
        ipos = int(reg_pos[i])
        jpos = int(ind_pos[j])
        r[0,ipos * nind + jpos] = val

##############################################
#Save as pickle

label = {'region': region, 'industry': industry, 'final': final, 'unit': 'tonne'}

waste = {'label': label, 'r': r, 'h': h}

pkl_str = 'waste.pkl'  
pkl_out = open(pkl_dir + pkl_str,"wb")
pkl.dump(waste, pkl_out)
pkl_out.close()
