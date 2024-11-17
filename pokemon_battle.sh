#!/bin/sh

#SBATCH --job-name HEB_pokemonbattle
#SBATCH --array=1-3
#SBATCH --output=Output_data_files/out_battle_%a.txt

. /etc/profile
module load lang/python
## load the comp3 virtual environment
source /smallwork/$USER/comp3/bin/activate

python -m pip install --quiet openpyxl
python run_script.py ${SLURM_ARRAY_TASK_ID} 
