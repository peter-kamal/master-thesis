# DATA ANALYSIS SCRIPT FOR WOLF-DEER-MODEL IN LOGGED FOREST

# Author: Peter Kamal
# Python version: 3.9.13
# Last update: 05/09/23

# Note: This takes the full data sets generated from 'ecol_2_data_transformation.py' and produces the graphs for the paper.
# Graphs can be produced with titles and notes, this part is commented out.

#------------------------------------------------------------------------------

# IMPORTS
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from statistics import mean
import os

os.chdir('C:/Users/Kamal/OneDrive/TSE/M2 EE/thesis/ecol/model/output/')

#------------------------------------------------------------------------------

# GLOBAL PARAMETERS
length_year = 360
start_of_logging = 5*length_year
stop_of_logging = 6*length_year
end_of_seral_forest = 4*length_year

#------------------------------------------------------------------------------

# GLOBAL FUNCTIONS TO CALCULATE STATS

def calculate_extinction_rate(data, animal, n_simulations):
    
    # Function calculates percentage of simulations in which a population went extinct
    # Takes a dataset in wide format, and 'Wolves' or 'Deer' as input.

    subset = data.filter(regex = 'n_'+animal)
    extinction_counter = 0
    for column in subset:
        if 0 in subset[column].unique():
            extinction_counter += 1
            
    return round((extinction_counter/n_simulations)*100,1)


def calculate_mean_pop_size(data, animal, cutoff):
    
    # Function calculates mean population size per animal post a cutoff
    # Takes wide format data and strings for the animal names
    
    subset = (data.loc[data.timestep >= cutoff]).filter(regex = 'n_'+animal)

    means_per_sim = []

    for column in subset:
        means_per_sim.append(mean(subset[column]))
    
    return mean(means_per_sim)


def calculate_mean_hr_size(data, animal, cutoff):
    
    # Function calculates mean home range sizes per animal post a cutoff
    # Takes wide format data and strings for the animal names
    
    subset = (data.loc[data.timestep >= cutoff]).filter(regex = 'hr_'+animal)

    means_per_sim = []
    
    for column in subset:
        
        unfiltered = subset[column]
        filtered = [i for i in unfiltered if i != 0]
        
        if len(filtered) > 0:
            means_per_sim.append(mean(filtered))
        
    if len(means_per_sim) > 10:
        return mean(means_per_sim)
    else:
        return np.nan
    
def calculate_extinction_timing(data, animal):
    
    # Function calculates the timing in days of an extinction given a wide-format data set
    
    subset = data.filter(regex='n_'+animal)
    timing = []
    for column in subset:
        if 0 in subset[column].unique():
            index = (subset[column] == 0).idxmax()
            timing.append(index)
        else:
            timing.append(np.nan)
    
    return timing
        

def mean_excluding_zero(vec):
    
    # Function calculates the mean of a vector including elements that are 0
    
    nonzero = [elem for elem in vec if elem != 0]
    if len(nonzero) > 0:
        return sum(nonzero) / len(nonzero)
    else:
        return np.nan




#------------------------------------------------------------------------------

# FUNCTIONS TO CREATE THE DIFFERENT GRAPHS DEPENDING ON SCENARIO

def graph_deer_only(n_simulations, version, parameter):
    
    # This is Figure 9 in the paper.
    
    # Function graphs deer population dynamics for a set of simulations with logging,
    # but without predatory pressure from wolves. Shows direct effects of biomass growth,
    # as well as the carrying capacities under different forest scenarios.
    
    data = pd.read_csv('deer_only/pop_dynam_full_deer_only_'+str(parameter)+'_v'+str(version)+'.csv')

    final_data = pd.wide_to_long(data,['n_Deer','n_Wolves', 'hr_Deer', 'hr_Wolves'], sep = '_', i = 'timestep', j = 'sim').reset_index()

    fig = sns.relplot(final_data, kind='line', x = 'timestep',y = 'n_Deer', errorbar='sd', height = 5, aspect = 1.6)
    fig.set_axis_labels('Days', 'Population size')
    # fig.fig.suptitle("Deer population dynamics absent predatory pressure", x = 0.5, y = 1.1, fontsize = 16)
    # fig.fig.text(0.5, 1.03, 'The figure depicts mean population levels +/- 1 standard deviation averaged over N=' + str(n_simulations) + ' simulations.' +
    #               '\nThis is a model without wolves/predatory pressure. In year 5, there is one year of logging, in which ' + str(round(parameter*9*100/121,1)) + '% of the forest is clear-cut.', 
    #               wrap=True, horizontalalignment='center', fontsize=10)
    plt.axvline(x = start_of_logging, color = 'black', linestyle = '--', linewidth = 1)
    plt.axvline(x = stop_of_logging, color = 'black', linestyle = '--', linewidth = 1)
    plt.axvline(x = stop_of_logging + end_of_seral_forest, color = 'black', linestyle = '--', linewidth = 1)
    plt.annotate("Start of logging", (880,750), fontsize = 9)
    plt.annotate("Seral forest", (2220,750), fontsize = 9)
    plt.annotate("Closed canopy new-growth", (3700,750), fontsize = 9)
    plt.savefig('+graphs/deer_only_v' + str(version) + '.png', dpi= 300, bbox_inches='tight')



