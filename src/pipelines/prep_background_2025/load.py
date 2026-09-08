# -*- coding: utf-8 -*-
"""
Script for:
The environmental footprint of the Dutch healthcare sector: beyond environmental impact (in press)
Steenmeijer MA, Rodrigues JFD, Zijp MC, Waaijers-van der Loop SL
The Lancet Planetary Health

Tasks exiobase_3_7-load.py:

    1. Load Exiobase v3.7 and calibrate MRIO
    2. Merge in dictionary and store as pickle

@author: Joao F. D. Rodrigues
minor additions by Michelle A. Steenmeijer
"""

import pandas as pd
import numpy as np
import os
import time
import pickle as pkl
import sys
from paths import EXIOBASE_DIR, BACKGROUND_DIR, MRIO_DIR
np.set_printoptions(precision=2)
tstart = time.time()

year = os.environ.get('HC_BACKGROUND_YEAR', '2016')  # IOT_<year>_ixi must exist
# under data/bronze/exiobase_v3_7/. v3.8.2 is used for every year: its 2022 table
# reproduces Danish national accounts, whereas v3.10.2's 2022 nowcast does not
# (see docs/revision/exiobase_vintage_defects.md).

##############################################
##############################################
#TASK 1: Load Exiobase v3.7
'''
The structure of the Exiobase data is messy.

In the root folder there are:
    A.txt: technical coefficient matrix
    Y.txt: final demand matrix
In the satellite/ folder there are:
    F.txt: superimposed primary inputs (V) and extension (R) matrices of industries
    F_hh.txt: superimposed primary input (empty) and extension (H) matrices of final demand
    
The rest needs to be reconstructed:
    x = (I - A)^(-1) y
    Z = A * diag(x)

Adapted characterization factors are stored in the bronze Exiobase directory.
'''
##############################################
# Set working directory to envr-footprint-healthcare2025 folder
# or change to your folder structure
print("Starting to read files..\n")
exio_dir = str(EXIOBASE_DIR) + os.sep
# Folder settings: Change to reflect the location in your computer relative to the current working directory (run os.getcwd() to find out whatthat is)
# Exiobase 2011 folder
iot_dir = exio_dir + 'IOT_' + year + '_ixi' + os.sep
# Auxiliary files folder (regions and characterization)
# Folder to store MRIO

# Folder to write background files to (pickled prepared MRIO files) to
BACKGROUND_DIR.mkdir(parents=True, exist_ok=True)
MRIO_DIR.mkdir(parents=True, exist_ok=True)
bg_dir = str(BACKGROUND_DIR) + os.sep
mrio_dir = str(MRIO_DIR) + os.sep


##############################################
## Load category lists (industries and final demands) from auxiliary files in the IOT directory,
## Drop the 'Number' column, and store them as pandas DataFrames. Also compute the number of categories.

# Creates a list of categories for final demand
str_fin = 'finaldemands.txt'  
label_fin = pd.read_csv(iot_dir + str_fin, sep='\t', index_col=[3], header=[0])
label_fin = label_fin.drop(labels=['Number'],axis=1)
n_fin = label_fin.count().iloc[0]

# Creates a list of categories for industry
str_ind = 'industries.txt'  
label_ind = pd.read_csv(iot_dir + str_ind, sep='\t', index_col=[3], header=[0])
label_ind = label_ind.drop(labels=['Number'],axis=1)
n_ind = label_ind.count().iloc[0]

# Region list of categories including population in 2011. The upstream
# Netherlands region file is the canonical source; Denmark's one-row
# adaptation is derived in memory rather than stored as a duplicate Bronze
# file.
regions_file = EXIOBASE_DIR / "regions_nl.txt"
df = pd.read_csv(regions_file, sep="\t")

# Make Denmark its own region while keeping the Netherlands as its own region.
df.loc[df["ISO2"] == "DK", ["DESIRE region", "DESIRE region name"]] = ["DK", "Denmark"]

# Keep NL as its own region (do NOT remove it)
# Just leave NL unchanged so the structure matches unit.txt
# If NL is changed to Western Europe (WE) here, it will almost certainly misalign or mess up results later.
# You can aggregate NL into WE later, if desired. It's helpful to keep it also as a check for having made mistakes .

# Debug info
print(f"Loaded canonical regions file: {regions_file}")
print("Columns:", df.columns.tolist())
print("Check DK and NL rows:")
print(df[df["ISO2"].isin(["DK", "NL"])])

# Use the in-memory Denmark adaptation; do not write a generated derivative
# into the Bronze source directory.
label_reg = df.set_index("ISO2")
n_reg = label_reg.count().iloc[0]

#################################################
# Load unit information from 'unit.txt' in the IOT folder.
# Stores the result as a pandas DataFrame for later use.

str_unit = 'unit.txt'  
label_unit = pd.read_csv(iot_dir + str_unit, sep='\t', index_col=[0,1], header=[0])

