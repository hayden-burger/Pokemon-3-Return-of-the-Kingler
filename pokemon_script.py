#Run a pokemon file
import numpy as np
import pandas as pd
import pokemon_module as pk
import csv


#Initial Conditions should be fed into python script
if len(sys.argv) >=3 :
    #run index number
    poke_index = int(sys.argv[1])
    fight_index = int(sys.argv[2])
else:
    #Not enough inputs
    poke_index = 1
    fight_index = 1

###Things to index: 
#1: which team we're on
#2: which battle we're on (changes per job index)

#read team from csv
import csv
with open('random_teams.csv', mode='r') as f:
  reader = csv.reader(f)
  #playerteam = reader(poke_index)
  for current_line_number, row in enumerate(reader, start=1):
        if current_line_number == poke_index:
            player_team = row
            break

#elite four teams
elite4_1 = ['dewgong','cloyster','slowbro','jynx','lapras']
elite4_2 = ['onix','hitmonlee','hitmonchan','onix','machamp']
elite4_3 = ['gengar','golbat','haunter','arbok','gengar']
elite4_4 = ['gyarados','dragonair','dragonair','aerodactyl','dragonite']
elite_list = [elite4_1,elite4_2,elite4_3,elite4_4]

#create pokemon objects
elite = []
for team in elite_list:
    elite.append(pk.create_pokemon_objects(team))

#player team
playerteam = pk.create_pokemon_objects(player_team)

result,time,teamname,winnerlist = pk.run_elite(playerteam,elite,verbose=False)

