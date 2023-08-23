# MODEL TO SIMULATE DEER AND WOLF POPULATION DYNAMICS IN A LOGGED FOREST

# Author: Peter Kamal
# Python version: 3.9.13
# Last update: 22/07/23

# Note: The model includes additional tracking options, which are commented out. 
# They slow down the model but are helpful for checking the dynamics of individual animals if necessary.
# Multi-processing-oriented code for big sets of simulations is commented out at the bottom.

#------------------------------------------------------------------------------

# IMPORTS AND OPTIONS
import time
import numpy as np
import random as rd
import math as mt
import pandas as pd
import matplotlib.pyplot as plt
from statistics import mean

#------------------------------------------------------------------------------

# PARAMETER INITIALIZATIONS
years = 15
length_year = 360
timesteps = int(length_year*years)
beginning_of_winter = int(0.75*length_year)
month_ticks = list(range(1,beginning_of_winter+1,30))
landscape_size = 11 
no_cells_logged_per_month = 6
start_of_logging  = 5*length_year
stop_of_logging = 6*length_year
n_deers = 180
n_wolves = 10
initial_fitness_deer = 30
initial_fitness_wolf = 50
fitness_loss_deer = 1
fitness_loss_wolves = 1
old_growth_base_nutrition = 4
end_of_seral_forest = 4*length_year
new_growth_base_nutrition = 1
summer_food_factor_old_growth = 1
summer_food_factor_new_growth = 1
winter_food_factor_old_growth = 0.9
winter_food_factor_new_growth = 0.5
max_food_gain_deer = 2
gain_from_deer = 12
predation_efficiency = 0.16
hunt_refresh_time = 7
wolf_birth_threshold = 100
wolf_birth_loss = 50
deer_birth_threshold = 60
deer_birth_loss = 30


#------------------------------------------------------------------------------

# HELPER FUNCTIONS AND OBJECTS

# Landscape for first initialization
mock_landscape = np.zeros((landscape_size,landscape_size))


# Function to return a list of nxn cells around a given cell
def range_finder(matrix, position, radius):
    adj = []
    
    lower = 0 - radius
    upper = 1 + radius
    
    for dx in range(lower, upper):
        for dy in range(lower, upper):
            rangeX = range(0, matrix.shape[0])  # Identifies X bounds
            rangeY = range(0, matrix.shape[1])  # Identifies Y bounds
            
            (newX, newY) = (position[0]+dx, position[1]+dy)  # Identifies adjacent cell
            
            if (newX in rangeX) and (newY in rangeY) and (dx, dy) != (0, 0):
                adj.append((newX, newY))
    
    return adj


# Nested dictionary that contains all sets of neighbors for all possible distances up to half the landscape size
neighbor_dict = {d: {(i,j): range_finder(mock_landscape, (i,j), d)
                     for i in range(landscape_size) for j in range(landscape_size)}
                 for d in range(1,landscape_size)}




# Function for biomass growth in seral forests
def biomass_growth(forest_age):
    return np.log(forest_age + 1) + old_growth_base_nutrition


# Function that picks the cell in the home range that was visited longest ago
def cell_choice(position, home_range, memory):
    # These are all the adjacent cells to the current position
    adjacent_cells = neighbor_dict[1][position].copy()
    # This is the subset of cells of the adjacent cells belonging to homerange
    possible_choices = [i for i in adjacent_cells if i in home_range]
    # This yields the "master" indeces of those choices
    indeces = []
    for i in possible_choices:
        indeces.append(home_range.index(i))
    # This picks the index with the maximum value in the memory (ie visited longest ago)
    memory_values = [memory[i] for i in indeces]
    pick_index = indeces[memory_values.index(max(memory_values))]
    # Sets that values memory to zero
    memory[pick_index] = 0
    # Adds one period to every other index
    other_indeces = [i for i in list(range(len(memory))) if i != pick_index]
    for i in other_indeces:
        memory[i] += 1
    # Returns the picked cell
    return home_range[pick_index]


# Function to calculate average home range size per timestep
def avg_hr_size(environment, animal):
    
    sum_hr = 0
    
    if animal == 'Deer':
        for i in range(len(environment.deers)):
            sum_hr += len(environment.deers[i].home_range)
       
        if len(environment.deers) > 0:
            return sum_hr/len(environment.deers)
        else: 
            return 0
    
    if animal == 'Wolf':
        for i in range(len(environment.wolves)):
            sum_hr += len(environment.wolves[i].home_range)
        
        if len(environment.wolves) > 0:
            return sum_hr/len(environment.wolves)
        else: 
            return 0
        
        

