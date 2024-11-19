#combine output
import pandas as pd
import glob

paths = glob.glob("./Output_data_files/results_team_*.csv")

def readpaths(path_names):
    '''Reads a list of jsons and appends to a single dataframe'''
    data_list = []

    for file_name in path_names: 
        ## In hamming:
        #team_number = file_name.replace("./Output_data_files/results_team_","")
        ## In windows:
        team_number = file_name.replace("./Output_data_files\\results_team_","")
        team_number = team_number.replace(".csv","")
        team_number = int(team_number)
        #read output for each file
        df = pd.read_csv(file_name)
        df['Unnamed: 0'] = team_number
        data_list.append(df)
        #turn output to dataframe and add to list
        #data_list.append(pd.DataFrame([outputs]))
    
    #combine all dataframes and return
    combined_df = pd.concat(data_list,ignore_index=True)
    combined_df.rename(columns={'Unnamed: 0': 'team_num'},inplace=True)
    return combined_df

combined_df = readpaths(paths)
nteams = len(combined_df)
filename = f"./Output_data_files/Team_Summary_{nteams}.csv"

combined_df.to_csv(filename)