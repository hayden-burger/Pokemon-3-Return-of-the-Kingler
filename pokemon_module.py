#Hayden Burger, Corinne Desroches, David Lee
#OA 3302 Simulation Modeling
#November 2024
#Pokemon module

#import statements
import numpy as np
import pandas as pd
import random
import copy



#---------------------------------------------------------------------------------
#Pull Data 
###################################
#Pokemon_df:
Pokemon_df_level1 = pd.read_csv('Input_data_files/pokemon.csv', index_col = 'name', keep_default_na=False)
lvl = 1

#---------------------------------------------------------------------------------
# Merge Moves Data
merged_moves_df = pd.read_csv('Input_data_files/moves.csv', keep_default_na=False)

#---------------------------------------------------------------------------------

def levelup(Pokemon_dataframe, level):
    '''Function to level up all Pokemon to a specified level'''
    # edit stats for level
    temp_df = Pokemon_dataframe.copy()
    stats = ['hp', 'speed', 'attack', 'sp_attack', 'defense', 'sp_defense']
    for pokemon in temp_df.index:
        temp_df.loc[pokemon, 'level'] = level
        for stat in stats:
            if stat == 'hp':
                temp_df.loc[pokemon, stat] = int(((temp_df.loc[pokemon, stat] * 2) * level / 100) + level + 10)
            else:
                temp_df.loc[pokemon, stat] = int(((temp_df.loc[pokemon, stat] * 2) * level / 100) + 5)
        temp_df.loc[pokemon, 'base_total'] = temp_df.loc[pokemon, stats].sum()
    return temp_df
Pokemon_df = levelup(Pokemon_df_level1,lvl)

#--------------------------------------------------------------------------------
def verboseprint(printstatement,verbose):
    '''Prints a statement only if boolean argument is true'''
    if verbose:
        print(printstatement)


