# DATA CONVERSION FILE FOR WOLF-DEER-MODEL IN LOGGED FOREST

# Author: Peter Kamal
# Python version: 3.9.13
# Last update: 21/07/23

# Note: The main model script exports one excel file per simulation. 
# This script merges the files together depending on the scenario and output.

#------------------------------------------------------------------------------

# SETUP

import pandas as pd
import os

os.chdir('C:/Users/Kamal/OneDrive/TSE/M2 EE/thesis/ecol/model/output/')

#------------------------------------------------------------------------------

# FUNCTIONS TO TRANSFORM THE MANY DATASETS GENERATED IN THE MAIN SCRIPT INTO SINGLE ONES

def create_pop_dynam(scenario,n_simulations,version,parameter):
    
    # This is a function that imports all the relevant population dynamics datasets, merges them, and exports them.
    # Input one of four scenarios: 
    # 1. logging_intensity (i.e. unprotected forest at a specific logging intensity), 
    # 2. protection_only (i.e. protected forest at a specific logging intensity), 
    # 3. protection_full (both unprotected and protected forest at a specific logging intensity), 
    # 4. deer_only (deer absent predatory pressure under unprotected logging)
    # Also input the number of simulations, the version and the logging parameter.
    
    if scenario == 'logging_intensity':
    
        data = pd.read_csv(scenario+'/v'+str(version)+'/'+str(parameter)+'/pop_dynam_1.csv')
        data.columns = ['timestep', 'n_Deer_1', 'n_Wolves_1', 'hr_Deer_1', 'hr_Wolves_1']
    
        for i in range(2,n_simulations + 1):
            addon = pd.read_csv(scenario+'/v'+str(version)+'/'+str(parameter)+'/pop_dynam_'+str(i)+'.csv')
            addon.columns = ['timestep', 'n_Deer_' + str(i), 'n_Wolves_' + str(i), 'hr_Deer_'+str(i), 'hr_Wolves_'+str(i)]
            data = pd.merge(data, addon, on='timestep')
            
        data.to_csv(scenario+'/v'+str(version)+'/pop_dynam_full_log_int_'+str(parameter)+'_v'+str(version)+'.csv', index=False)
        
    elif scenario == 'protection_only':
        
        data = pd.read_csv('protection/v' + str(version) + '/' + str(parameter) + '/pop_dynam_1.csv')
        data.columns = ['timestep', 'n_Deer_1', 'n_Wolves_1', 'hr_Deer_1', 'hr_Wolves_1']
        
        for i in range(2,n_simulations + 1):
            addon = pd.read_csv('protection/v' + str(version) + '/' + str(parameter) + '/pop_dynam_'+str(i)+'.csv')
            addon.columns = ['timestep', 'n_Deer_' + str(i), 'n_Wolves_' + str(i), 'hr_Deer_'+str(i), 'hr_Wolves_'+str(i)]
            data = pd.merge(data, addon, on='timestep')
            
        data.to_csv('protection/v' + str(version) + '/pop_dynam_only_prot_'+str(parameter)+'_v'+ str(version) +'.csv',index = False)

    
    elif scenario == 'protection_full':
        
        data = pd.read_csv('logging_intensity/v' + str(version) + '/' + str(parameter) + '/pop_dynam_1.csv')
        data.columns = ['timestep', 'n_Deer_unprotected_1', 'n_Wolves_unprotected_1', 'hr_Deer_unprotected_1', 'hr_Wolves_unprotected_1']
        addon = pd.read_csv('protection/v' + str(version) + '/' + str(parameter) + '/pop_dynam_1.csv')
        addon.columns = ['timestep', 'n_Deer_protected_1', 'n_Wolves_protected_1', 'hr_Deer_protected_1', 'hr_Wolves_protected_1']
        data = pd.merge(data,addon, on = 'timestep')


        for i in range(2,n_simulations + 1):
            addon = pd.read_csv('logging_intensity/v' + str(version) + '/' + str(parameter) + '/pop_dynam_'+str(i)+'.csv')
            addon.columns = ['timestep', 'n_Deer_unprotected_' + str(i), 'n_Wolves_unprotected_' + str(i), 'hr_Deer_unprotected_' + str(i), 'hr_Wolves_unprotected_' + str(i)]
            data = pd.merge(data, addon, on='timestep')
            addon = pd.read_csv('protection/v' + str(version) + '/' + str(parameter) + '/pop_dynam_' + str(i) + '.csv')
            addon.columns = ['timestep', 'n_Deer_protected_' + str(i), 'n_Wolves_protected_' + str(i), 'hr_Deer_protected_' + str(i), 'hr_Wolves_protected_' + str(i)]
            data = pd.merge(data, addon, on='timestep')
            
        data.to_csv('protection/v' + str(version) + '/pop_dynam_full_prot_'+str(parameter)+'_v'+ str(version) +'.csv',index = False)
    
    elif scenario == 'deer_only':
        
        data = pd.read_csv(scenario+'/v'+str(version)+'/pop_dynam_1.csv')
        data.columns = ['timestep', 'n_Deer_1', 'n_Wolves_1', 'hr_Deer_1', 'hr_Wolves_1']
    
        for i in range(2,n_simulations + 1):
            addon = pd.read_csv(scenario+'/v'+str(version)+'/pop_dynam_'+str(i)+'.csv')
            addon.columns = ['timestep', 'n_Deer_' + str(i), 'n_Wolves_' + str(i), 'hr_Deer_' + str(i), 'hr_Wolves_' + str(i)]
            data = pd.merge(data, addon, on='timestep')
            
        data.to_csv(scenario+'/pop_dynam_full_'+scenario+'_'+str(parameter)+'_v'+str(version)+'.csv', index=False)
        

#------------------------------------------------------------------------------

# EXECUTE 
# create_pop_dynam(scenario = 'logging_intensity',n_simulations = 1000, version = 1, parameter = 1)
