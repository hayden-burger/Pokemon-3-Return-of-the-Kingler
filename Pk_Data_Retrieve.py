#Hayden Burger, Corinne Desroches, David Lee
#OA 3302 Simulation Modeling
#November 2024
#Pokemon Data Retrieval script

#import statements
import numpy as np
import pandas as pd
import requests

#---------------------------------------------------------------------------------
#Pull Data 
###################################
#Pokemon_df:

base_url = 'https://pokeapi.co/api/v2/generation/1'
response = requests.get(base_url)
gen1_data = response.json()

gen_1_pokemon = []
for i in gen1_data['pokemon_species']:
    gen_1_pokemon.append(i['name'])

against_columns = [
    'against_bug', 'against_dark', 'against_dragon', 'against_electric', 'against_fairy',
    'against_fight', 'against_fire', 'against_flying', 'against_ghost', 'against_grass',
    'against_ground', 'against_ice', 'against_normal', 'against_poison', 'against_psychic',
    'against_rock', 'against_steel', 'against_water'
]

# Fetch Pokemon data
pk = []
for i in gen_1_pokemon:
    url = f'https://pokeapi.co/api/v2/pokemon/{i}'
    pk_data = requests.get(url).json()
    
    pokemon_info = {
        'name': pk_data['name'],
        'pokedex_number': pk_data['id'],
        'generation': 1 if pk_data['id'] <= 151 else 'N/A',
        'type1': pk_data['types'][0]['type']['name'],
        'type2': pk_data['types'][1]['type']['name'] if len(pk_data['types']) > 1 else 'N/A',
        'height_(m)': pk_data['height'] / 10,
        'weight_(kg)': pk_data['weight'] / 10,
        'base_total': sum(stat['base_stat'] for stat in pk_data['stats']),
        'hp': pk_data['stats'][0]['base_stat'],
        'attack': pk_data['stats'][1]['base_stat'],
        'defense': pk_data['stats'][2]['base_stat'],
        'sp_attack': pk_data['stats'][3]['base_stat'],
        'sp_defense': pk_data['stats'][4]['base_stat'],
        'speed': pk_data['stats'][5]['base_stat'],
        'image_url': pk_data['sprites']['other']['official-artwork']['front_default']
    }
    
    for col in against_columns:
        pokemon_info[col] = 1.0
    
    pk.append(pokemon_info)

# Create DataFrame
Pokemon_df = pd.DataFrame(pk)
Pokemon_df.set_index('name', inplace=True)
Pokemon_df.sort_values(by='pokedex_number', inplace=True)

# Get unique types from Pokemon_df.type1 and Pokemon_df.type2
unique_types = np.unique(np.append(Pokemon_df['type1'].unique(), Pokemon_df['type2'].unique()))
unique_types = unique_types[unique_types != 'N/A']

# Fetch type modifiers data
modifiers_data_dict = {type: requests.get(f'https://pokeapi.co/api/v2/type/{type}').json() for type in unique_types}

# Update against columns based on type modifiers
for pokemon in Pokemon_df.index:
    type1 = Pokemon_df.loc[pokemon, 'type1']
    type2 = Pokemon_df.loc[pokemon, 'type2']
    
    for type in [type1, type2]:
        if type == 'N/A':
            continue
        modifiers_data = modifiers_data_dict[type]
        for col in against_columns:
            against_type = col.split('_')[1]
            if any(t['name'] == against_type for t in modifiers_data['damage_relations']['double_damage_to']):
                Pokemon_df.loc[pokemon, col] *= 2.0
            if any(t['name'] == against_type for t in modifiers_data['damage_relations']['half_damage_to']):
                Pokemon_df.loc[pokemon, col] *= 0.5

#---------------------------------------------------------------------------------
# Merge Moves Data

def poke_moves(pokemon_name='bulbasaur'):
    def get_value(data, key, default):
        return data.get(key, default) if data.get(key) is not None else default

    base_url = 'https://pokeapi.co/api/v2/pokemon'
    url = f'{base_url}/{pokemon_name}'
    response = requests.get(url)
    data = response.json()
    # add struggle move
    data['moves'].append({'move': {'name': 'struggle'}, 'version_group_details': [{'level_learned_at': 1, 'version_group': {'name': 'red-blue'}, 'move_learn_method': {'name': 'level-up'}}]})

    pk_moves = []
    gen_map = {
        'generation-i': 1, 'generation-ii': 2, 'generation-iii': 3,
        'generation-iv': 4, 'generation-v': 5
    }

    for move in data['moves']:
        version_details = move['version_group_details'][0]
        if version_details['move_learn_method']['name'] == 'level-up' and version_details['version_group']['name'] == 'red-blue':
            move_url = f'https://pokeapi.co/api/v2/move/{move["move"]["name"]}'
            move_data = requests.get(move_url).json()
            
            # Extract main move details with fallbacks
            acc = get_value(move_data, 'accuracy', '_')
            power = get_value(move_data, 'power', 0)
            pp = get_value(move_data, 'pp', 0)
            type_ = move_data['type']['name']
            effect = get_value(move_data['effect_entries'][0], 'short_effect', 'N/A')
            prob = get_value(move_data, 'effect_chance', 100)
            category = move_data['damage_class']['name']
            gen = gen_map.get(move_data['generation']['name'], 'N/A')
            stat_change = move_data['stat_changes'][0]['stat']['name'].replace("special-","sp_") if move_data['stat_changes'] else 'N/A'
            amount_change = move_data['stat_changes'][0]['change'] if move_data['stat_changes'] else 0

            # Update with past values if available
            if move_data['past_values']:
                past_values = move_data['past_values'][0]
                acc = get_value(past_values, 'accuracy', acc)
                power = get_value(past_values, 'power', power)
                pp = get_value(past_values, 'pp', pp)
                type_ = get_value(past_values, 'type', {}).get('name', type_)
                prob = get_value(past_values, 'effect_chance', prob)
                if past_values['effect_entries']:
                    effect = get_value(past_values['effect_entries'][0], 'short_effect', effect)
            
            # Append the processed move details
            pk_moves.append({
                'name': pokemon_name,
                'level': version_details['level_learned_at'],
                'move': move['move']['name'],
                'type': type_,
                'power': power,
                'accuracy': acc,
                'pp': pp,
                'category': category,
                'effect': effect,
                'effect_prob': prob,
                'gen': gen,
                'stat_change': stat_change,
                'amount_changed': amount_change
            })

    pk_moves_df = pd.DataFrame(pk_moves).sort_values('level')
    return pk_moves_df

merged_moves_df = pd.DataFrame()
for pokemon in gen_1_pokemon:
    temp = poke_moves(pokemon)
    merged_moves_df = pd.concat([merged_moves_df, temp], ignore_index=True)
#---------------------------------------------------------------------------------

if __name__ == '__main__':
    print(Pokemon_df.head())
    print(merged_moves_df.head())
    # save data to csv
    Pokemon_df.to_csv('Input_data_files/pokemon.csv')
    merged_moves_df.to_csv('Input_data_files/moves.csv', index=False)