#------------------------------------------------------------------------------

# CLASS SETUPS

class Deer:
    
    
    def __init__(self, ID):
        
        # Assigns individual ID
        self.id = ID
        
        # Initializes fitness
        self.fitness = initial_fitness_deer
        
        # Initializes a random position within the landscape 
        self.position = (rd.randint(0,landscape_size-1),rd.randint(0,landscape_size-1))
        self.original_position = self.position

        # Sets up a counter how long the deer has been in the cell
        self.time_spent_in_cell = 1
        
        # Defines a distance parameter that specifies the radius of the homerange around the base
        self.movement_radius = 1
        
        # Defines an initial home range around the position
        self.home_range = neighbor_dict[self.movement_radius][self.position].copy()
        self.home_range.append(self.position)
        
        # Sets up a list of counters how long ago cells in the home range have been visited
        self.memory = [float('inf')]*len(self.home_range)
        self.memory[self.home_range.index(self.position)] = 0

        
        # Defines a feeding counter
        self.feed_history = [0,0]
        
    
    
    def move(self, landscape, landscape_history):

        # Determines movement based on forest type
        # Case 1: Old-growth forest
        if landscape[self.position[0], self.position[1]] == 0:
            # If last two time periods already in this cell, move and reset counter, otherwise stay and increase
            if self.time_spent_in_cell > 2:
                self.position =  cell_choice(self.position, self.home_range, self.memory)
                self.time_spent_in_cell = 1
            else:
                self.time_spent_in_cell += 1
        # Case 2: New-growth forest
        else:
            # Case 2a: If in seral forest, move immediately
            if landscape_history[self.position[0], self.position[1]] < end_of_seral_forest:
                self.position =  cell_choice(self.position, self.home_range, self.memory)
                self.time_spent_in_cell = 1
            # Case 2b: Closed canopy new-growth
            elif landscape_history[self.position[0], self.position[1]] >= end_of_seral_forest:
                # If in this cell in the previous period, move, otherwise stay
                if self.time_spent_in_cell > 1:
                    self.position =  cell_choice(self.position, self.home_range, self.memory)
                    self.time_spent_in_cell = 1
                else:
                    self.time_spent_in_cell += 1
                    
                    
    
    def feed(self,landscape, landscape_nutrition, food_factor_old_growth, food_factor_new_growth):
        
        # Increases the deer's fitness depending on the forest type and update feeding history
        # Case 1: Old-growth forest
        if landscape[self.position[0], self.position[1]] == 0:
            intake = min(max_food_gain_deer, landscape_nutrition[self.position[0], self.position[1]]*food_factor_old_growth)
            self.fitness += intake
            self.feed_history[0] += intake
        # Case 2: New-growth forest
        else:
            intake = min(max_food_gain_deer, landscape_nutrition[self.position[0], self.position[1]]*food_factor_new_growth)
            self.fitness += intake
            self.feed_history[0] += intake
            
        self.feed_history[1] += 1
            


    def update_homerange(self):
        
        # If the deer is undernourished, expand home range starting from the original position and reset spatial memory
        if self.feed_history[0]/self.feed_history[1] < 1:
            if self.movement_radius < mt.floor(landscape_size/2):
                self.movement_radius += 1
                self.home_range = neighbor_dict[self.movement_radius][self.original_position].copy()
                self.home_range.append(self.original_position)
                self.memory = [float('inf')]*len(self.home_range)
                self.memory[self.home_range.index(self.position)] = 0

        

