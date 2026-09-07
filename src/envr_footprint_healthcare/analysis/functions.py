# -*- coding: utf-8 -*-
"""
Script for:
The environmental footprint of the Dutch healthcare sector: beyond environmental impact (in press)
Steenmeijer MA, Rodrigues JFD, Zijp MC, Waaijers-van der Loop SL
The Lancet Planetary Health

Tasks functions.py:
    
    1. Functions to load data from Statistics NL (CBS) database
    2. Functions to load and prepare background EE-IOA elements
    3. Functions for the mathematical footprint operations

@author: Joao F. D. Rodrigues & Michelle A. Steenmeijer
"""

import pandas as pd
import numpy as np
import numpy.matlib
import os
import time
import pickle as pkl
import requests
np.set_printoptions(precision=2)
import sys


##############################################
# Retrieve relevant data from National statistics
#   expentiture and registered sectoral emissions from open data portal
#   conversion supply > basic price from sheet
##############################################
# snippet from https://www.cbs.nl/nl-nl/onze-diensten/open-data/open-data-v4/snelstartgids-odata-v4
def get_odata(target_url):
    data = pd.DataFrame()
    while target_url:
        r = requests.get(target_url).json()
        data = data.append(pd.DataFrame(r['value']))        
        if '@odata.nextLink' in r:
            target_url = r['@odata.nextLink']
        else:
            target_url = None            
    return data

def get_cbsdata(data_dir):
    if str(os.getcwd()).endswith('envr-footprint-healthcare') == False:
        print("Please set working directory to envr-footprint-healthcare folder")
        sys.exit()
    # Directe emissies Zorg en Welzijn
    #_________________________________
        # Source: https://opendata.cbs.nl/#/CBS/nl/dataset/83300NED/table
        # Onderwerp: Broeikasgassen/Broeikas-equivalent, 2016, Q Gezondheids-en welzijnzorg
        # Broeikasgassen: CO2, CH4, N20
        # Karakterisatie:
        # de uitstoot van 1 kg methaan (CH4) gelijk aan 25 broeikasgas-equivalenten 
        # en is de uitstoot van 1 kg lachgas (N2O) gelijk aan 298 broeikasgas-equivalenten.
        # hierin is de uitstoot van narcose/inhalatorengasssen niet meegenomen 
    table_url = "https://odata4.cbs.nl/CBS/83300NED"
    target_url = table_url + "/Observations"
    data = get_odata(target_url)
    
    # Uncomment code to check whether filter is correct
    #meta = get_odata(table_url)
    #codes = get_odata(table_url + "/MeasureCodes")
    #EcCode = get_odata(table_url + "/NederlandseEconomieCodes")
    #PerCode = get_odata(table_url + "/PeriodenCodes")
    #prop = get_odata(table_url + "/Properties")
    
    # Identifier M006309  # Broeikasgas-equivalent
    id_measure = 'M006309'
    # EcCode 422400 Identifier
    id_eccode = '422400'
    # PerCode Periode identifier 2016JJ00
    id_period = '2016JJ00'
    
    # kg CO2-eq * mln (kt CO2eq)
    val_GWP_health = data[(data['Measure'] == id_measure) & (data['Perioden'] == id_period) & (data['NederlandseEconomie'] == id_eccode)]['Value'].item()
    
    
    #_________________________________
    # Zorguitgaven op functie
        # Source expenditure:  https://opendata.cbs.nl/#/CBS/nl/dataset/84043NED/table?searchKeywords=CAO-sector%20overheid
        # Filter for 2016 and Totaal alle financieringsregelingen
    table_url = "https://odata4.cbs.nl/CBS/84043NED"
    target_url = table_url + "/Observations"
    data = get_odata(target_url)
    # data.columns = Index(['Id', 'Measure', 'ValueAttribute', 'Value', 'Zorgfuncties',
    #'FinancieringsregelingenZorg', 'Perioden'],dtype='object')
    
    # Uncomment code to check whether filter is correct
    #meta = get_odata(table_url)
    #ZFcodes = get_odata(table_url + "/ZorgfunctiesCodes")
    #ZFincodes = get_odata(table_url + "/FinancieringsregelingenZorgCodes")
    #percode = get_odata(table_url + "/PeriodenCodes")
    
    id_zorgwelzijn = 'T001104'  # ZorgfunctiesCodes: Totale uitgaven zorg en welzijn
    id_hc51 = 'A019196'  # ZorgfunctiesCodes: Geneesmiddelen, verbruiksartikelen
    id_hc52 = 'A019197'  # ZorgfunctiesCodes: Therapeutische hulpmiddelen
    id_fin = 'T001103' # FinancieringsregelingenZorgCodes: totaal alle financieringsregeling 
    id_per = '2016JJ00' # PeriodeCodes
    
    val_HC = data[(data['Zorgfuncties'] == id_zorgwelzijn) & (data['FinancieringsregelingenZorg'] == id_fin) & (data['Perioden'] == id_per)]['Value'].item()
    val_HC51 = data[(data['Zorgfuncties'] == id_hc51) & (data['FinancieringsregelingenZorg'] == id_fin) & (data['Perioden'] == id_per)]['Value'].item()
    val_HC52 = data[(data['Zorgfuncties'] == id_hc52) & (data['FinancieringsregelingenZorg'] == id_fin) & (data['Perioden'] == id_per)]['Value'].item()
    
    #remove HC51 and HC52 value from total healthcare value
    val_HC = val_HC - val_HC51 - val_HC52
    
    
    # Purchaser price > basic price conversion with NL Supply Use tables 
    #_________________________________
    
    sut_file = os.getcwd() + '\\data\\Supply tables 2015-2018.xlsx'  
    sut = pd.read_excel(sut_file, sheet_name = "Supply 2016 current prices", skiprows = 1, header=[0], index_col = [1], nrows=98)
    sut = sut[['Supply at basic prices (columns 82–85)  ','Total']]
    sut['conversion'] = sut['Supply at basic prices (columns 82–85)  '] / sut['Total'] 
    
    l_ = ['Basic pharmaceutical products and preparations',
          'Computer, electronic and optical products',
          'Human health services', 'Residential care and social work services']
    
    conv_pharm, conv_appl, conv_HC, conv_rescare = [sut.loc[x, 'conversion'] for x in l_]
    
    
    # Read all out to excel file 
    #_________________________________
    HC_col = [val_HC, conv_HC, val_GWP_health]
    pharm_col = [val_HC51, conv_pharm, 0]
    appl_col = [val_HC52, conv_appl, 0]
    index_col = ['Expenditure','Conversion','DirectEm']
    unit_col = ['MEUR','na','kt CO2e']
    cbs_data = pd.DataFrame({'Index':index_col, 'Unit': unit_col, 'HC service': HC_col,'Pharm': pharm_col,'MedAppl':appl_col}).set_index(['Index','Unit'])
    
    os.chdir(data_dir)
    cbs_data.to_csv('CBS_data_2016.csv') 
    os.chdir('..')
    return cbs_data



