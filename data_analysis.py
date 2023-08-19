# DATA ANALYSIS SCRIPT FOR WOLF-DEER-MODEL IN LOGGED FOREST
# Author: Peter Kamal
# Python version: 3.9.13
# Last update: 21/07/23

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
    
    subset = data.filter(regex='n_'+animal)
    timing = []
    for column in subset:
        if 0 in subset[column].unique():
            index = (subset[column] == 0).idxmax()
            timing.append(index)
        else:
            timing.append(np.nan)
    
    return timing
        


#------------------------------------------------------------------------------

# FUNCTIONS TO CREATE THE DIFFERENT GRAPHS DEPENDING ON SCENARIO

def graph_deer_only(n_simulations, version, parameter):
    
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
    
    # Function graphs mean population levels +/- 1 sdev. for both animals in the scenario
    # without logging. Could be used for all other single scenarios if slightly adapted.
    
    data = pd.read_csv('logging_intensity/v'+str(version)+'/pop_dynam_full_log_int_0_v'+str(version)+'.csv')
    interim = pd.wide_to_long(data,['n_Deer','n_Wolves', 'hr_Deer', 'hr_Wolves'], sep = '_', i = 'timestep', j = 'sim').reset_index()
    final_data = pd.wide_to_long(interim, stubnames = ['n','hr'], i = ['timestep','sim'], j = 'Animal', sep = '_', suffix=r'\w+').reset_index()

    extinction_rate = calculate_extinction_rate(data, 'Wolves', n_simulations)
            
    avg_hr_size_deer = calculate_mean_hr_size(data, 'Deer', post_eq_time)
    avg_hr_size_wolf = calculate_mean_hr_size(data, 'Wolves', post_eq_time)

    fig = sns.relplot(final_data, kind='line', x = 'timestep',y = 'n', errorbar='sd', hue='Animal', height = 5, aspect = 1.6)
    fig.set_axis_labels('Days', 'Population size')
    # fig.fig.suptitle("Population dynamics of the base model", x = 0.5, y = 1.1, fontsize = 16)
    # fig.fig.text(0, 1.03, 'The figure depicts mean population levels +/- 1 standard deviation averaged over N=' + str(n_simulations) + ' simulations.' +
    #               ' This is the base model with no change in the forest and predator efficiency at 0.16.' +
    #               '\nExtinctions due to stochasticity occured in ' + str(extinction_rate) + '% of cases. The wolf population did not drop below ' + str(min(interim.n_Wolves)) + '.' + 
    #               ' Avg. HR sizes post-canopy-closure were ' + str(round(avg_hr_size_deer,1)) + ' cells for deer and ' + str(round(avg_hr_size_wolf,1)) + ' for wolves respectively.', 
    #               wrap=True, horizontalalignment='left', fontsize=10)
    plt.savefig('+graphs/predator_prey_v' + str(version) + '.png', dpi= 300, bbox_inches='tight')