class Wolf:
    
    def __init__(self, ID):
        
        # Assigns individual ID
        self.id = ID
        
        # Initializes fitness
        self.fitness = initial_fitness_wolf
        
        # Initializes a random position within the landscape and assigns it to memory
        self.position = (rd.randint(0,landscape_size-1),rd.randint(0,landscape_size-1))
        self.original_position = self.position
        
        # Sets up a counter how long the wolf has been in the cell
        self.time_spent_in_cell = 1
        
        # Sets up a counter how long ago the last kill was
        self.time_since_recent_kill = hunt_refresh_time
        
        # Defines a distance parameter that specifies the radius of the homerange around the base
        self.movement_radius = mt.ceil(landscape_size/4)
        
        # Defines an initial home range around the position
        self.home_range = neighbor_dict[self.movement_radius][self.position].copy()
        self.home_range.append(self.position)
        
        # Sets up a list of counters how long ago cells in the home range have been visited
        self.memory = [float('inf')]*len(self.home_range)
        self.memory[self.home_range.index(self.position)] = 0
        
        # Defines a feeding counter
        self.feed_history = [0,0]

        
        
    def move(self, landscape, landscape_history):

        # Determines movement based on forest type
        # Case 1: Old-growth forest
        if landscape[self.position[0], self.position[1]] == 0:
            # If last two time periods already in this cell, move and reset counter, otherwise stay and increase
            if self.time_spent_in_cell > 2:
                self.position =  cell_choice(self.position, self.home_range, self.memory)
                self.time_spent_in_cell = 1
            else:
                self.time_spent_in_cell += 1
        # Case 2: New-growth forest
        else:
            # Case 2a: If in seral forest, move immediately
            if landscape_history[self.position[0], self.position[1]] < end_of_seral_forest:
                self.position =  cell_choice(self.position, self.home_range, self.memory)
                self.time_spent_in_cell = 1
            # Case 2b: Closed canopy new-growth
            elif landscape_history[self.position[0], self.position[1]] >= end_of_seral_forest:
                # If in this cell in the previous period, move, otherwise stay
                if self.time_spent_in_cell > 1:
                    self.position =  cell_choice(self.position, self.home_range, self.memory)
                    self.time_spent_in_cell = 1
                else:
                    self.time_spent_in_cell += 1
                    
                    
    def update_homerange(self):
        
        # If the wolf is undernourished, expand home range starting from the original position and reset spatial memory
        if self.feed_history[0]/self.feed_history[1] < 1:
            if self.movement_radius < landscape_size - 1:
                self.movement_radius += 1
                self.home_range = neighbor_dict[self.movement_radius][self.original_position].copy()
                self.home_range.append(self.original_position)
                self.memory = [float('inf')]*len(self.home_range)
                self.memory[self.home_range.index(self.position)] = 0
        
    
        