##############################################
#Create baseline object, dictionary containing
#   
#
##############################################
def createBackground(mrio_dir, cbs_data, bg_dir, year):
    tstart = time.time()

    ##############################################
    #Load waste
    mrio_str = 'waste.pkl'  
    pkl_in = open(mrio_dir + mrio_str,"rb")
    waste = pkl.load(pkl_in)
    pkl_in.close()

    #Load Leontief inverse
    mrio_str = 'leontief'+ year +'.pkl'  
    pkl_in = open(mrio_dir + mrio_str,"rb")
    L = pkl.load(pkl_in)
    pkl_in.close()

    #Load rest of the system
    mrio_str = 'mrio'+ year +'.pkl'  
    pkl_in = open(mrio_dir + mrio_str,"rb")
    mrio = pkl.load(pkl_in)
    pkl_in.close()

    #labels
    label = mrio['label']

    #matrix/vector objects
    x = mrio['x']
    Z = mrio['Z']
    Y = mrio['Y']
    V = mrio['V']
    R = mrio['R']
    H = mrio['H']
    Q = mrio['Q']
    A = mrio['A']
    
    #convert extensions to footprints
    xinv = (x != 0) / (x + (x ==0))
    R = np.dot(Q, R)
    H = np.dot(Q, H)

    # add waste
    R = np.concatenate((R, waste['r']), 0)
    H = np.concatenate((H, waste['h']), 0)

    characterization_waste = pd.DataFrame(data = [['Waste generation', 'tonne']], columns = ['Name', 'Unit'], index = [6])

    label['characterization'] = label['characterization'].append(characterization_waste)

    # generate coefficients
    B = np.dot(R, np.diag(xinv[:,0]))

    # determine aggregation of regions
    coderagg = ['NL', 'WE', 'WA', 'WL', 'WM', 'WF']
    labelragg = []
    nragg = len(coderagg)
    nr = label['region'].count()[0]
    gragg = np.zeros((nragg, nr))
    for (k, val) in enumerate(coderagg):
        pos = list(label['region']['DESIRE region']).index(val)
        labelragg.append(label['region']['DESIRE region name'][pos])
        jpos = [i for (i, e) in enumerate(list(label['region']['DESIRE region'])) if e == val]    
        for j in jpos:
            gragg[k, j] = 1
    ragg = {'code': coderagg, 'label': labelragg, 'g': gragg}

    # totals
    nr = label['region'].count()[0]
    ns = label['industry'].count()[0]
    ny = label['final'].count()[0]
    nv = label['primary'].count()[0]