def graph_predator_prey(n_simulations,version, post_eq_time):
    
    # This is Figure 11 in the paper.
    
    # Function graphs daily mean population levels +/- 1 sdev. for both animals in the scenario
    # without logging. Could be used for all other single scenarios if slightly adapted.
    
    data = pd.read_csv('logging_intensity/v'+str(version)+'/pop_dynam_full_log_int_0_v'+str(version)+'.csv')
    interim = pd.wide_to_long(data,['n_Deer','n_Wolves', 'hr_Deer', 'hr_Wolves'], sep = '_', i = 'timestep', j = 'sim').reset_index()
    final_data = pd.wide_to_long(interim, stubnames = ['n','hr'], i = ['timestep','sim'], j = 'Animal', sep = '_', suffix=r'\w+').reset_index()


    fig = sns.relplot(final_data, kind='line', x = 'timestep',y = 'n', errorbar='sd', hue='Animal', height = 5, aspect = 1.6)
    fig.set_axis_labels('Days', 'Population size')
    for i in range(1,15):
        plt.axvline(x = i*360, color = 'grey', linestyle = '-', alpha = 0.3)
    plt.savefig('+graphs/predator_prey_v' + str(version) + '.png', dpi= 300, bbox_inches='tight')



def graph_population_sizes(n_simulations, parameters_unprotected, parameters_protected, version, post_eq_time):

    # This is Figure 12 in the paper.
    
    # Function graphs mean deer and wolf population sizes +/- 1 standard deviation in both logging 
    # scenarios as a function of logging pressure.
    
    
    scattered = pd.read_csv('logging_intensity/v'+str(version)+'/pop_dynam_full_log_int_'+str(parameters_unprotected[0])+'_v'+str(version)+'.csv')   
    scattered = (scattered.loc[scattered.timestep >= post_eq_time]).filter(regex = 'timestep|n_')
    scattered = pd.wide_to_long(scattered, ['n_Deer','n_Wolves'], 'timestep', 'sim', sep = '_').reset_index()
    scattered = (scattered.groupby('sim').mean().reset_index()).drop('timestep', axis=1)
    scattered = scattered.rename(columns={'n_Deer': 'n_Deer_Scattered_'+str(parameters_unprotected[0]), 'n_Wolves': 'n_Wolves_Scattered_'+str(parameters_unprotected[0])})


    for i in parameters_unprotected[1:]:
         
          addon = pd.read_csv('logging_intensity/v'+str(version)+'/pop_dynam_full_log_int_'+str(i)+'_v'+str(version)+'.csv')
          addon = (addon.loc[addon.timestep >= post_eq_time]).filter(regex = 'timestep|n_')
          addon = pd.wide_to_long(addon, ['n_Deer','n_Wolves'], 'timestep', 'sim', sep = '_').reset_index()
          addon = (addon.groupby('sim').mean().reset_index()).drop('timestep', axis=1)
          addon = addon.rename(columns={'n_Deer': 'n_Deer_Scattered_'+str(i), 'n_Wolves': 'n_Wolves_Scattered_'+str(i)})
          scattered = pd.merge(scattered, addon, how='left', on = 'sim')
             
            
    targeted = pd.read_csv('protection/v'+str(version)+'/pop_dynam_only_prot_'+str(parameters_protected[0])+'_v'+str(version)+'.csv')   
    targeted = (targeted.loc[targeted.timestep >= post_eq_time]).filter(regex = 'timestep|n_')
    targeted = pd.wide_to_long(targeted, ['n_Deer','n_Wolves'], 'timestep', 'sim', sep = '_').reset_index()
    targeted = (targeted.groupby('sim').mean().reset_index()).drop('timestep', axis=1)
    targeted = targeted.rename(columns={'n_Deer': 'n_Deer_Targeted_'+str(parameters_protected[0]), 'n_Wolves': 'n_Wolves_Targeted_'+str(parameters_protected[0])})


    for i in parameters_protected[1:]:
         
          addon = pd.read_csv('protection/v'+str(version)+'/pop_dynam_only_prot_'+str(i)+'_v'+str(version)+'.csv')
          addon = (addon.loc[addon.timestep >= post_eq_time]).filter(regex = 'timestep|n_')
          addon = pd.wide_to_long(addon, ['n_Deer','n_Wolves'], 'timestep', 'sim', sep = '_').reset_index()
          addon = (addon.groupby('sim').mean().reset_index()).drop('timestep', axis=1)
          addon = addon.rename(columns={'n_Deer': 'n_Deer_Targeted_'+str(i), 'n_Wolves': 'n_Wolves_Targeted_'+str(i)})
          targeted = pd.merge(targeted, addon, how='left', on = 'sim')
         
    full = pd.merge(scattered, targeted, how = 'left', on = 'sim')
    
    full = pd.wide_to_long(full, stubnames = ['n_Deer_Scattered', 'n_Wolves_Scattered', 'n_Deer_Targeted', 'n_Wolves_Targeted'], i = 'sim', j = 'Logging pressure', sep='_').reset_index()
    full = pd.wide_to_long(full, ['n_Deer', 'n_Wolves'], ['sim', 'Logging pressure'], 'Logging', sep = '_', suffix=r'\w+').reset_index()
    full = pd.wide_to_long(full, 'n', ['sim', 'Logging pressure', 'Logging'], 'Animal', sep = '_', suffix=r'\w+').reset_index()
    
    
    fig = sns.FacetGrid(data = full, col = 'Animal', hue='Logging', hue_order = ['Targeted', 'Scattered'], height=4, aspect = 1.2, sharey=False)
    fig.map_dataframe(sns.lineplot, x= 'Logging pressure', y= 'n', errorbar= 'sd', marker = 'o')
    fig.add_legend()
    fig.set_axis_labels('Logging pressure', 'Avg. population size')
    
    plt.savefig('+graphs/pop_size_v' + str(version) + '.png', dpi= 300, bbox_inches='tight')