class Environment:
    
    
    def __init__(self, policy_in_effect):
        
        # Generates a square landscape with nxn cells normalized to 0 (old-growth)
        self.landscape = np.zeros((landscape_size, landscape_size))
        
        # Generates a backup landscape that keeps track of logging events
        self.landscape_history = np.full([landscape_size,landscape_size], np.nan)
        
        # Generates a backup landscape that provides nutritional information
        self.landscape_nutrition = np.full([landscape_size,landscape_size], np.nan)
        
        # Generates a backup landscape that can define a protected block in the middle of the landscape
        self.protected_zone = np.zeros((landscape_size,landscape_size))
        
        # If a policy is in place, protect the block
        if policy_in_effect:
            
            indeces_to_protect = []
            
            number_of_columns_reserved_for_protection = landscape_size - mt.ceil(no_cells_logged_per_month*9/landscape_size)
            
            for i in range(landscape_size):
                for j in range(number_of_columns_reserved_for_protection):
                    indeces_to_protect.append((i,j))
            
            for i in indeces_to_protect:
                self.protected_zone[i[0],i[1]] = 1
                
        self.loggable_cells = list(zip(*np.where(self.protected_zone == 0)))
        
        # Puts predefined number of deer in the landscape
        self.deers = [Deer(ID = i) for i in range(n_deers)]
        self.deer_counter = n_deers
        
        # Puts predefined number of wolves in the landscape
        self.wolves = [Wolf(ID = i) for i in range(n_wolves)]
        self.wolf_counter = n_wolves
        
        # Sets up data collection for population dynamics
        self.pop_dynam = pd.DataFrame([{"timestep": 0,
                                       "n_deer": n_deers,
                                       "n_wolves": n_wolves,
                                       'hr_deer': avg_hr_size(self, 'Deer'),
                                       'hr_wolves': avg_hr_size(self, 'Wolf')}])
        
        # Sets up data collection for birth and death rates and appropriate counters
        # self.birth_death = pd.DataFrame([{"timestep": 0,
        #                                   "deer_born": 0,
        #                                   "deer_died": 0,
        #                                   "wolves_born": 0,
        #                                   "wolves_died": 0}])
        
        # self.deer_birth_counter = 0
        # self.deer_death_counter = 0
        # self.wolf_birth_counter = 0
        # self.wolf_death_counter = 0
        
        
        # # Sets up tracking for deer and wolves separately
        # self.deer_tracking = pd.DataFrame([{"deerid": deer.id, 
        #                                     "timestep": 0, 
        #                                     "xpos": deer.position[0], 
        #                                     "ypos": deer.position[1],
        #                                     "fitness": deer.fitness} for deer in self.deers])
        
        # self.wolf_tracking = pd.DataFrame([{"wolfid": wolf.id, 
        #                                     "timestep": 0, 
        #                                     "xpos": wolf.position[0], 
        #                                     "ypos": wolf.position[1],
        #                                     "fitness": wolf.fitness} for wolf in self.wolves])
        
        
    def logging(self):
        
        set_of_unlogged_cells =  list(zip(*np.where(self.landscape == 0)))
        set_of_possible_cells = [i for i in set_of_unlogged_cells if i in self.loggable_cells]

        draw = rd.sample(set_of_possible_cells,no_cells_logged_per_month)
        
        for cell in draw:
            self.landscape[cell] = 1
            self.landscape_history[cell] = 0
                
    
    
    def available_food(self):
        
        # For each forest cell
        for i in range(landscape_size):
            for j in range(landscape_size):
                
                # Count the number of deer in the cell
                check = []
                
                for deer in self.deers:
                    check.append(deer.position[0] == i and deer.position[1] == j)
                    
                deer_in_cell = check.count(True)
                
                # For cells with deer presence, calculate nutrition depending on forest type
                if deer_in_cell > 0:
                    # Case 1: Old-growth forest
                    if self.landscape[i,j] == 0:
                        # Base nutrition divided by number of deer in cell
                        self.landscape_nutrition[i,j] = old_growth_base_nutrition/deer_in_cell
                    # Case 2: New-growth
                    else:
                        # Case 2a: Seral period
                        if self.landscape_history[i,j] < end_of_seral_forest:
                            # Marginally decreasing growth divided by number of deer in cell
                            self.landscape_nutrition[i,j] = biomass_growth(self.landscape_history[i,j])/deer_in_cell
                        # Case 2b: Closed canopy 
                        elif self.landscape_history[i,j] >= end_of_seral_forest:
                            # New base nutrition divided by number of deer in cell
                            self.landscape_nutrition[i,j] = new_growth_base_nutrition/deer_in_cell
    
    
    def predation(self):
        
        # Simulates predation
        for wolf in self.wolves:
            # If wolf has not killed recently:
            if wolf.time_since_recent_kill >= hunt_refresh_time:
                # Check for all deer
                for deer in self.deers:
                    # Double check for a contemporary kill
                    if wolf.time_since_recent_kill >= hunt_refresh_time:
                        # Checks for all deer whether they are in the same cell
                        if wolf.position == deer.position:
                            # Draws a random 0/1 with the kill rate as the probability
                            draw = np.random.binomial(1,predation_efficiency,1)
                            # Increases wolf's fitness, kills deer, and resets hunting counter in case of success 
                            if draw == 1:
                                wolf.fitness = wolf.fitness + gain_from_deer
                                deer.fitness = 0
                                wolf.time_since_recent_kill = -1
                                wolf.feed_history[0] += gain_from_deer
                        
            # Adds to the counters
            wolf.time_since_recent_kill += 1
            wolf.feed_history[1] += 1
            
            
    
    def reproduction(self):
        
        # Performs global reproduction for deer and wolves
        for wolf in self.wolves:
            # Create new wolf in the same position if parent fitness is high enough
            if wolf.fitness > wolf_birth_threshold:
                new_wolf = Wolf(ID = self.wolf_counter)
                self.wolf_counter += 1
                # Update standard initialization
                new_wolf.position = wolf.position
                new_wolf.original_position = new_wolf.position
                new_wolf.home_range = neighbor_dict[new_wolf.movement_radius][new_wolf.position].copy()
                new_wolf.home_range.append(new_wolf.position)
                new_wolf.memory = [float('inf')]*len(new_wolf.home_range)
                new_wolf.memory[new_wolf.home_range.index(new_wolf.position)] = 0
                # Add to list of wolves
                self.wolves.append(new_wolf)
                # Reduce fitness of parent
                wolf.fitness = wolf.fitness - wolf_birth_loss
                #self.wolf_birth_counter += 1
                
        for deer in self.deers:
            # Same for deer
            if deer.fitness > deer_birth_threshold:
                # Create new deer
                new_deer = Deer(ID = self.deer_counter)
                self.deer_counter += 1
                # Update standard initialization
                new_deer.position = deer.position
                new_deer.original_position = new_deer.position
                new_deer.home_range = neighbor_dict[new_deer.movement_radius][new_deer.position].copy()
                new_deer.home_range.append(new_deer.position)
                new_deer.memory = [float('inf')]*len(new_deer.home_range)
                new_deer.memory[new_deer.home_range.index(new_deer.position)] = 0
                # Add to list of deer
                self.deers.append(new_deer)
                deer.fitness = deer.fitness - deer_birth_loss
                #self.deer_birth_counter += 1
                
    
    
    def kill_animals(self):
        
        for j, deer in enumerate(self.deers):
            
            # Decreases fitness linearly
            deer.fitness = deer.fitness - fitness_loss_deer
            
            if deer.fitness <= 0:
                self.deers.remove(deer)
                #self.deer_death_counter += 1
                
        for j, wolf in enumerate(self.wolves):
            
            # Decreases fitness linearly
            wolf.fitness = wolf.fitness - fitness_loss_wolves
            
            if wolf.fitness <= 0:
                self.wolves.remove(wolf)
                #self.wolf_death_counter += 1
        
        
        
    def simulation(self):
        
        # Sets up a counter for determining the season
        season_counter = 0
        
        # Runs one simulation
        for timestep in range(1,timesteps+1):
            
            # Registers seasonal changes and resets once one year is over
            season_counter += 1
            if season_counter > length_year:
                season_counter = 1
            
            # Registers changes to the forest
            # Adds one time period for all new-growth cells (old-growth are NaNs, adding does nothing)
            self.landscape_history += 1
            
            # If under the cap, within in the logging window and not in winter, register possible logging.
            if timestep >= start_of_logging and timestep < stop_of_logging:
                if season_counter in month_ticks:
                    self.logging()
                
            # Moves the animals
            for deer in self.deers:
                deer.move(self.landscape, self.landscape_history)
            
            for wolf in self.wolves:
                wolf.move(self.landscape, self.landscape_history) 
                
            # Calculates available nutrition for deer:
            self.available_food()
            
            for deer in self.deers:
                # Feeds the deer depending on season
                if season_counter < beginning_of_winter:
                    deer.feed(self.landscape, self.landscape_nutrition, summer_food_factor_old_growth,summer_food_factor_new_growth)
                else:
                    deer.feed(self.landscape, self.landscape_nutrition, winter_food_factor_old_growth,winter_food_factor_new_growth)
                
                # Checks for home range expansions and resets food counter every year    
                if season_counter == length_year:
                    deer.update_homerange()
                    deer.feed_history = [0,0]
                
            
            # Registers global predation
            self.predation()
            
            # Updates home ranges for wolves (after predation)
            for wolf in self.wolves:
                if season_counter == length_year:
                    wolf.update_homerange()
                    wolf.feed_history = [0,0]
        
            
            # Registers global reproduction
            self.reproduction()
                
            # Eliminates dead animals   
            self.kill_animals()
                
            # Updates tracking tables
            self.pop_dynam = pd.concat([self.pop_dynam,
                                       pd.DataFrame([{"timestep": timestep,
                                                     "n_deer": len(self.deers),
                                                     "n_wolves": len(self.wolves),
                                                     'hr_deer': avg_hr_size(self, 'Deer'),
                                                     'hr_wolves': avg_hr_size(self, 'Wolf')}])])
            
            # self.birth_death = pd.concat([self.birth_death,
            #                               pd.DataFrame([{"timestep": timestep,
            #                                              "deer_born": self.deer_birth_counter,
            #                                              "deer_died": self.deer_death_counter,
            #                                              "wolves_born": self.wolf_birth_counter,
            #                                              "wolves_died": self.wolf_death_counter}])])
            
            # # Reset counters
            # self.deer_birth_counter = 0
            # self.deer_death_counter = 0
            # self.wolf_birth_counter = 0
            # self.wolf_death_counter = 0
            
            
            # self.deer_tracking = pd.concat([self.deer_tracking,
            #                           pd.DataFrame([{"deerid": deer.id,
            #                                          "timestep": timestep,
            #                                          "xpos": deer.position[0],
            #                                          "ypos": deer.position[1],
            #                                          "fitness": deer.fitness} for deer in self.deers])])
            
            # self.wolf_tracking = pd.concat([self.wolf_tracking,
            #                           pd.DataFrame([{"wolfid": wolf.id,
            #                                           "timestep": timestep,
            #                                           "xpos": wolf.position[0],
            #                                           "ypos": wolf.position[1],
            #                                           "fitness": wolf.fitness} for wolf in self.wolves])])
            

