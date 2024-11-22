#!/bin/sh

#SBATCH --job-name create_random_csv
#SBATCH --array=0-99
#SBATCH --output=Output_data_files/out_input.txt

. /etc/profile
module load lang/python
## load the comp3 virtual environment
source /smallwork/$USER/comp3/bin/activate

## arguments:  team number, number of runs
python create_teams.py ${SLURM_ARRAY_TASK_ID}
