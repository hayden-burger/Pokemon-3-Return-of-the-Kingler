# Pokémon 3 Return of the Kingler

Our team meets yet again, but this time with an even larger scope for our project. Our goal: Using HPC at NPS, what 6-Pokémon team can most efficiently beat the Elite Four?

## About This Repository

### Contributors

- Hayden Burger
- Corinne Desroches
- David Lee

Special thanks to our course instructors and peers at NPS for their support and guidance throughout this project.

### Input Data Files

- **`moves.csv`**: Details the moves available to each Pokémon and their effects.
- **`pokemon.csv`**: Contains the stats for each Pokémon.
- **`random_teams.csv`**: Lists 10,000 randomly generated teams of 6 Pokémon.

### Output Data Files

- **`elite_results.csv`**: Details the results from the 11 chosen teams battling the Elite Four.
- **`Level_1_1000runs.csv`**: These were the results from the first project of battling all level 1 Pokemon 1000 times.
- **`Level_50_1000runs.csv`**: These were the results from battling all level 50 Pokemon 1000 times.
- **`Random_Team_Summary.csv`**: Details the results from randomly generated teams battling the Elite Four.

### Presentation and Paper

Contains the presentationa and paper submitted for our final project.

### Scripts for HPC

- **`combine_ouput.py`**:
- **`combine_output.sh`**:
- **`create_input.sh`**:
- **`create_teams.py`**:
- **`pokemon_battle.sh`**:
- **`pokemon_script.py`**:
- **`run_script.py`**:

### Python Files

- **`Pk_Data_Retrieve.py`**: Contains the functions to pull data from the PokeAPI and create the CSV files: `moves.csv` and `pokemon.csv`.
- **`Pokemon_module.py`**: Contains the Pokémon class, and the battle functions.
- **`Vis.py`**: Contains the script to visualize the results in a Streamlit App.
- **`Requirements.txt`**: Lists the packages needed for the Streamlit app.
- **`testpokemon.ipynb`**: Jupyter Notebook used to explore our project. Also contains functions and code to build visuals.

### Project Overview

Our project applies Python programming and data visualization skills to simulate and analyze battles between teams of 6 pokemon vs the generation one Elite Four. This required:

- Accessing Pokémon data from the PokeAPI and creating CSV files for moves and stats.
- Developing a Python class to represent Pokémon, including attributes for stats and moves.
- Implementing battle logic with methods for selecting moves, applying effects, and calculating damage.
- Simulating battles utilizing HPC resources at NPS.
- Visualizing results with Plotly and Streamlit.

### Getting Started

1. **Clone this repository**: Get a local copy for exploration and experimentation.
2. **Explore the directories**: Each contains unique aspects of the project, with detailed `README.md` files.
3. **Run the Jupyter notebook and Streamlit app**: Dive into the code and visualizations.

### Prerequisites

- Python 3.x installed.
- Familiarity with Python programming.
- Optionally, an IDE like PyCharm or VS Code for a better development experience.

### Contributing

Contributions, suggestions, and feedback are welcome! Feel free to fork the repository, create a feature branch, and submit pull requests with improvements or new content.

### Contact

Questions or discussions? Reach out via our NPS email addresses.

### Acknowledgements

Our heartfelt thanks to the NPS faculty and our classmates for their invaluable input and encouragement throughout this project.