#    ne = label['extension'].count()[0]
    nq = label['characterization'].count()[0]

    #fixing names
    label['characterization']['Name'].iloc[0] = 'Global warming'
    label['characterization']['Name'].iloc[1] = 'Material extraction'
    label['characterization']['Name'].iloc[2] = 'Blue water consumption'
    label['characterization']['Name'].iloc[4] = 'Value added'


    ##################################################
    #Determine the stimulus
    
    #Extract NL, GWP and healthcare
    #direct emissions from healthcare in kgCO2eq
    # Positions
    k_NL = 20
    k_GWP = 0 
    k_health = 137
    val_GWP_health = cbs_data.iloc[2,0].item() * 1e6  # kt to kg

    k_pharm = 62
    val_pharm_pp = cbs_data.iloc[0,1].item()  # purchaser price
    val_pharm_conv = cbs_data.iloc[1,1].item()  # could round up for same result as in paper 
    val_pharm_bp = val_pharm_conv * val_pharm_pp

    # Source conversion to basic price: 
    k_appl = 89
    val_appl_pp = cbs_data.iloc[0,2].item()  
    val_appl_conv = cbs_data.iloc[1,2].item()  
    val_appl_bp = val_appl_pp * val_appl_conv


    #vector to allocate across imports of pharmaceuticals
    vy = Y[:, k_NL * ny: (k_NL + 1)* ny].sum(1).reshape((nr,ns))
    vtmp = vy[:,k_pharm]
    vtmp = vtmp / vtmp.sum()
    vy = np.zeros((nr, ns))
    vy[:,k_pharm] = vtmp
    valloc_pharm = vy.reshape((nr*ns, ))

    #vector to allocate across imports of appliances
    vy = Y[:, k_NL * ny: (k_NL + 1)* ny].sum(1).reshape((nr,ns))
    vtmp = vy[:,k_appl]
    vtmp = vtmp / vtmp.sum()
    vy = np.zeros((nr, ns))
    vy[:,k_appl] = vtmp
    valloc_appl = vy.reshape((nr*ns, ))

    vy = Y[:, k_NL * ny: (k_NL + 1)* ny].sum(1).reshape((nr,ns))
    vtmp = Y[k_NL*ns + k_health,:] 

    # Healthcare service expenditure, ignore conversoin to basic price (0.38% difference)
    val_HCserv = cbs_data.iloc[0, 0].item()
    
    # Find scale factor to scale healthcare sector in Z column
    # divide expenditure with total sum of inter-industry use and factor inputs
    scale_factor = val_HCserv / x[k_NL*ns + k_health].sum()

    #filling in
    #stimulus vector and direct emissions of final demand
    Ystim = np.zeros((nr*ns,3))
    Hstim = np.zeros((nq,3))
    Vstim = np.zeros((nv,3))

    Ystim[:,0] = Z[:,k_NL*ns + k_health] * scale_factor
    Ystim[:,1] = val_pharm_bp * valloc_pharm  # add proportional import distribution 
    Ystim[:,2] = val_appl_bp * valloc_appl
    Hstim[:,0] = B[:, k_NL*ns + k_health] * (x[k_NL*ns + k_health] * scale_factor) 
    Hstim[k_GWP,0] = val_GWP_health 
    Vstim[:,0] = V[:, k_NL*ns + k_health] * scale_factor


    #agg grand total to first col in stimulus
    Ystim = np.concatenate((Ystim.sum(1).reshape((nr*ns,1)), Ystim),1)
    Hstim = np.concatenate((Hstim.sum(1).reshape((nq,1)), Hstim),1)
    Vstim = np.concatenate((Vstim.sum(1).reshape((nv,1)), Vstim),1)

    #converting unit from kgCO2 to ktCO2
    label['characterization']['Unit'][0] = 'ktCO2eq'
    Hstim[0,:] = Hstim[0,:] * 1e-6
    H[0,:] = H[0,:] * 1e-6
    B[0,:] = B[0,:] * 1e-6

    label['characterization']['Unit'][6] = 'kt'
    Hstim[-1,:] = Hstim[-1,:] * 1e-3
    H[-1,:] = H[-1,:] * 1e-3
    B[-1,:] = B[-1,:] * 1e-3

    ##############################################
    #Save relevant objects as background

    sheetname = ['all_sec_all_reg', 'agg_sec_all_reg', 'agg_sec_agg_reg', 'all_sec_sin_reg', 'agg_sec_sin_reg', 'sin_sec_all_reg', 'sin_sec_agg_reg']

    sheettext = ['Breakdown by all regions and all sectors',  'Breakdown by all regions and aggregate sectors', 'Breakdown by aggregate regions and aggregate sectors', 'Breakdown by all sectors (in the world)', 'Breakdown by aggregate sectors (in the world)', 'Breakdown by all regions (all economy)', 'Breakdown by aggregate regions (all economy)']

    excelname = ['healthcare_total', 'healthcare_only', 'pharmaceuticals', 'appliances']

    exceltext = ['Healthcare combined with household purchases of pharmaceuticals and medical appliances', 'Healthcare sector only', 'Household purchases of pharmaceuticals', 'Household purchases of medical appliances']

    
    bg = {'label': label, 'ragg': ragg, 'L': L, 'A': A,  'B': B, 'H': H, 'Y': Y, 'Q':Q, 'Ystim': Ystim, 'Vstim': Vstim, 'Hstim': Hstim, 'sheetname': sheetname, 'sheettext': sheettext, 'excelname': excelname, 'exceltext': exceltext}

    pkl_str = 'gddz_background_information_' + year + '.pkl'  
    pkl_out = open(bg_dir + pkl_str,"wb")
    pkl.dump(bg, pkl_out)
    pkl_out.close()

    tend = time.time()
    print('Prepared background in %5.2f s\n'% (tend - tstart))
    tstart = time.time()

    return bg