def graph_hr_sizes(n_simulations, parameters_unprotected, parameters_protected, version, post_eq_time):

    # This is Figure 13 in the paper.
    
    # Function graphs mean deer and wolf home range sizes +/- 1 standard deviation in both logging 
    # scenarios as a function of logging pressure.
    
    scattered = pd.read_csv('logging_intensity/v'+str(version)+'/pop_dynam_full_log_int_'+str(parameters_unprotected[0])+'_v'+str(version)+'.csv')   
    scattered = (scattered.loc[scattered.timestep >= post_eq_time]).filter(regex = 'timestep|hr_')
    scattered = pd.wide_to_long(scattered, ['hr_Deer','hr_Wolves'], 'timestep', 'sim', sep = '_').reset_index()
    scattered = (scattered.groupby('sim').agg(mean_excluding_zero).reset_index()).drop('timestep', axis=1)
    scattered = scattered.rename(columns={'hr_Deer': 'hr_Deer_Scattered_'+str(parameters_unprotected[0]), 'hr_Wolves': 'hr_Wolves_Scattered_'+str(parameters_unprotected[0])})


    for i in parameters_unprotected[1:]:
         
          addon = pd.read_csv('logging_intensity/v'+str(version)+'/pop_dynam_full_log_int_'+str(i)+'_v'+str(version)+'.csv')
          addon = (addon.loc[addon.timestep >= post_eq_time]).filter(regex = 'timestep|hr_')
          addon = pd.wide_to_long(addon, ['hr_Deer','hr_Wolves'], 'timestep', 'sim', sep = '_').reset_index()
          addon = (addon.groupby('sim').agg(mean_excluding_zero).reset_index()).drop('timestep', axis=1)
          addon = addon.rename(columns={'hr_Deer': 'hr_Deer_Scattered_'+str(i), 'hr_Wolves': 'hr_Wolves_Scattered_'+str(i)})
          scattered = pd.merge(scattered, addon, how='left', on = 'sim')
             
            
    targeted = pd.read_csv('protection/v'+str(version)+'/pop_dynam_only_prot_'+str(parameters_protected[0])+'_v'+str(version)+'.csv')   
    targeted = (targeted.loc[targeted.timestep >= post_eq_time]).filter(regex = 'timestep|hr_')
    targeted = pd.wide_to_long(targeted, ['hr_Deer','hr_Wolves'], 'timestep', 'sim', sep = '_').reset_index()
    targeted = (targeted.groupby('sim').agg(mean_excluding_zero).reset_index()).drop('timestep', axis=1)
    targeted = targeted.rename(columns={'hr_Deer': 'hr_Deer_Targeted_'+str(parameters_protected[0]), 'hr_Wolves': 'hr_Wolves_Targeted_'+str(parameters_protected[0])})


    for i in parameters_protected[1:]:
         
          addon = pd.read_csv('protection/v'+str(version)+'/pop_dynam_only_prot_'+str(i)+'_v'+str(version)+'.csv')
          addon = (addon.loc[addon.timestep >= post_eq_time]).filter(regex = 'timestep|hr_')
          addon = pd.wide_to_long(addon, ['hr_Deer','hr_Wolves'], 'timestep', 'sim', sep = '_').reset_index()
          addon = (addon.groupby('sim').agg(mean_excluding_zero).reset_index()).drop('timestep', axis=1)
          addon = addon.rename(columns={'hr_Deer': 'hr_Deer_Targeted_'+str(i), 'hr_Wolves': 'hr_Wolves_Targeted_'+str(i)})
          targeted = pd.merge(targeted, addon, how='left', on = 'sim')
         
    full = pd.merge(scattered, targeted, how = 'left', on = 'sim')
    
    full = pd.wide_to_long(full, stubnames = ['hr_Deer_Scattered', 'hr_Wolves_Scattered', 'hr_Deer_Targeted', 'hr_Wolves_Targeted'], i = 'sim', j = 'Logging pressure', sep='_').reset_index()
    full = pd.wide_to_long(full, ['hr_Deer', 'hr_Wolves'], ['sim', 'Logging pressure'], 'Logging', sep = '_', suffix=r'\w+').reset_index()
    full = pd.wide_to_long(full, 'hr', ['sim', 'Logging pressure', 'Logging'], 'Animal', sep = '_', suffix=r'\w+').reset_index()
    
    fig = sns.FacetGrid(data = full, col = 'Animal', hue='Logging', hue_order = ['Targeted', 'Scattered'], height=4, aspect = 1.2, sharey=False)
    fig.map_dataframe(sns.lineplot, x= 'Logging pressure', y= 'hr', errorbar= 'sd', marker = 'o')
    fig.add_legend()
    fig.set_axis_labels('Logging pressure', 'Avg. home range size')
    
    plt.savefig('+graphs/hr_size_v' + str(version) + '.png', dpi= 300, bbox_inches='tight')


    
