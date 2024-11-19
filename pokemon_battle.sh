#!/bin/sh

#SBATCH --job-name HEB_pokemonbattle
#SBATCH --array=1-4
#SBATCH --output=Output_data_files/out_battle_%a.txt

. /etc/profile
module load lang/python
## load the comp3 virtual environment
source /smallwork/$USER/comp3/bin/activate

## arguments:  team number, number of runs
python pokemon_script.py ${SLURM_ARRAY_TASK_ID} 10