def graph_logging_intensity(n_simulations, parameters_unprotected, parameters_protected, version, post_eq_time):
    
    # Function graphs key variable response rates to changes in the logging parameter.
    
    mean_wolf_pop = []
    mean_deer_pop = []
    ext_rate = []
    #ext_tim_spread = []
    mean_hr_deer = []
    mean_hr_wolf = []
    
    for i in parameters_unprotected:
        
        pop_dynam = pd.read_csv('logging_intensity/v'+str(version)+'/pop_dynam_full_log_int_'+str(i)+'_v'+str(version)+'.csv')
    
        #ext_timing = calculate_extinction_timing(pop_dynam, 'Wolves')
    
        mean_deer_pop.append(calculate_mean_pop_size(pop_dynam, 'Deer', post_eq_time))
        mean_wolf_pop.append(calculate_mean_pop_size(pop_dynam, 'Wolves', post_eq_time))
        ext_rate.append(calculate_extinction_rate(pop_dynam, 'Wolves', n_simulations))
        #ext_tim_spread.append(np.nanmax(ext_timing) - np.nanmin(ext_timing))
        mean_hr_deer.append(calculate_mean_hr_size(pop_dynam, 'Deer', post_eq_time))
        mean_hr_wolf.append(calculate_mean_hr_size(pop_dynam, 'Wolves', post_eq_time))


    data = pd.DataFrame()
    data['Logging pressure'] = parameters_unprotected
    data['Value_mean_deer_pop_unprotected'] = mean_deer_pop
    data['Value_mean_wolf_pop_unprotected'] = mean_wolf_pop
    data['Value_extinction_rate_unprotected'] = ext_rate
    #data['Value_extinction_timing_spread'] = ext_tim_spread
    data['Value_mean_hr_size_deer_unprotected'] = mean_hr_deer
    data['Value_mean_hr_size_wolf_unprotected'] = mean_hr_wolf
    
    mean_wolf_pop = []
    mean_deer_pop = []
    ext_rate = []
    mean_hr_deer = []
    mean_hr_wolf = []
    
    for i in parameters_protected:
        
        pop_dynam = pd.read_csv('protection/v'+str(version)+'/pop_dynam_only_prot_'+str(i)+'_v'+str(version)+'.csv')
    
        mean_deer_pop.append(calculate_mean_pop_size(pop_dynam, 'Deer', post_eq_time))
        mean_wolf_pop.append(calculate_mean_pop_size(pop_dynam, 'Wolves', post_eq_time))
        ext_rate.append(calculate_extinction_rate(pop_dynam, 'Wolves', n_simulations))
        mean_hr_deer.append(calculate_mean_hr_size(pop_dynam, 'Deer', post_eq_time))
        mean_hr_wolf.append(calculate_mean_hr_size(pop_dynam, 'Wolves', post_eq_time))


    addon = pd.DataFrame()
    addon['Logging pressure'] = parameters_protected
    addon['Value_mean_deer_pop_protected'] = mean_deer_pop
    addon['Value_mean_wolf_pop_protected'] = mean_wolf_pop
    addon['Value_extinction_rate_protected'] = ext_rate
    #data['Value_extinction_timing_spread'] = ext_tim_spread
    addon['Value_mean_hr_size_deer_protected'] = mean_hr_deer
    addon['Value_mean_hr_size_wolf_protected'] = mean_hr_wolf
    
    data = pd.merge(data, addon, how = 'outer', on='Logging pressure')
    data = pd.wide_to_long(data, ['Value_mean_deer_pop','Value_mean_wolf_pop','Value_extinction_rate','Value_mean_hr_size_deer','Value_mean_hr_size_wolf'], 'Logging pressure', 'Forest', sep='_', suffix=r'\w+').reset_index()
    plot_data = pd.wide_to_long(data, 'Value', ['Logging pressure','Forest'], 'Variable', sep='_', suffix=r'\w+').reset_index()
    
    fig = sns.FacetGrid(data = plot_data, col = 'Variable', hue = 'Forest', hue_order = ['protected','unprotected'], col_wrap=3, height=3, aspect = 1.2, sharey=False)
    fig.map_dataframe(sns.lineplot, x= 'Logging pressure', y= 'Value', marker = 'o')
    fig.add_legend()
    # fig.fig.suptitle("Key variable response to changes in logging pressure", x = 0.5, y = 1.1, fontsize = 16)
    # fig.fig.text(0.5, 1.03, 'The figure depicts the responses of five key variables to changes in logging pressure. Logging pressure is the number of cells logged per month. The variables are: ' +
    #              '\nThe mean size of the both populations after the population has stabilized post-canopy-closure; the % of simulations in which the wolf population has gone extinct, as well as the mean home range sizes (in number of cells) of both deer and wolves.',
    #              wrap=True, horizontalalignment='center', fontsize=10)
    plt.savefig('+graphs/logging_intensity_v' + str(version) + '.png', dpi= 300, bbox_inches='tight')