def graph_extinction_rate(n_simulations, parameters_unprotected, parameters_protected, version, post_eq_time):
    
    # This is Figure 14 in the paper.
    
    # Function graphs percentage of simulations in which the wolf population went extinct for both logging 
    # scenarios as a function of logging pressure.
    
    ext_rate = []

    for i in parameters_unprotected:
        pop_dynam = pd.read_csv('logging_intensity/v'+str(version)+'/pop_dynam_full_log_int_'+str(i)+'_v'+str(version)+'.csv')        
        ext_rate.append(calculate_extinction_rate(pop_dynam, 'Wolves', n_simulations))

    data = pd.DataFrame()
    data['Logging pressure'] = parameters_unprotected
    data['Extinction rate_Scattered'] = ext_rate
    
    ext_rate = []
    
    for i in parameters_protected:
        pop_dynam = pd.read_csv('protection/v'+str(version)+'/pop_dynam_only_prot_'+str(i)+'_v'+str(version)+'.csv')
        ext_rate.append(calculate_extinction_rate(pop_dynam, 'Wolves', n_simulations))
        
    addon = pd.DataFrame()
    addon['Logging pressure'] = parameters_protected
    addon['Extinction rate_Targeted'] = ext_rate  
    
    data = pd.merge(data, addon, how = 'outer', on='Logging pressure')
    plot_data = pd.wide_to_long(data, 'Extinction rate', 'Logging pressure', 'Logging', sep='_', suffix=r'\w+').reset_index()
    
    plt.figure(figsize = (8,5))
    sns.lineplot(data = plot_data, x = 'Logging pressure', y = 'Extinction rate', hue = 'Logging', hue_order = ['Targeted', 'Scattered'], marker = 'o')
    plt.savefig('+graphs/extinction_rate_v' + str(version) + '.png', dpi= 300, bbox_inches='tight')



