#run pokemon script

#import libraries
import sys
import pandas as pd
import os

#number fights
if len(sys.argv) >=2 :
    #run index number
    fight_index = int(sys.argv[1])
else:
    #Not enough inputs
    fight_index = 1

#get teams from csv
teams = pd.read_csv("Input_data_files/random_teams.csv",header=None)
teamnumbers = len(teams)

#feed teams to pokemon script (runs battlse and writes results to elite_resutls_test.xlsx)
for i in range(teamnumbers):
    
    command = f"python pokemon_script.py {i+1} {fight_index}"
    for value in teams.loc[i].values:
        command = command + " " + value
    
    os.system(command)