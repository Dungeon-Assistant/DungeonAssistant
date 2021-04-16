# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 18:50:03 2021

@author: jfc97
"""
from . import encounterCall as ec

def encounter_division(num_layers, target_difficulty, num_rooms):
    #encounter distributions, max of 10 levels, "deeper" levels should have higher CR
    nums = [6,5,4,4]
    diffs = ec.difficulty_strings
    difficulty_scalar = 1.2 #hyperparameter that helps control difficulty spreads, higher "softens encounters"
    
    #requested difficulty
    try:
        enc_index = diffs.index(target_difficulty)
    except:
        enc_index = 0
    
    #return lists
    encounter_nums = []
    encounter_diffs = []
    for i in range(num_layers):
        encounter_nums.append(nums[int(i*len(nums)/num_layers)])
        diff_ind = int((enc_index + difficulty_scalar*len(diffs)*(i-num_layers/2)/(num_layers)))
        if(diff_ind >= len(diffs)):
            encounter_nums[i] -= diff_ind - len(diffs) - 1
            diff_ind = len(diffs)-1
        elif(diff_ind < 0):
            encounter_nums[i] += diff_ind - 1
            diff_ind = 0
        encounter_diffs.append(diffs[diff_ind])
        
        #update based on room availability
        if(encounter_nums[i] > num_rooms[i]):
            encounter_nums[i] = num_rooms[i]
            #requested difficulty + 1
            try:
                enc_index = diffs.index(target_difficulty) + 1
            except:
                enc_index = 0
            
            #if no higher difficulty, do nothing
            if(enc_index >= len(diffs)):
                enc_index = len(diffs) - 1;
            
            encounter_diffs[i] = diffs[enc_index]
    
    return encounter_nums, encounter_diffs
    

def generateEncounter(target_diff, num_encounters, num_players, avg_level):    
    encounters = ec.call_encounter(target_diff, num_encounters, num_players, avg_level)    
    return encounters
    

if __name__ == '__main__':
    x,y = encounter_division(4, "Medium", [8,8,8,8])
    