def graph_protection(n_simulations, version, parameter, post_eq_time):
    
    # This is Figure 15 in the paper.
    
    # Function graphs daily mean deer and wolf population dynamics +/- 1 standard deviation for both logging scenarios.
    
    data = pd.read_csv('protection/v'+str(version)+'/pop_dynam_full_prot_'+str(parameter)+'_v'+str(version)+'.csv')
    
    first_step = pd.wide_to_long(data,['n_Deer_unprotected','n_Wolves_unprotected','n_Deer_protected','n_Wolves_protected',
                                       'hr_Deer_unprotected','hr_Wolves_unprotected','hr_Deer_protected','hr_Wolves_protected'], sep = '_', i = 'timestep', j = 'sim').reset_index()
    second_step = pd.wide_to_long(first_step, ['n_Deer','n_Wolves', 'hr_Deer','hr_Wolves'], sep = '_', i = ['timestep','sim'], j = 'Forest', suffix=r'\w+').reset_index()
    final_data = pd.wide_to_long(second_step, stubnames = ['n','hr'], i = ['timestep','sim','Forest'], j = 'Animal', sep = '_', suffix=r'\w+').reset_index()

    final_data = final_data.rename(columns={'Forest': 'Logging'})
    final_data['Logging'] = final_data['Logging'].replace({'protected':'Targeted', 'unprotected':'Scattered'})  
    
    fig = sns.FacetGrid(data = final_data, col = 'Animal', hue='Logging', hue_order = ['Targeted', 'Scattered'], height=4, aspect = 1.2, sharey=False)
    fig.map_dataframe(sns.lineplot, x= 'timestep', y= 'n', errorbar= 'sd')
    fig.add_legend()
    fig.set_axis_labels('Days', 'Population size')
    fig.map(plt.axvline, x = start_of_logging, color = 'black', linestyle = '--', linewidth = 1)
    fig.map(plt.axvline, x = stop_of_logging, color = 'black', linestyle = '--', linewidth = 1)
    fig.map(plt.axvline, x = stop_of_logging + end_of_seral_forest, color = 'black', linestyle = '--', linewidth = 1)

    plt.savefig('+graphs/protection_'+str(parameter)+'_v' + str(version) + '.png', dpi= 300, bbox_inches='tight')



def graph_extinction_timing(n_simulations, version, parameter):
    
    # This is Figure 16 in the paper.
    
    # Function graphs a layered histogram comparing extinction timings between the two logging scenarios.
    
    data = pd.read_csv('protection/v'+str(version)+'/pop_dynam_full_prot_'+str(parameter)+'_v'+str(version)+'.csv')

    extinction_data = pd.DataFrame(list(range(1,n_simulations+1)), columns= ['Simulation'])
    
    for i in ["unprotected", "protected"]:
        timing = calculate_extinction_timing(data, 'Wolves_'+i)
        extinction_data['Timing_'+i] = timing
        
    plot_data = pd.wide_to_long(extinction_data, 'Timing', 'Simulation', 'Forest', sep='_', suffix =r'\w+').reset_index()
    
    plt.figure(figsize = (8,5))
    sns.histplot(data=plot_data, x ='Timing', hue = 'Forest', hue_order = ['protected','unprotected'])
    plt.legend(labels = ['Scattered', 'Targeted'])
    plt.axvline(x = stop_of_logging + end_of_seral_forest, color = 'black', linestyle = '--')
    plt.annotate('End of seral forest',(3000,80), fontsize = 9)
    plt.savefig('+graphs/extinction_timing_'+str(parameter)+'_v' + str(version) + '.png', dpi= 300, bbox_inches='tight')
    
    
#------------------------------------------------------------------------------

# EXECUTE

#graph_deer_only(n_simulations = 100, version = 1, parameter = 8)
#graph_predator_prey(n_simulations = 1000, version = 1, post_eq_time = 4000)
#graph_population_sizes(n_simulations= 1000, parameters_unprotected = list(range(0,14)), parameters_protected = list(range(1,13)) , version = 1, post_eq_time = 4000)
#graph_hr_sizes(n_simulations= 1000, parameters_unprotected = list(range(0,14)), parameters_protected = list(range(1,13)) , version = 1, post_eq_time = 4000)
#graph_extinction_rate(n_simulations= 1000, parameters_unprotected = list(range(0,14)), parameters_protected = list(range(1,13)) , version = 1, post_eq_time = 4000)
#graph_protection(n_simulations = 1000, version = 1, parameter = 7, post_eq_time = 4000)
#graph_extinction_timing(n_simulations = 1000, version = 1, parameter = 7)

