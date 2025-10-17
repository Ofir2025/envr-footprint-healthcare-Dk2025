# envr-footprint-healthcare - The environmental footprint of the Dutch healthcare sector
This project contains the model and some of the input data for the paper: 
*The environmental footprint of the Dutch healthcare sector: beyond environmental impact*
*Steenmeijer MA, Rodrigues JFD, Zijp MC, Waaijers-van der Loop SL. The Lancet Planetary Health (in press)*

The work is part of a research project at the RIVM - the national institute for public health and the environment, on building a knowledge base to support the healthcare sector in becoming more sustainable.

## Getting started (steps for the first run)
### Step 1: Additional input data
After cloning the project from this repository, it is necessary to download the **Exiobase 3.7 IOT_2016_ixi zip folder** from Zenodo: https://zenodo.org/record/3583071#.Y0MV7NhBw2w .
The unzipped file should be placed in the **exiobase_v3.7** folder under the data folder. Do not change anything about the folder structure or the name of the Exiobase file.  
It is both possible to use newer versions (3.8 and up) and other years, but at this point it will  require manual adjustments in the model's scripts (e.g. F_hh should be changed into F_Y when using v3.8).

### Step 2: First run, preparing pickled EE-IO files
Before running the main script the first time, the Exiobase data will be processed into several pickled files. These files will later on be used to create the so-called **background** that contains all the elements needed for the main script.
Four scripts are used, that can be found under the **prep_background** folder under the scripts folder. 
These scripts need to be executed in the following order:
1. **exiobase_3_7-load.py**, this script filters for the desired impact category, and processes the required Exiobase files into a pickled dictionary
2. **exiobase_3_7-leontief.py**, this script calculates and pickles the Leontief inverse from the dictionary
3. **exiobase_3_7-process.py**, this script calculates and pickles the total input (**x**) and the transaction matrix (**Z**)
4. **exiobase_3_7-waste.py**, this script processes and pickles the waste production extension from the hybrid SUT.

The output for these scripts are automatically placed in the **pickled_mrio** folder, under the **bg** (background) folder within the data folder.

## Running the main script (main.py)
By running main.py, functions are imported from **functions.py**. Depending on your IDE and whether you execute the code by blocks or not, you might have to manually adjust the code for the path to the functions.py file for importing the background functions. The first run will produce two intermediate data files, which can be used in the following runs to speed up the process (see 2a and 2b). 
The output from the model is stored in the **output** folder. 

### Output
For some of the output files, we use the following abbreviations
- **aggsec** = results aggregated on aggregated sector groups (19 groups)
- **aggsec_aggreg** = results aggregated on aggregated sector groups and global regions (19 sector groups for 6 global regions)
- **allsec** = = results aggregated on sector (163 sectors)
- **full** = unaggregated results, complete list (163 sectors for 49 countries/regions)



