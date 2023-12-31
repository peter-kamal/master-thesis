# Master Thesis Code Repository
This repository stores all the codes necessary to replicate the results from my master's thesis in the M2 Economics &amp; Ecology at Toulouse School of Economics.

If you have any questions, address them to peter.kamal@t-online.de 


There are two main parts: 
1. The economic one, in which I perform a policy impact evaluation with satellite deforestation data.
2. The ecological one, in which I construct an agent-based model of wolves and deer in a dynamic forest.

The files are coded econ/ecol depending on which part they belong to, and the numbers indicate the order in which they are to be run.

## Economic Part

This part consists of six scripts of code:
1. 'econ_1_satellite_calculations': This is a piece of Javascript code to be used in the Google Earth Engine API. It calculates forest cover (loss) for the entirety of BC between 2000 and 2021.
2. 'econ_2_shapefile_creation': This is an R Notebook that constructs the shapefile underlying the main dataset. It merges a 1:20000 grid with different land use zones and regional districts, and outputs shapefiles to be ingested in GEE.
3. 'econ_3_satellite_raw_export': This is the second piece of JavaScript code to be used in the GEE API. It takes the output of the first two scripts together, calculates forest cover loss for each spatial unit, and exports this dataset.
4. 'econ_4_webscraper': This is a small piece of Python code to webscrape weather data from the Canadian goverment.
5. 'econ_5_dataset_creation': This is an R Notebook that merges all the exported satellite data together and matches it with the webscraped weather data. It exports an analysis-ready data set and creates two maps used in the paper.
6. 'econ_6_analysis': This is an R Notebook that takes the analysis-ready dataset and produces the different graphs and analyses used and mentioned in the paper.

While all the data (shapefiles, satellite data, etc.) is publicly available and referenced in the codes and paper, steps 1-5 have very long computation times. To make replication of the analysis easier, I provide the analysis-ready dataset on Figshare (accessible through the paper).

## Ecological Part

This part consists of three scripts of code:
1. 'ecol_1_model': This is the core model (written in Python). All simulations are run with this piece of code.
2. 'ecol_2_data_transformation': The model outputs single .csv files for each simulation. This file merges all the files from one batch of simulations into a large, analysis-ready data set.
3. 'ecol_3_data_analysis': This piece analyses the merged datasets and produces the different graphs for the paper.

As this is a simulation, replication is inherently easy (notwithstanding computation time). I did not have sufficient cloud storage to provide all the data that is used to produce the graphs. I can provide it if necessary.