def graph_protection(n_simulations, version, parameter, post_eq_time):
    
    # Function graphs comparative population dynamics for unrprotected and protected scenarios.
    
    data = pd.read_csv('protection/v'+str(version)+'/pop_dynam_full_prot_'+str(parameter)+'_v'+str(version)+'.csv')
    
    first_step = pd.wide_to_long(data,['n_Deer_unprotected','n_Wolves_unprotected','n_Deer_protected','n_Wolves_protected',
                                       'hr_Deer_unprotected','hr_Wolves_unprotected','hr_Deer_protected','hr_Wolves_protected'], sep = '_', i = 'timestep', j = 'sim').reset_index()
    second_step = pd.wide_to_long(first_step, ['n_Deer','n_Wolves', 'hr_Deer','hr_Wolves'], sep = '_', i = ['timestep','sim'], j = 'Forest', suffix=r'\w+').reset_index()
    final_data = pd.wide_to_long(second_step, stubnames = ['n','hr'], i = ['timestep','sim','Forest'], j = 'Animal', sep = '_', suffix=r'\w+').reset_index()

    # extinction_rates = [calculate_extinction_rate(data, 'Wolves_unprotected', n_simulations),calculate_extinction_rate(data, 'Wolves_protected', n_simulations)]
    # avg_pop_size_deer = [round(calculate_mean_pop_size(data, 'Deer_unprotected', post_eq_time),1),round(calculate_mean_pop_size(data, 'Deer_protected', post_eq_time),1)]
    # avg_pop_size_wolf = [round(calculate_mean_pop_size(data, 'Wolves_unprotected', post_eq_time),1),round(calculate_mean_pop_size(data, 'Wolves_protected', post_eq_time),1)]
    # avg_hr_size_deer = [round(calculate_mean_hr_size(data, 'Deer_unprotected', post_eq_time),1),round(calculate_mean_hr_size(data, 'Deer_protected', post_eq_time),1)]
    # avg_hr_size_wolf = [round(calculate_mean_hr_size(data, 'Wolves_unprotected', post_eq_time),1),round(calculate_mean_hr_size(data, 'Wolves_protected', post_eq_time),1)]
    
    
    fig = sns.FacetGrid(data = final_data, col = 'Forest', hue='Animal', height=4, aspect = 1.2)
    fig.map_dataframe(sns.lineplot, x= 'timestep', y= 'n', errorbar= 'sd')
    fig.add_legend()
    # fig.fig.suptitle("Population dynamics with and without forest protection", x = 0.5, y = 1.07, fontsize = 16)
    # fig.fig.text(0.5, 1.0, 'The figure depicts mean population levels +/- 1 standard deviation averaged over N=' + str(n_simulations) + ' simulations for two scenarios.' +
    #               '\n In the upper facet, logging can happen anywhere. In the lower facet, a block of a good half of the forest is protected from logging.' +
    #               '\n Logging is only allowed in year 5. By year 10, the canopy of all cut cells has closed again, ending the seral period.' +
    #               '\n Logging is calibrated such that the same amount of forest (' + str(round(parameter*9*100/121,1)) + '%) is cut in both the unprotected and the protected scenario.' 
    #               , wrap=True, horizontalalignment='center', fontsize=10)
    fig.set_axis_labels('Days', 'Population size')
    fig.map(plt.axvline, x = start_of_logging, color = 'black', linestyle = '--', linewidth = 1)
    fig.map(plt.axvline, x = stop_of_logging, color = 'black', linestyle = '--', linewidth = 1)
    fig.map(plt.axvline, x = stop_of_logging + end_of_seral_forest, color = 'black', linestyle = '--', linewidth = 1)
    # for ax in fig.fig.axes:
    #     ax.text(900, 600,'Logging starts', fontsize=9)
    #     ax.text(2200, 600,'Logging ends', fontsize=9)
    #     ax.text(3650, 600,'Canopy closes', fontsize=9)
    # for ax, pos in zip(fig.axes.flat, extinction_rates):
    #     ax.text(3800, 40, "Wolf extinction rate: " + str(pos) +'%', fontsize = 9,
    #             bbox=dict(boxstyle="square,pad=0.3",fc="navajowhite", ec="orange", lw=2))
    # for ax, pos in zip(fig.axes.flat, avg_pop_size_wolf):
    #     ax.text(3800, 75, "Mean wolf pop. size: " + str(pos) , fontsize = 9,
    #             bbox=dict(boxstyle="square,pad=0.3",fc="navajowhite", ec="orange", lw=2))      
    # for ax, pos in zip(fig.axes.flat, avg_hr_size_wolf):
    #     ax.text(3800, 310, "Mean wolf HR size: " + str(pos), fontsize = 9,
    #             bbox=dict(boxstyle="square,pad=0.3",fc="navajowhite", ec="orange", lw=2)) 
    # for ax, pos in zip(fig.axes.flat, avg_hr_size_deer):
    #     ax.text(3800, 345, "Mean deer HR size: " + str(pos), fontsize = 9,
    #             bbox=dict(boxstyle="square,pad=0.3",fc="lightblue", ec="steelblue", lw=2))
    # for ax, pos in zip(fig.axes.flat, avg_pop_size_deer):
    #     ax.text(3800, 380, "Mean deer pop. size: " + str(pos) , fontsize = 9,
    #             bbox=dict(boxstyle="square,pad=0.3",fc="lightblue", ec="steelblue", lw=2))  
    plt.savefig('+graphs/protection_'+str(parameter)+'_v' + str(version) + '.png', dpi= 300, bbox_inches='tight')


def graph_extinction_timing(n_simulations, version, parameter):
    
    # Function graphs a layered histogram comparing extinction timings between
    # the unprotected and the protected scenario.
    
    data = pd.read_csv('protection/v'+str(version)+'/pop_dynam_full_prot_'+str(parameter)+'_v'+str(version)+'.csv')

    extinction_data = pd.DataFrame(list(range(1,n_simulations+1)), columns= ['Simulation'])
    
    for i in ["unprotected", "protected"]:
        timing = calculate_extinction_timing(data, 'Wolves_'+i)
        extinction_data['Timing_'+i] = timing
        
    plot_data = pd.wide_to_long(extinction_data, 'Timing', 'Simulation', 'Forest', sep='_', suffix =r'\w+').reset_index()
    
    plt.figure(figsize = (8,5))
    sns.histplot(data=plot_data, x ='Timing', hue = 'Forest', hue_order = ['protected','unprotected'])
    #plt.title("Timing of wolf population extinctions")
    plt.axvline(x = stop_of_logging + end_of_seral_forest, color = 'black', linestyle = '--')
    plt.annotate('End of seral forest',(3000,80), fontsize = 9)
    plt.savefig('+graphs/extinction_timing_'+str(parameter)+'_v' + str(version) + '.png', dpi= 300, bbox_inches='tight')
    
    
#------------------------------------------------------------------------------

# EXECUTE

#graph_deer_only(n_simulations = 100, version = 1, parameter = 8)
#graph_predator_prey(n_simulations = 1000, version = 1, post_eq_time = 4000)
graph_logging_intensity(n_simulations = 1000, parameters_unprotected = list(range(0,14)), parameters_protected = list(range(1,13)) , version = 1, post_eq_time = 4000)
#graph_extinction_timing(n_simulations = 1000, version = 1, parameter = 7)
#graph_protection(n_simulations = 1000, version = 1, parameter = 7, post_eq_time = 4000)


