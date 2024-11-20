#Create random_teams.csv

import sys
import numpy as np
import csv
import pokemon_module as pk


#number fights
if len(sys.argv) >=2 :
    #run index number
    csv_index = int(sys.argv[1])
else:
    #Not enough inputs
    csv_index = 0

def random_team_names(n):
    '''Does same as random_team but just names instead of pokemon'''
    team = []
    for i in range(n):
        pokemon_name = np.random.choice(list(pokemon_dict.keys()))
        team.append(pokemon_name)
    return team

def save_teams(n,filename):
    '''writes n random teams to csv file'''
    with open(filename,'w',newline='') as file:
        writer = csv.writer(file)
        for i in range(n):
            team = random_team_names(6) 
            writer.writerow(team)
    return 

pokemon_dict = pk.create_pokemon_dict()

filename = f'Input_data_files/random_teams_{csv_index}.csv'
            
np.random.seed(csv_index)
save_teams(10000,filename)