##############################################


##############################################
# Functions for footprint calculation
##############################################

# Hotspot analysis / indirect footprint broken down from production perspective
def calc_hotspot(B, L, Y):
    R = []
    for k in range(Y.shape[1]):
        LxY = np.diag(np.dot(L,Y[:,k]))
        R_ = np.dot(B, LxY) 
        R.append(R_.T)
    return R

# Contribution analysis /indirect footprint broken down from consumption perspective
def calc_contrib(B, L, Y):
    R = []
    for k in range(Y.shape[1]):
        BxL = np.dot(B, L)
        R_ = np.dot(BxL, np.diag(Y[:,k]))
        R.append(R_.T)        
    return R

# Make dataframe from the array results from calc_contrib() and calc_hotspot()
def df_fromarray(arrs_hotspot, char_labels, multiindex, cols_impcat):
    l_df = []
    for i in range(len(arrs_hotspot)):
        df = pd.DataFrame(arrs_hotspot[i], columns = char_labels, index = multiindex)
        df = df[cols_impcat].reset_index()
        df.columns = ['ISO3', 'SecTxtCode'] + cols_impcat
        l_df.append(df)
    return l_df



##############################################
# functions to adapt for scenarios for B, Y and Y
##############################################

# new B
def adapt_B(bg, multiindex, charlabels, *args):
    B = pd.DataFrame(bg['B'], columns = multiindex, index = charlabels)
    for x in args:
        B.loc[x[0], (x[1],x[2])] = x[3]
    B = B.to_numpy()
    return B

# new Ystim
def adapt_Ystim(bg, multiindex, *args):
    Y = pd.DataFrame(bg['Ystim'], columns = ['Tot','HC','Pharm','Appl'], index = multiindex)
    for x in args:
        Y.loc[(x[0], x[1]),x[2]] = x[3]
    Y['Tot'] = Y['HC'] +Y['Pharm'] +Y['Appl']
    Y = Y.to_numpy()     # terug naar numpy array
    return Y

# new A
def adapt_A(bg, multiindex, *args):
    A = pd.DataFrame(bg['A'], columns = multiindex, index = multiindex)
    for x in args:
        A.loc[(x[0], x[1]), (x[2],x[3])] = x[4]
    A = A.to_numpy()     # terug naar numpy array
    return A

# new L
def calcnew_L(bg):
    L = np.linalg.inv(np.eye(163*49) - bg['A'])  
    return L


