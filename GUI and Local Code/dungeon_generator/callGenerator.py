# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 19:16:36 2021

@author: jfc97
"""

from . import generateDungeonMap as gm
from . import encounterLogic as el

class Dungeon:
    def __init__(self, dungeon_parameters):
        # Construction Parameters
        dungeon_class = dungeon_parameters.get('dungeon_class', 'Small')
        room_class = dungeon_parameters.get('room_class', 'Varied')
        density_class = dungeon_parameters.get('density_class', 'Dense')
        layers = dungeon_parameters.get('layers', 1)
        numPlayers = dungeon_parameters.get('players', 4)
        avgLevel = dungeon_parameters.get('avgLevel', 10)
        difficulty = dungeon_parameters.get('difficulty', 'Medium')
        
        
        # Return Objects
        self.dungeon_objects = makeDungeon(dungeon_class, room_class, density_class, layers)
        self.dungeon_maps = [gm.to_image(layer) for layer in self.dungeon_objects]
        self.dungeon_encounters = makeEncounters(self.dungeon_objects, numPlayers, avgLevel, difficulty)

def makeDungeon(dungeon_class, room_class, density_class, layers):
    return gm.create_dungeon(dungeon_class, room_class, density_class, layers)

def makeEncounters(dungeon, numPlayers, avgLevel, difficulty):
    #determine difficulty per layer (needs # of layers and target difficulty)
    room_nums = [len(x.rooms) for x in dungeon]
    layer_enc_num, layer_diff = el.encounter_division(len(dungeon), difficulty, room_nums)
    #generate encounters layer by layer (layer difficulty, and target number of encounters)
    encounters_list = [el.generateEncounter(layer_diff[i], layer_enc_num[i], numPlayers, avgLevel) for i in range(len(layer_enc_num))]
        
    #assign encounter to room (get room numbers in order of smallest to largest room)
    #assumes rooms are numbered in grid order
    encounters_by_room = []
    for i,layer in enumerate(dungeon):
        size_rooms = gm.room_sort(layer, "size")
        grid_rooms = gm.room_sort(layer, "grid")
        layer_encounters = []
        
        #match largest rooms with encounters
        for j,encounter in enumerate(encounters_list[i]):
            room_index = grid_rooms.index(size_rooms[j])
            layer_encounters.append([room_index, encounter])
        
        encounters_by_room.append(layer_encounters)
    
    #return strings with room numbers (ordered by room number)
    return encounters_by_room

if __name__ == '__main__':
    dungeon_options = {'dungeon_class' : 'Medium', 
                       'room_class' : 'Medium', 
                       'density_class' : 'Dense', 
                       'layers' : 3,
                       'players' : 4,
                       'avgLevel' : 10,
                       'difficulty' : 'Medium'}
    
    dng = Dungeon(dungeon_options)
    for image in dng.dungeon_maps:
        image.show()