#fix order of regions
vec_reg = []
for k_reg in range(n_reg):
    tmp = label_unit.iloc[k_reg * n_ind].name[0]  # index name position 0
    vec_reg.append(tmp)
label_reg = label_reg.reindex(vec_reg)

#explore and verify order of industries
vec_ind = []
for k_ind in range(n_ind):
    tmp = label_unit.iloc[k_ind].name[1]
    vec_ind.append(tmp)
    if tmp != label_ind.iloc[k_ind]['Name']:
        print(k_ind, tmp, label_ind.iloc[k_ind]['Name'])

#################################################
# Commented sanity check code snippets

# primary input classification
# unit of monetary flows is:
unit_monetary = 'M.EUR'
#labels_unit_str = 'unit.txt'  
#labels_unit_pd = pd.read_csv(iot_dir + labels_unit_str, sep='\t')
#print(set(labels_unit_pd['unit']))

#read units of environmental extensions
str_ext = 'satellite/unit.txt'  
label_ext = pd.read_csv(iot_dir + str_ext, sep='\t')
label_ext.columns.values[0] = 'Name'
n_ext = label_ext.shape[0]

# position of monetary primary inputs in extensions are: 
n_pri = 9
pos_pri = list(range(n_pri)) 
#truncating labels of primary inputs 
label_pri = label_ext.iloc[pos_pri]

#################################################
#reach characterization factors
# adapted for use, plus adapted for ReCiPe for impactcategory x, y z !!!
str_char = 'characterisation_desire_version3_4_adapted.xlsx'

#for k in range(label_char.shape[0]):
#    aval = label_ext['Name'].iloc[k]
#    bval = label_char['Name'].iloc[k]
#    if(aval != bval): 
#        print(k, aval, bval)
#There are apostrophes missing in entries 2-4
#There are 1104 extensions in the characterization matrix, but 1113 in the extensions unit list. The extra 9 are appended at the end.

## Load characterization factor matrices from str_char file (from just above)

Q_factorinputs = pd.read_excel(exio_dir + str_char, sheet_name = 'Q_factorinputs', index_col=[0,1], header=[0,1])

Q_emissions = pd.read_excel(exio_dir + str_char, sheet_name = 'Q_emissions', index_col=[0,1,2,3], header=[0,1])

Q_resources = pd.read_excel(exio_dir + str_char, sheet_name = 'Q_resources', index_col=[0,1], header=[0,1])

Q_materials = pd.read_excel(exio_dir + str_char, sheet_name = 'Q_materials', index_col=[0,1], header=[0,1])

# initial step that should be added to each
# extension position to be in the right place:
step_factorinputs = 0
step_emissions = 23
step_resources = 446
step_materials = 466

# build conversion factor matrix with selected
# six themes and truncate extensions to only
# those that matter
# 6 themes - GWP100, Mat extr, Water use, LU, VA, Employment

n_char = 6  
Q = np.zeros((n_char, n_ext))
Q_name = []
Q_unit = []

# Extract GWP100 characterization factors from Q_emissions and insert them into the first row of the 6×n_ext matrix, storing impact name and units
pos_gwp = 5  # position for impcat in characterisation table
vtmp = np.array(Q_emissions.iloc[pos_gwp])  # select CFs for relevant impcat
vpos = np.where(vtmp)[0]  # get indices number for which CF != 0
Q[0, vpos + step_emissions]= vtmp[vpos]  # fill in CF for index in empty 6x1113 array
Q_name.append(Q_emissions.index[pos_gwp][1])  # collect name of impact
Q_unit.append(Q_emissions.index[pos_gwp][3])  # collect unit of impact

# Same for Abiotic material extraction
pos_mat = 4  # position domestic extraction
vtmp = np.array(Q_materials.iloc[pos_mat])
vpos = np.where(vtmp)[0] #all positions v != 0
Q[1,vpos + step_materials]= vtmp[vpos]
Q_name.append(Q_materials.index[pos_mat][0])
Q_unit.append(Q_materials.index[pos_mat][1])

#Water use
pos_water = 12
vtmp = np.array(Q_materials.iloc[pos_water])
vpos = np.where(vtmp)[0]
Q[2,vpos + step_materials]= vtmp[vpos]
Q_name.append(Q_materials.index[pos_water][0])
Q_unit.append(Q_materials.index[pos_water][1])

#Land use
pos_land = 0
vtmp = np.array(Q_resources.iloc[pos_land])
vpos = np.where(vtmp)[0]
Q[3,vpos + step_resources]= vtmp[vpos]
Q_name.append(Q_resources.index[pos_land][0])
Q_unit.append(Q_resources.index[pos_land][1])

#Added value
pos_gva = 0
vtmp = np.array(Q_factorinputs.iloc[pos_gva])
vpos = np.where(vtmp)[0]
Q[4,vpos + step_factorinputs]= vtmp[vpos]
Q_name.append(Q_factorinputs.index[pos_gva][0])
Q_unit.append(Q_factorinputs.index[pos_gva][1])

