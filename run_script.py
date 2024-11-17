#run pokemon script

import sys
import pandas as pd
import os
import json

if len(sys.argv) >=2 :
    #run index number
    nfights = int(sys.argv[1])
else:
    #Not enough inputs
    nfights = 1

teams = pd.read_csv("random_teams.csv",header=None)
teamnumbers = len(teams)

for i in range(teamnumbers):
    team_list = teams.loc[1].to_list()
    list_as_string = json.dumps(team_list)
    command = f"python pokemon_script.py {list_as_string}"
    os.system(command)