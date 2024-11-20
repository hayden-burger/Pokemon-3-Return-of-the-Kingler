#Run a pokemon file
import numpy as np
import pandas as pd
import pokemon_module as pk
import sys
import math


#Arguments: poke_index, n_fights
if len(sys.argv) >=2:
    poke_index = int(sys.argv[1])
    n_fights = int(sys.argv[2])
else:
    #Not enough inputs
    poke_index = 1
    n_fights = 1

team_index = math.floor((poke_index-1)/10000)
infilename = "Input_data_files/random_teams_{team_index}.csv"
teams = pd.read_csv(infilename,header=None)
csv_loc = (poke_index%10000)-1
player_team = teams.loc[csv_loc].to_list()

###Things to index: 
#1: which team we're on
#2: which battle we're on (changes per job index)


#function to run num_runs battles and save results to dataframe
def sim_elite(team,elite,num_runs=10):
    results = pd.DataFrame(columns=['Result','Time','Winner','Winner List'])
    for i in range(num_runs):
        result,time,teamname,winnerlist = pk.run_elite(team,elite,verbose=False,roundreset=False)
        results.loc[i] = [result,time,teamname,winnerlist]
    return results

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
team_names = joined_string = ', '.join(player_team)


#run battle
results = sim_elite(playerteam,elite,num_runs=n_fights)

#collect battle info
collectedresults_df = pd.DataFrame()
nemesis_dict = {}
team_results = results
wins = team_results['Result'].sum()
#calculate average time if win = 1
avg_time_win = round(team_results[team_results['Result'] == 1]['Time'].mean(),2)
sd_time_win = round(team_results[team_results['Result'] == 1]['Time'].std(),2)
#calculate efficiency
efficiency = wins/avg_time_win
#calculate average time if win = 0
avg_time_loss = round(team_results[team_results['Result'] == 0]['Time'].mean(),2)
sd_time_loss = round(team_results[team_results['Result'] == 0]['Time'].std(),2)
#record distribution of winners
winner_dict = team_results['Winner'].value_counts().to_dict()
#record distribution of nemesis
for run in team_results.index:
    #who beat them last
    nem = team_results.iloc[np.where(team_results.index == run)]['Winner List'].values[0]
    nemesis = nem[-1]
    if nemesis in nemesis_dict:
        nemesis_dict[nemesis] += 1
    else:
        nemesis_dict[nemesis] = 1
#update dataframe
collectedresults_df = pd.concat([collectedresults_df,pd.DataFrame({'Team':team_names,'Efficiency: (Wins/avg_Time)':efficiency,'Wins':wins,'Avg Time Win':avg_time_win,'SD Time Win':sd_time_win,
                                                                                'Avg Time Loss':avg_time_loss,'SD Time Loss':sd_time_loss,
                                                                                'Losses to Lorelei':winner_dict.get('Lorelei',0), 'Losses to Bruno':winner_dict.get('Bruno',0),
                                                                                'Losses to Agatha':winner_dict.get('Agatha',0), 'Losses to Lance':winner_dict.get('Lance',0),
                                                                                'Nemesis':max(nemesis_dict, key=nemesis_dict.get), 'Nemesis Losses':nemesis_dict[max(nemesis_dict, key=nemesis_dict.get)]},index=[0])])



#save results to csv
file_name = f"./Output_data_files/results_team_{poke_index}.csv"
collectedresults_df.to_csv(file_name)