#------------------------------------------------------------------------------

# ONE SIMULATION (for a quick glance)

# Simulate

start_time = time.time()
environment = Environment(policy_in_effect = True)
environment.simulation()
print("--- %s seconds ---" % (time.time() - start_time))

# Plot Population dynamics
plt.figure(figsize = (12,8))
plt.plot(environment.pop_dynam.timestep,environment.pop_dynam.n_deer)
plt.plot(environment.pop_dynam.timestep,environment.pop_dynam.n_wolves)
plt.xlabel("Days")
plt.ylabel("Population size")
plt.title("Population dynamics")
plt.legend(["Deer", "Wolves"])
plt.axvline(x = start_of_logging, color = 'black')
plt.axvline(x = stop_of_logging, color = 'black')
plt.axvline(x = stop_of_logging + end_of_seral_forest, color = 'black')
    
#------------------------------------------------------------------------------

# MULTIPROCESSING OUTPUT - DEER ONLY

# PARAMETER CHANGES

# no_cells_logged_per_month = 8
# n_wolves = 0

# import multiprocess

# version = str(1)
# n_simulations = 102 # must be divisible by 3

# set_of_ranges = [1] 

# for i in range(1,multiprocess.cpu_count()-1):
#     set_of_ranges.append(i*(int(n_simulations/(multiprocess.cpu_count()-1))) + 1)