#-------------------------------------------------------------------------------
##Pokemon Class:
class Pokemon:
    '''A Class that contains traits for a single pokemon'''

    def __init__(self,name,Pokemon_df):
        '''Initialize an individual pokemon by name'''
        self.name = name
        #grabs a row from Pokemon_df to reference
        self.individual_df = Pokemon_df.loc[name]
        self.level = Pokemon_df.loc[name,'level']

        #Base stats
        self.start_speed = self.individual_df['speed']
        self.start_attack = self.individual_df['attack']
        self.start_defense = self.individual_df['defense']
        self.start_sp_attack = self.individual_df['sp_attack']
        self.start_sp_defense = self.individual_df['sp_defense']
        self.start_hp = self.individual_df['hp']

        #Base types:
        type1 = self.individual_df['type1']
        type2 = self.individual_df['type2']
        self.start_types = {1:type1} #dictionary of types
        #Includes a second type in dictionary only if it's not 0 (null)
        if type2 != 0:
            self.start_types[2] = type2

        #Damage Multiplier
        #NOTE! this is a multiplier for the damage TAKEN, not dealt
        #Grab all columns of 'against_blank' format and remove 'against_'
        against = self.individual_df.index.str.contains('against_')
        type_advantages_df = self.individual_df[against]
        type_advantages_df.index = type_advantages_df.index.str.replace('against_','')
        #replace 'fight' with 'fighting' to match the pokemon/move type
        type_advantages_df['fighting']=type_advantages_df.pop('fight')
        #create a dictionary of damage multipliers by the type of move
        self.start_damage_multiplier = type_advantages_df.to_dict()

        #Available Moveset
        pokemon = np.where(merged_moves_df['name'] == name) #selects pokemon's moves
        # define the moveset for the pokemon for corresponding level
        pokemon_moves = merged_moves_df.iloc[pokemon]
        pokemon_moves = pokemon_moves[pokemon_moves['level'] <= self.level]                                 
        pokemon_moves.set_index('move',inplace = True) #sets the moves as the index
        self.start_moveset = {} #dictionary of available moves
        for move in pokemon_moves.index:
        #Each move has a dictionary of type, power, accuracy, pp, effect, and effect prob
            self.start_moveset[move] = {'type':pokemon_moves.loc[move]['type'],\
                             'power':pokemon_moves.loc[move]['power'],\
                             'accuracy':pokemon_moves.loc[move]['accuracy'],\
                             'pp':pokemon_moves.loc[move]['pp'],\
                             'category':pokemon_moves.loc[move]['category'],\
                             'effect':pokemon_moves.loc[move]['effect'],\
                             'effect_prob': pokemon_moves.loc[move]['effect_prob']/100,\
                             'stat_change':pokemon_moves.loc[move]['stat_change'],\
                             'amount_changed':pokemon_moves.loc[move]['amount_changed']}

        #statuses have stages between -6 to 6 and each corresponds with a multiplier
        #eg if attack is in stage -6, all damage will be multiplied by .25
        self.statmods_multipliers={-6:0.25,-5:0.38,-4:0.33,-3:0.4,-2:0.5,-1:0.66,0:1,\
                                   1:1.5,2:2,3:2.5,4:3,5:3.5,6:4}
        #Set all changing values to their start values:
        self.reset()

    def take_damage(self,other,chosen_move, working_move, verbose = False):
        '''A function for a pokemon to take damage from a move. 
        Calls other pokemon and the move. Returns the damage'''
        level = other.level
        #Calculates threshold for a critical hit:
        if other.focus_energy:
            if working_move['effect'] == "Increases the user's chance to score a critical hit.":
                T = 4*(other.start_speed//4)
            else:
                T = other.start_speed//8
        else:
            if working_move['effect'] == "Increases the user's chance to score a critical hit.":
                T = 8*(other.start_speed//2)
            else:
                T = other.start_speed//2
        if T > 255: #threshold cannot exceed 255
            T = 255
        if random.randint(1,256) < T: #If hit is critical, set damage multiplier
            critical = (2*level+5)/(level+5)
            verboseprint("  Critical Hit!",verbose)
        else:
            critical = 1

        if working_move['category'] == 'special':#for special move, use sp attack/defense
            A = other.sp_attack*self.statmods_multipliers[self.statmods['sp_attack']]
            D = self.sp_defense*self.statmods_multipliers[self.statmods['sp_defense']]
        elif working_move['category'] == 'physical':#for physical move, use attack/defense
            A = other.attack*self.statmods_multipliers[self.statmods['attack']]
            if other.effects_nv['burn']:
                A = A/2
            D = self.defense*self.statmods_multipliers[self.statmods['defense']]
        #if the move type matches the attacker's type: Same Type Attack Bonus
        if working_move['type'] in other.types.values(): 
            STAB = 1.5 
        else:
            STAB = 1
        power = working_move['power']

        multiplier = self.damage_multiplier[working_move['type']] #type disadvantage
        Random = random.randint(217,255)/255

        Damage = round((((((2*level*critical/5)+2)*power*A/D)/50)+2)*STAB*multiplier*Random,2)
        verboseprint("  %s hit for %.1f damage!" % (chosen_move, Damage),verbose)
        self.hp = self.hp - Damage
        return Damage

    def confusion_damage(self,verbose = False):
        level =  self.level
        critical = 1
        power = 40
        STAB = 1
        A = self.attack*self.statmods_multipliers[self.statmods['attack']]
        D = self.defense*self.statmods_multipliers[self.statmods['defense']]
        if self.effects_nv['burn']:
                A = A/2
        Random = random.randint(217,255)/255
        multiplier = 1
        Damage = round((((((2*level*critical/5)+2)*power*A/D)/50)+2)*STAB*multiplier*Random,2)
        self.hp -= Damage
        verboseprint("  %s hit itself in its confusion! %.1f damage! %.1f hp remaining." % \
                     (self.name, Damage, self.hp),verbose)
        

    def choose_move(self,other,verbose=False):
        '''Randomly choses a move from pokemon's available moveset.
        If pokemon doesn't have status effects preventing them to use move, apply use move.
        Apply poison or burn damage after'''
                
        #Status effects that prevent moving:
        #Cannot move if asleep. Counts down to recover from sleep effects
        if self.effects_nv['sleep']:
            asleep = True
            self.effect_counter['sleep'] -=1
            if self.effect_counter['sleep'] == 0:
                self.effects_nv['sleep'] = False
        else:
            asleep = False

        #Cannot move if flinched (Lasts one move)
        if self.effects_v['flinch']:
            flinched = True
            self.effect_counter['flinch'] =0
            self.effects_v['flinch'] = False
        else:
            flinched = False

        #Paralysis has a 25 percent chance of making a pokemon unable to move
        if self.effects_nv['paralysis']:
            if random.random() < .25:
                fully_paralyzed = True
                self.frenzy = False
                self.effect_counter['frenzy'] = 0
                self.frenzy_move = False
            else: fully_paralyzed = False
        else:
            fully_paralyzed = False

        #Cannot move if frozen
        if self.effects_nv['freeze']:
            frozen = True
        else:
            frozen = False

        #cant_move boolean variable is True for any status effect that prevents moving
        cant_move = fully_paralyzed or asleep or frozen or flinched

        #Inflict confusion:
        if self.effects_v['confusion'] and not cant_move:
            if random.random() < .5:
                confused = True
                self.confusion_damage(verbose)
                self.frenzy = False
                self.effect_counter['frenzy'] = 0
                self.frenzy_move = False
                self.underground = False
                self.dig_move = False
            else:
                confused = False
            self.effect_counter['confusion'] -= 1
            if self.effect_counter['confusion'] == 0:
                self.effects_v['confusion'] = False
        else: confused = False

        #Effect of Petal Dance or thrash:
        if self.frenzy == True:
            if not cant_move:
                self.effect_counter['frenzy'] -= 1
            if self.effect_counter['frenzy'] <= 0:
                self.frenzy_move = False
                self.frenzy = False
                self.effects_v['confusion'] = True
                self.effect_counter['confusion'] = random.randint(1,3)

        cant_attack = cant_move or confused or self.underground
        
        #choose from available moves. If pokemon cannot use a move, removes from list
        available_moves = list(self.moveset.keys())
        # remove struggle from available moves if it is in the list
        available_moves.remove('struggle')
        
        # Count down the move embargo
        if self.move_embargo:
            for move in list(self.move_embargo.keys()):
                self.move_embargo[move] -= 1
                if self.move_embargo[move] <= 0:
                    verboseprint(f'  {move} is no longer disabled', verbose)
                    del self.move_embargo[move]
                else:
                    if move in available_moves:
                        available_moves.remove(move)
                    verboseprint(f'  {move} is disabled', verbose)

        #If there are still moves to choose from, randomly select a move
        if len(available_moves)>=1:
            chosen_move = random.choice(available_moves)
        else: chosen_move = "struggle"
        #Effect of frenzy:
        if self.frenzy:
            chosen_move = self.frenzy_move
        #Effect of underground:
        if self.underground and not fully_paralyzed:
            chosen_move = self.dig_move
        verboseprint("%s used %s!" % (self.name,chosen_move),verbose)

        #Effect of dig:
        if self.underground and not fully_paralyzed:
            self.use_move(other,chosen_move,verbose)
            self.underground = False

        if cant_move:
            verboseprint("  %s can't move." % (self.name),verbose)
        #If pokemon can move and there is an available move they can use:
        if (not cant_attack) and (chosen_move):
            self.use_move(other,chosen_move,verbose) #use move

        #Inflict poison damage
        if self.effects_nv['poison']:
            damage = self.start_hp//16
            if damage == 0:
                damage = 1
            self.hp -= damage
            verboseprint("  %s took %d poison damage" % (self.name,damage),verbose)
            
        #Inflict burn damage
        if self.effects_nv['burn']:
            damage = self.start_hp//16
            if damage == 0:
                damage = 1
            self.hp -= damage
            verboseprint("  %s took %d burn damage" % (self.name,damage),verbose)

        #Inflict Seeding
        if self.effects_v['seed']:
            damage = self.start_hp//16
            if damage == 0:
                damage = 1
            self.hp -= damage
            newhp = other.hp + damage
            if newhp > other.start_hp:
                other.hp = other.start_hp
            else:
                other.hp = newhp
            verboseprint("  %s took %d seeding damage" % (self.name,damage),verbose)
            verboseprint("  %s gains %d hp!" % (other.name,damage),verbose)
            
        #Inflict bound damage
        if self.effects_v['bound']:
            damage = self.start_hp//16
            if damage == 0:
                damage = 1
            self.hp -= damage
            verboseprint("  %s took %d bound damage" % (self.name,damage),verbose)
            self.effect_counter['bound'] -= 1
            if self.effect_counter['bound'] == 0:
                self.effects_v['bound'] = False

    def use_move(self,other,chosen_move,verbose=False):
        '''Use a chosen move against another pokemon'''

        #use_move can be called with a move that is not in the Pokemon's individual moveset.
        #if so, recreates a move dictionary for that specific move
        if chosen_move in self.moveset:
            working_move = self.moveset[chosen_move]
        else:
            move = merged_moves_df.iloc[np.where(merged_moves_df['move'] == \
                                                 chosen_move)].iloc[0]
            working_move = {'type':move['type'],\
                            'power':move['power'],\
                            'accuracy':move['accuracy'],\
                            'pp':move['pp'],\
                            'category':move['category'],\
                            'effect':move['effect'],\
                            'effect_prob':move['effect_prob']/100,\
                            'stat_change':move['stat_change'],\
                            'amount_changed':move['amount_changed']}

        #if no other move has been used yet, assign as first move
        if not self.first_move:
            self.first_move = working_move
            
        #Accuracy:
        # if accuracy is inapplicable, move always works.
        if working_move['accuracy'] == '_':
                acc = 1
        else: #convert accuracy to a probability
            #Accuracy depends on individual accuracy, move accuracy, and other's evasion
            move_acc = float(working_move['accuracy'])
            self_acc = self.statmods_multipliers[self.statmods['accuracy']]
            other_evasion = other.statmods_multipliers[other.statmods['evasion']]
            acc = move_acc*self_acc*(1/other_evasion)/100
         

        ####
        #if the other pokemon is underground they are immune to most moves
        #(not swift or transform)
        if other.underground and (chosen_move != 'swift') and (chosen_move != 'transform'):
            acc = 0
        
        #Given the accuracy, does the move hit?
        if random.random() < acc: #bernoulli with p = acc on whether move hits or not
            verboseprint("%s's move hits!" % (self.name),verbose) #display whether move hits
            # Check if the move fails
            move_failed = False
            if "Only works on sleeping Pokémon." in working_move['effect']:
                if other.effects_nv['sleep']:
                    pass
                else:
                    move_failed = True
                    verboseprint('  move failed',verbose)
            # if user is bound and tries to flee, the move fails
            if self.effects_v['bound'] and 'teleport' == chosen_move:
                move_failed = True
                verboseprint('  move failed',verbose)
            if other.effects_v['bound'] and "Forces trainers to switch Pokémon." in working_move['effect']:
                move_failed = True
                verboseprint('  move failed',verbose)
            
            if move_failed:
                pass
            else:
                #If the move has effect, take effect
                if (working_move['effect'] is not np.nan):
                    self.take_effect(other,chosen_move,working_move,verbose)
                #if the move hits and it's special or physical, the other pokemon takes damage
                if (working_move['category'] == 'special') or \
                (working_move['category'] == 'physical'):
                    # for moves that have special effects, apply them
                    healed = False
                    recoil = False
                    
                    
                    if not self.underground and working_move['effect'] != 'Hits 2-5 times in one turn.':
                        dam = other.take_damage(self,chosen_move, working_move, verbose)
                        if other.rage:
                            other.take_status('attack',1)
                            verboseprint(f'  {other.name}\'s attack was raised by {other.statmods_multipliers[other.statmods["attack"]]}',verbose)
                    
                    # for life stealing moves:
                    if ("Drains half the damage inflicted to heal the user." in working_move['effect']):
                        self.hp += round(dam/2,2)
                        healed = True
                        if self.hp > self.start_hp:
                            self.hp = self.start_hp
                    #for recoil damage
                    if ("User receives 1/4 the damage it inflicts in recoil." in working_move['effect']):
                        recoil_dam = round(dam/4,2)
                        self.hp -= recoil_dam
                        recoil = True
                    if ("User receives 1/3 the damage inflicted in recoil." in working_move['effect']):
                        recoil_dam = round(dam/3,2)
                        self.hp -= recoil_dam
                        recoil = True
                    if chosen_move == "struggle":
                        recoil_dam = round(self.start_hp/4,2)
                        self.hp -= recoil_dam
                        recoil = True
                    if ("Inflicts 40 points of damage." in working_move['effect']):
                        dam = (40-dam)
                        other.hp -= dam
                        dam = 40  #for print statement
                    if ("Inflicts 20 points of damage." in working_move['effect']):
                        dam = (20-dam)
                        other.hp -= dam
                        dam = 20 #for print statement
                    if ("Inflicts damage equal to the user's level." in working_move['effect']):
                        dam = self.level - dam
                        other.hp -= dam
                        dam = self.level #for print statement
                        

                    #print out statements for damage and effects
                    if not self.underground:
                        if healed:
                            verboseprint(f'  {self.name} healed for {dam/2:.1f} hp',verbose)
                            healed = False
                        if recoil:
                            verboseprint(f'  {self.name} took {recoil_dam:.1f} recoil damage',verbose)
                            recoil = False
                        

                #status moves don't have damage outside of their effects
                elif working_move['category'] == 'status':
                    if chosen_move == "transform":
                        self.transform(other)

        else: # display whether move misses
            verboseprint("%s's move misses..." % (self.name),verbose) 
        #Saves the move as last_attack
        self.last_attack = chosen_move

    def take_effect(self,other,chosen_move,working_move,verbose=False):
        '''Applies move affects to the appropriate pokemon
        takes as arguments other, the move name, move dictionary, and verbose'''
        stat_changed = working_move['stat_change'] #Assigns stat change to a variable
        amount_changed = working_move['amount_changed'] #Assigns amount changed to a variable
        effect = working_move['effect'] #Assigns effect to a variable
        verboseprint(f'  {effect}',verbose) #Print the effect if verbose is true

        ## Modifies other's stats
        if stat_changed != 'N/A' and 'chance' not in effect:
            if amount_changed < 0:
                other.take_status(stat_changed,amount_changed)
                # print(f'  {other.name}\'s {stat_changed} was lowered by {other.statmods_multipliers[other.statmods[stat_changed]]}')
            elif amount_changed >= 0:
                self.take_status(stat_changed,amount_changed)   
                # print(f'  {self.name}\'s {stat_changed} was raised by {self.statmods_multipliers[self.statmods[stat_changed]]}')
        elif stat_changed != 'N/A' and 'chance' in effect:  
            if amount_changed < 0:
                if random.random() < working_move['effect_prob']:
                    other.take_status(stat_changed,amount_changed)
                    # print(f'  {other.name}\'s {stat_changed} was lowered by {other.statmods_multipliers[other.statmods[stat_changed]]}')
            elif amount_changed >= 0:
                if random.random() < working_move['effect_prob']:
                    self.take_status(stat_changed,amount_changed)   
                    # print(f'  {self.name}\'s {stat_changed} was raised by {self.statmods_multipliers[self.statmods[stat_changed]]}')                

        #Check other's statuses: (returns true if they already have a status effect)
        nv_effects = other.check_effects()

        #Changes statuses that don't have multipliers:
        if not nv_effects: #Non-volatile statuses don't get overwritten
            if effect == "Puts the target to sleep.":
                other.effects_nv['sleep'] = True
                other.effect_counter['sleep'] = random.randint(1,7)
            if (effect =='Poisons the target.') and ('poison' not in other.types.values()):
                other.effects_nv['poison']=True
            if "chance to poison the target." in effect:
                if (random.random() < working_move['effect_prob']) \
                and ('poison' not in other.types.values()):
                    other.effects_nv['poison']=True
            if (effect == 'Paralyzes the target.') \
                and ('electric' not in other.types.values()):
                if (working_move['type'] == 'electric') and ('ground' in other.types.values()):
                    other.effects_nv['paralysis']= False
                    verboseprint(f'  {other.name} is immune to paralysis',verbose)
                elif working_move['type'] == 'grass' and ('grass' in other.types.values()):
                    other.effects_nv['paralysis']= False
                    verboseprint(f'  {other.name} is immune to move',verbose)
                else:
                    other.effects_nv['paralysis']= True                 
            if "chance to paralyze the target." in effect \
                and ('electric' not in other.types.values()):
                if (working_move['type'] == 'electric') and ('ground' in other.types.values()):
                    other.effects_nv['paralysis']= False
                    verboseprint(f'  {other.name} is immune to paralysis',verbose)
                elif working_move['type'] == 'grass' and ('grass' in other.types.values()):
                    other.effects_nv['paralysis']= False
                    verboseprint(f'  {other.name} is immune to move',verbose)
                else:
                    if random.random() < working_move['effect_prob']:
                        other.effects_nv['paralysis']= True
            if "chance to freeze the target." in effect:
                if 'ice' not in other.types.values():
                    if random.random() < working_move['effect_prob']:
                        other.effects_nv['freeze'] = True
        #Burn counteracts freezing and is the exception to a non-volatile statuses staying
        if (not nv_effects) or (other.effects_nv['freeze']):
            if 'chance to burn the target.' in effect:
                other.effects_nv['freeze'] = False
                if (random.random() < working_move['effect_prob']) \
                and ('fire' not in other.types.values()):
                    other.effects_nv['burn'] = True

        #Volatile Status effects:
        if effect == 'Confuses the target.':
            other.effects_v['confusion'] = True
            other.effect_counter['confusion'] = random.randint(1,3)
        if "chance to confuse the target." in effect:
            if random.random() < working_move['effect_prob']:
                other.effects_v['confusion'] = True
                other.effect_counter['confusion'] = random.randint(1,3)
        if 'make the target flinch' in effect:
            if random.random() < working_move['effect_prob']:
                other.effects_v['flinch'] = True
                other.effect_counter['flinch'] = 1
        if ('Seeds the target, stealing HP from it every turn.' in effect) \
            and ('grass' not in other.types.values()):
            other.effects_v['seed']= True
        if effect == "Prevents the target from fleeing and inflicts damage for 2-5 turns.":
            other.effects_v['bound'] = True
            other.effect_counter['bound'] = random.randint(2,5)

        #Special effects
        if effect == "If the user is hit after using this move, its Attack rises by one stage.":
            self.rage = True
        if effect == 'increases critical hit ratio.':
            self.focus_energy = True
        if effect == 'Hits 2-5 times in one turn.':
            ntimes = random.randint(2,5)
            for i in range(ntimes):
                other.take_damage(self,chosen_move, working_move, verbose)
            if other.rage:
                other.take_status('attack',1)
                verboseprint(f'  {other.name}\'s attack was raised by {other.statmods_multipliers[other.statmods["attack"]]}',verbose)
            verboseprint(f'  {self.name} hits {other.name} {ntimes} times',verbose)
        if effect == 'Hits twice in one turn.':
            other.take_damage(self,chosen_move, working_move, verbose)
        if effect == 'Hits every turn for 2-3 turns, then confuses the user.' and not self.frenzy:
            self.frenzy = True
            self.effect_counter['frenzy'] = random.randint(2,3)
            self.frenzy_move = chosen_move
        if (not self.underground) and (effect == 'User digs underground, dodging all attacks, and hits next turn.'):
            verboseprint('  user digs underground',verbose)
            self.underground = True
            self.dig_move = chosen_move
        elif self.underground and (effect == 'User digs underground, dodging all attacks, and hits next turn.'):
            verboseprint('  user strikes from below',verbose)
            self.underground = False
        if effect == "User's type changes to the type of one of its moves at random.": 
            available_types = []
            for move in self.moveset:
                type_ = self.moveset[move]['type']
                available_types.append(type_)
            chosen_type = random.choice(available_types)
            self.types[1] = chosen_type
            verboseprint(f'  {self.name} changed type to {chosen_type}',verbose)
        if effect == 'Randomly selects and uses any move in the game.':
            available_moves = list(merged_moves_df.move.unique())
            chosen_move = random.choice(available_moves)
            verboseprint(f'  {self.name} used {chosen_move}',verbose)
            self.use_move(other,chosen_move,verbose)
        if (effect == 'Immediately ends wild battles.  Forces trainers to switch Pokémon.')\
         or (effect =='Immediately ends wild battles.  No effect otherwise.'):
            self.in_battle = False
            verboseprint('  teleported away',verbose)
        if effect == "Disables the target's last used move for 1-8 turns.":
            if other.last_attack != False and other.last_attack != 'struggle':
                other.move_embargo[other.last_attack] = random.randint(1,8)+1
                verboseprint(f'  {other.last_attack} was disabled for {other.move_embargo[other.last_attack]-1} turns',verbose)
        if effect == 'User sleeps for two turns, completely healing itself.':
            self.effects_nv['sleep'] = True
            self.effect_counter['sleep'] = 2
            self.rest = True
            self.hp = self.start_hp
            self.effects_nv['poison']=False
            self.effects_nv['paralysis']=False
            self.effects_nv['burn'] = False
            self.effects_nv['freeze'] = False


        # Added verbose statements for effect changes
        # filter by effects that are true using a filter function
        if True in self.effects_nv.values():
            active_nv_effects = list(filter(lambda key: self.effects_nv[key],\
                                            self.effects_nv.keys()))
            verboseprint(f'  {self.name} has status: {active_nv_effects}',verbose)
        if True in self.effects_v.values():
            active_v_effects = list(filter(lambda key: self.effects_v[key],\
                                           self.effects_v.keys()))
            verboseprint(f'  {self.name} has status: {active_v_effects}',verbose)

        if True in other.effects_nv.values():
            active_nv_effects = list(filter(lambda key: other.effects_nv[key],\
                                            other.effects_nv.keys()))
            verboseprint(f'  {other.name} has status: {active_nv_effects}',verbose)
        if True in other.effects_v.values():
            active_v_effects = list(filter(lambda key: other.effects_v[key],\
                                           other.effects_v.keys()))
            verboseprint(f'  {other.name} has status: {active_v_effects}',verbose)


    def take_status(self,status_name,modification):
        '''Adjusts the stage of a stat to change its multipliers.'''
        new_status = self.statmods[status_name] + modification
        #Stage must be between -6 and 6
        if new_status < -6:
            self.statmods[status_name] = -6
        elif new_status > 6:
            self.statmods[status_name] = 6
        else:
            self.statmods[status_name] = new_status

    def check_effects(self):
        '''returns True if there is a nonvolatile status in place'''
        nv_effects = False
        for status in self.effects_nv:
            nv_effects = nv_effects or self.effects_nv[status]
        return nv_effects

    def transform(self,other):
        '''Status move where pokemon takes traits of the other pokemon'''
        self.speed = other.speed
        self.types = other.types
        self.moveset = other.moveset
        self.damage_multiplier = other.damage_multiplier
        self.attack = other.attack
        self.defense = other.defense
        self.sp_attack = other.sp_attack
        self.sp_defense = other.sp_defense

    def healthpercent(self):
        return round(float(self.hp/self.start_hp),3)

    def reset(self):
        '''Resets all conditions to starting conditions'''
        #Base stats, type, and modifiers:
        self.hp = self.start_hp
        self.speed = self.start_speed
        self.defense = self.start_defense
        self.attack = self.start_attack
        self.sp_attack = self.start_sp_attack
        self.sp_defense = self.start_sp_defense
        self.types = self.start_types
        self.damage_multiplier = self.start_damage_multiplier
        self.statmods = {'speed':0,'attack':0,'defense':0,'sp_attack':0,\
                         'sp_defense':0,'accuracy':0,'evasion':0}
        self.moveset = self.start_moveset
        #nonvolatile status effects:
        self.effects_nv = {'sleep':False,'paralysis':False,'poison':False,\
                           'freeze':False,'burn':False}
        #volatile status effects:
        self.effects_v = {'confusion':False,'flinch':False,'seed':False,'bound':False}
        #Statuses to keep track of states
        self.effect_counter = {'sleep':0,'confusion':0,'poison':0,\
                               'flinch':0,'frenzy':0}
        self.first_move = False
        self.last_attack = False
        self.move_embargo = {}
        self.in_battle = True
        self.focus_energy = False
        self.frenzy = False
        self.frenzy_move = False
        self.underground = False
        self.dig_move = False
        self.rage = False
        self.rest = False

#-------------------------------------------------------------------------------------
## Run Battle
def runbattle(pokemon_a,pokemon_b,verbose=False,healing=False,remaininghealth = 1,freshstart=True):
    '''pokemon_a and pokemon_b: Pokemon class
    verbose: boolean, print or don't print moves 
    healing: boolean for whether to heal in battle
    remaininghealth: percent of health pokemon b has left (between 0 and 1)
    freshstart: boolean for whether to reset at the beginning of a match '''
    #check if pokemon a is the same as pokemon b
    if pokemon_a.name == pokemon_b.name:
        #create a copy of pokemon b with a different name
        pokemon_b = copy.deepcopy(pokemon_a)
        pokemon_b.name = pokemon_b.name + '2'

    #reset the stats of both pokemon
    if freshstart:
        pokemon_a.reset()
        pokemon_b.reset()

    #if healing is True, set a number of heals per battle
    if healing:
        Nheals1 = 1
        Nheals2 = 1
    else:
        Nheals1 = 0
        Nheals2 = 0
    healingthreshold = 0.15 #heals at 15 percent of original health

    pokemon_b.hp = pokemon_b.start_hp*(remaininghealth)
    verboseprint("->%s has %.1f hp.\n->%s has %.1f hp." % (pokemon_a.name,pokemon_a.hp,pokemon_b.name,pokemon_b.hp),verbose)

    #fastest pokemon is "pokemon1", who goes first
    if pokemon_a.start_speed > pokemon_b.start_speed:
        pokemon1=pokemon_a
        pokemon2=pokemon_b
    elif pokemon_b.start_speed > pokemon_a.start_speed:
        pokemon1=pokemon_b
        pokemon2=pokemon_a
    else: #for pokemon with the same speed, randomly select who goes first
        if random.random() < 0.5:
            pokemon1 = pokemon_a
            pokemon2 = pokemon_b
        else:
            pokemon1 = pokemon_b
            pokemon2 = pokemon_a

    verboseprint("%s goes first!" % pokemon1.name,verbose)
    nturns = 0

    while pokemon1.hp >0 and pokemon2.hp>0:
        
        #Pokemon 1: heals or takes a turn
        if (Nheals1 > 0) and (pokemon1.hp < healingthreshold * pokemon1.start_hp):
            Nheals1 -= 1
            pokemon1.reset()
            verboseprint("%s used a full restore!" % pokemon1.name,verbose)
        else:
            pokemon1.choose_move(pokemon2,verbose)
        verboseprint("-- %s has %.1f hp remaining." % (pokemon2.name,pokemon2.hp),verbose)
        nturns += 1
        
        #Check for a winner 
        winner = check_winner(pokemon1,pokemon2)
        if winner: 
            if winner != 'draw':
                verboseprint('\n%s wins after %d turns! %d percent of health remaining\n' % (winner.name,nturns,winner.healthpercent()*100),verbose)
                return winner.name, nturns, pokemon_a.healthpercent(),pokemon_b.healthpercent()
            else:
                return winner,nturns,pokemon_a.healthpercent(),pokemon_b.healthpercent()
        if pokemon1.in_battle == False:
            verboseprint('\n%s left the battle, draw after %d turns' % (pokemon1.name, nturns), verbose)
            return 'draw', nturns, pokemon_a.healthpercent(),pokemon_b.healthpercent()
        #Pokemon 2: heals or takes a turn
        if (Nheals2 > 0) and (pokemon2.hp < healingthreshold * pokemon2.start_hp):
            Nheals2 -= 1
            pokemon2.reset()
            verboseprint("%s used a full restore!" % pokemon2.name,verbose)
        else:
            pokemon2.choose_move(pokemon1,verbose)
        verboseprint("-- %s has %.1f hp remaining." % (pokemon1.name,pokemon1.hp),verbose)
        nturns +=1

        #Check for a winner
        winner = check_winner(pokemon1,pokemon2)
        if winner:
            #healthperc = winner.hp/winner.start_hp
            if winner != 'draw':
                verboseprint('\n%s wins after %d turns! %d percent of health remaining\n' % (winner.name,nturns,winner.healthpercent()*100),verbose)
                return winner.name, nturns, pokemon_a.healthpercent(),pokemon_b.healthpercent()
            else:
                return 'draw',nturns,pokemon_a.healthpercent(),pokemon_b.healthpercent()
        # Check if pokemon 2 has left the battle    
        if pokemon2.in_battle == False:
            verboseprint('\n%s left the battle, draw after %d turns' % (pokemon2.name, nturns), verbose)
            return 'draw', nturns, pokemon_a.healthpercent(),pokemon_b.healthpercent()
        # Check if the battle has gone on for too long
        if nturns >100:
            verboseprint('\ndraw after %d turns' % nturns, verbose)
            return 'draw', nturns, pokemon_a.healthpercent(),pokemon_b.healthpercent()

#----------------------------------------------------------------------------------------

def check_winner(pokemona,pokemonb):
    '''Returns winner's name if either pokemon's hp has decreased below zero'''
    if pokemona.hp <=0 and pokemonb.hp<=0:
        pokemona.hp = 0
        pokemonb.hp = 0
        return 'draw'
    elif pokemona.hp <=0:
        pokemona.hp = 0
        return pokemonb
    elif pokemonb.hp <=0:
        pokemonb.hp = 0
        return pokemona
    else:
        return False
    
#----------------------------------------------------------------------------------------

def create_pokemon_dict(pk_df = Pokemon_df_level1, generation = 1, pk_level = 1):
    '''Create a dictionary of pokemon objects'''
    # Assign all pokemon as a class
    temp_df = levelup(pk_df, pk_level)
    gen1 = np.where(temp_df['generation'] == generation) #isolates gen 1 pokemon
    pokemon_dict = {} #Dictionary in {Pokemon name:Pokemon class format}
    
    for pokemon_name in temp_df.iloc[gen1].index: #for every pokemon in gen 1
        #assign a class as a member of the dictionary
        pokemon_dict[pokemon_name] = Pokemon(pokemon_name, temp_df)
        
    return pokemon_dict

def create_pokemon_objects(pokemon_list, generation = 1,  pk_level = 1):
    pokemon_dict = create_pokemon_dict(Pokemon_df_level1, generation, pk_level)
    return [pokemon_dict[pk] for pk in pokemon_list]

#----------------------------------------------------------------------------------------

def battle_team(team_1, team_2, verbose=False,roundreset = True):
    '''Runs a battle between two teams of pokemon. Returns the winner 
    winner list, and the number of rounds it took to win.'''
    team_1_names = [pokemon.name for pokemon in team_1]
    team_2_names = [pokemon.name for pokemon in team_2]
    # reset all pokemon
    if roundreset:
        for pokemon in team_1:
            pokemon.reset()
        for pokemon in team_2:
            pokemon.reset()
    rounds = 0
    winner_list = []
    n = 0
    percent_health_a = 1
    
    for opponent in team_2:
        percent_health_b = 1
        for i in range(n,len(team_1)):
            if percent_health_b > 0:
                if percent_health_a == 1:
                    winner, round_count, percent_health_a, percent_health_b = runbattle(team_1[i], opponent, verbose = verbose, healing=False, remaininghealth = percent_health_b)
                    winner_list.append(winner)
                    rounds += round_count
                else:
                    winner, round_count, percent_health_b, percent_health_a = runbattle(opponent, team_1[i], verbose = verbose, healing=False, remaininghealth = percent_health_a)
                    winner_list.append(winner)
                    rounds += round_count
                if percent_health_a <= 0:
                    n += 1
                    percent_health_a = 1
            else:
                break
    if winner_list[-1] in team_1_names:
        winner = '1st team'    
    else:
        winner = '2nd team'
    return winner, winner_list, rounds

def run_elite(our_team,verbose = False,roundreset = True):
    ''' Function to run the elite four battles. Input is a list of 6 pokemon and 
        the elite4 - these have to be pokemon objects.
        Returns a tuple of success,round_time,teamname,winner_list:
            Success is 1 if the team wins, 0 if the team loses.
            round_time is the number of rounds it took to win divided by 10. 
            Teamname is the name of the elite four member that the team lost to.
            Winner_list is a list of the winners from the final battle.
    '''
    success = 0
    winner = 'NA'
    round_time = 0
    teamname = 'NA'

    elite4_1 = ['dewgong','cloyster','slowbro','jynx','lapras']
    elite4_2 = ['onix','hitmonlee','hitmonchan','onix','machamp']
    elite4_3 = ['gengar','golbat','haunter','arbok','gengar']
    elite4_4 = ['gyarados','dragonair','dragonair','aerodactyl','dragonite']
    elite_list = [elite4_1,elite4_2,elite4_3,elite4_4]

    elite4 = []
    for team in elite_list:
        elite4.append(create_pokemon_objects(team, generation = 1, pk_level = 50))
    
    for team in elite4:
        if team ==  elite4[0]:
            winner,winner_list,rounds = battle_team(our_team,team,verbose,True)
        else:
            winner,winner_list,rounds = battle_team(our_team,team,verbose,roundreset)
        round_time += rounds
        if winner == "2nd team":
            if team == elite4[0]:
                teamname = 'Lorelei'
            elif team == elite4[1]:
                teamname = 'Bruno'
            elif team == elite4[2]:
                teamname = 'Agatha'
            elif team == elite4[3]:
                teamname = 'Lance'
            else:
                teamname = 'Error: Team not found'
            round_time = round_time/10
            return success,round_time,teamname,winner_list
    round_time = round_time/10
    teamname = 'Champion'
    success = 1
    return success,round_time,teamname,winner_list

if __name__ == '__main__':
    #----------------------------------------------------------------------------------------
    # Test Battle
    #----------------------------------------------------------------------------------------
    # Create a dictionary of pokemon objects
    pokemon_dict = create_pokemon_dict()

    # # Enter Pokemon one
    # pokemon1 = 'charizard'
    # # Enter Pokemon two
    # pokemon2 = 'blastoise'
    # # Run the battle
    # runbattle(pokemon_dict[pokemon1],pokemon_dict[pokemon2],verbose=True)

    team1 = ['bulbasaur','charmander','squirtle','pikachu','jigglypuff','meowth']
    team1 = create_pokemon_objects(team1)
    result,time,teamname,winnerlist = run_elite(team1,verbose=False)
    print(result)
    print("%.2f minutes" % time)
    print(teamname)
    print(winnerlist)
    print('---------------------------------')
    