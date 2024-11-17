#Run a pokemon file
import numpy as np
import pandas as pd
import pokemon_module as pk
import openpyxl
from openpyxl import Workbook
import sys


#Arguments: poke_index and team members
if len(sys.argv) >=2:
    poke_index = int(sys.argv[1])
    player_team = []
    for i in range(2,len(sys.argv)):
        player_team.append(sys.argv[i])
    
    #fight_index = int(sys.argv[2])
else:
    #Not enough inputs
    player_team = ['gyarados','zapdos','moltres','articuno','mew','mewtwo']
    poke_index = 1
    #fight_index = 1

###Things to index: 
#1: which team we're on
#2: which battle we're on (changes per job index)

# function to write multiple results to excel
def write_results_append(columns,results,sheet_name,file_name):
    #open workbook or create it if it doesn't exist
    try:
        wb = openpyxl.load_workbook(file_name)
    except FileNotFoundError:
        wb = Workbook()
    #use worksheet or create if it doesn't exist
    if sheet_name in wb.sheetnames:
        ws= wb[sheet_name]
    else:
        ws= wb.create_sheet(sheet_name)
        # Write the headers to the first row
        ws.append(columns)
    
    #append to filename
    string_list = [str(element) for element in results]
    ws.append(string_list)
    wb.save(file_name)
    return


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

#headers
columns = ['Result','Time','Winner','Winner List']

#run battle
results = pk.run_elite(playerteam,elite,verbose=False)

#define names for excel file
sheet_name = f"team{poke_index}"
file_name = "Output_data_files/elite_results_test.xlsx"

#add results to sheet
write_results_append(columns,results,sheet_name,file_name)