# def deer_only_simulations(start):
    
#     for i in range(start,start + int(n_simulations/(multiprocess.cpu_count()-1))):
#         environment = Environment(policy_in_effect = False)
#         environment.simulation()
#         environment.pop_dynam.to_csv('output/deer_only/v'+version+'/pop_dynam_'+str(i)+'.csv', index = False)
        
  
# start_time = time.time() 

# if __name__ == '__main__':
#     with multiprocess.Pool() as p:
#         p.map(deer_only_simulations, set_of_ranges)


# print('Program finished in ', time.time() - start_time, 'seconds.' )



#-----------------------------------------------------------------------------

# MULTI PROCESSING OUTPUT - LOGGING INTENSITY AND POLICIES

# PARAMETER CHANGES
# no_cells_logged_per_month = 1 #vary between 0 and 13

# import multiprocess

# version = str(1)
# n_simulations = 1002 # must be divisible by 3

# set_of_ranges = [1] 

# for i in range(1,multiprocess.cpu_count()-1):
#     set_of_ranges.append(i*(int(n_simulations/(multiprocess.cpu_count()-1))) + 1)
    
# def simulations_logging_intensity(start):

#     for i in range(start,start + int(n_simulations/(multiprocess.cpu_count()-1))):
  
#        environment = Environment(policy_in_effect = False)
#       environment.simulation()
#        environment.pop_dynam.to_csv('output/logging_intensity/v'+version+'/'+str(no_cells_logged_per_month)+'/pop_dynam_'+str(i)+'.csv', index = False)
        
        # uncomment for the protection scenarios
        # environment = Environment(policy_in_effect = True)
        # environment.simulation()
        # environment.pop_dynam.to_csv('output/protection/v'+version+'/'+str(no_cells_logged_per_month) +'/pop_dynam_'+str(i)+'.csv', index = False)
                    

# start_time = time.time() 

# if __name__ == '__main__':
#    with multiprocess.Pool() as p:
#        p.map(simulations_logging_intensity, set_of_ranges)

# print('Program finished in ', time.time() - start_time, 'seconds.' )