#Employment - eventually not used in the calculation
pos_emp = 1
vtmp = np.array(Q_factorinputs.iloc[pos_emp])
vpos = np.where(vtmp)[0]
Q[5,vpos + step_factorinputs]= vtmp[vpos]
Q_name.append(Q_factorinputs.index[pos_emp][0])
Q_unit.append(Q_factorinputs.index[pos_emp][1])

# ---------------------------------------------------------------------------
# Restate climate on IPCC AR6 GWP100.
#
# The DESIRE workbook's climate row carries IPCC AR4 factors (CH4 = 25,
# N2O = 298) despite its "CML 1999" label. AR6 is the current assessment and is
# what this study reports, so row 0 of Q is rebuilt from the stressor names.
#
# HFC and PFC are reported by EXIOBASE already aggregated in kg CO2-equivalent
# rather than as individual species. Their vintage is fixed by EXIOBASE and
# cannot be recovered, so they keep their existing factor of 1 and are left
# untouched here. Set HC_GWP_VINTAGE=AR4 to reproduce the previous behaviour.
# ---------------------------------------------------------------------------
from analysis.constants import ar6_gwp_factor  # noqa: E402

_gwp_vintage = os.environ.get('HC_GWP_VINTAGE', 'AR6').upper()
if _gwp_vintage == 'AR6':
    _restated, _kept = 0, 0
    for _i in range(n_ext):
        _factor = ar6_gwp_factor(label_ext['Name'].iloc[_i])
        if _factor is not None:
            Q[0, _i] = _factor
            _restated += 1
        elif Q[0, _i] != 0:
            _kept += 1
    Q_name[0] = 'global warming GWP100 (IPCC AR6)'
    Q_unit[0] = 'kg CO2 eq.'
    print(f"GWP restated to IPCC AR6: {_restated} stressors; "
          f"{_kept} kept as supplied (HFC/PFC already in CO2-equivalent)")
else:
    print(f"GWP vintage left as supplied in the workbook ({_gwp_vintage})")

#Build a label dataframe for the characterization factors

Q_data = []
for k in range(n_char):
    Q_data.append([Q_name[k],Q_unit[k]]) 

label_char = pd.DataFrame(index = list(range(n_char)), columns = ['Name', 'Unit'], data = Q_data)

#############################################

# End of category and label organization (Metadata setup)
# Next part is about importing values into the dataframes created above

#################################################
#import numerical data

# final demand matrix
Y_str = 'Y.txt'  
Y_pd = pd.read_csv(iot_dir + Y_str, sep='\t', index_col=[0,1], header=[0,1])
Y = np.array(Y_pd)

# household emissions (file is named F_hh.txt in EXIOBASE 3.7 and F_Y.txt from 3.8 onward)
H_path = os.path.join(iot_dir, 'satellite', 'F_Y.txt')
if not os.path.exists(H_path):
    H_path = os.path.join(iot_dir, 'satellite', 'F_hh.txt')
H_pd = pd.read_csv(H_path, sep='\t', index_col=[0], header=[0,1])
H = np.array(H_pd)

# primary inputs and industry emissions # only the first 9 - employment not included.
VR_str = 'satellite/F.txt'
V_pd = pd.read_csv(iot_dir + VR_str, sep='\t', index_col=[0], header=[0,1]).iloc[pos_pri]
V = np.array(V_pd)

R_pd = pd.read_csv(iot_dir + VR_str, sep='\t', index_col=[0], header=[0,1])
R = np.array(R_pd) #incl factor inputs/employment

tend = time.time()
print('Done reading everything except intersectoral flows in %5.2f s\n'% (tend - tstart))
tstart = time.time()

# Load Technical Coefficients (Matrix (A))
A_str = 'A.txt'  
A = np.array(pd.read_csv(iot_dir + A_str, sep='\t', index_col=[0,1], header=[0,1]))

tend = time.time()
print('Done reading technical coefficients in %5.2f s\n'% (tend - tstart))
tstart = time.time()

#############################################
#############################################
#TASK 2 Merge in dictionary and store as pickle

# merge elements in MRIO dictionary
label = {'region': label_reg, 'industry': label_ind, 'final': label_fin, 'primary': label_pri, 'extension': label_ext, 'characterization': label_char}

mrio = {'Y': Y, 'A': A, 'V': V, 'R': R, 'H': H, 'Q': Q, 'label': label}

#############################################
# save to pickle

mrio_str = 'exio' + year + '.pkl'  
pkl_out = open(mrio_dir + mrio_str,"wb")
pkl.dump(mrio, pkl_out)
pkl_out.close()

tend = time.time()
print('Done writing in %5.2f s\n'% (tend - tstart))
tstart = time.time()
