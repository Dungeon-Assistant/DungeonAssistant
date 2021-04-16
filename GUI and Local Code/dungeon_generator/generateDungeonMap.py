from .dungeonGenerator import dungeonGenerator

from PIL import Image, ImageFont, ImageDraw
import numpy as np
import random, logging



def to_image(dm):
    grid = dm.grid
    width = dm.width
    height = dm.height
    
    scale = 6
    
    array = np.zeros((width*scale, height*scale, 3) , dtype=np.uint8)
    colorMap = {
        0: [0,0,0], #empty
        1: [255,255,255], #floor 
        2: [100,100,100], #corridor
        3: [200,0,0], #door
        4: [0,200,0], #deadend
        5: [255,255,150], #wall
        6: [0,0,255], #obstacle
        7: [255,100,100], #cave
        8: [0,0,255], #up_stairs
        9: [0,255,0] #down_stairs
        }
        
    for x in range(width):
        for y in range(height):
            #PIL Resize doesn't directly scale without interpolation
            for i in range(scale):
                for j in range(scale):
                        array[x*scale+i][y*scale+j] = colorMap.get(grid[x][y])
    # generate base map
    im = Image.fromarray(array)
    
    # load in font
    font = ImageFont.load_default() 
    
    #room numbering
    for i, room in enumerate(dm.rooms):
        r_height, r_width = room.height*scale, room.width*scale
        r_y, r_x = room.x*scale, room.y*scale
        
        r_y += (r_width/2)-4; #offset 1/2 text size
        r_x += (r_height/2)-4;
        
        # document  
        dctx = ImageDraw.Draw(im) 
        dctx.text((r_x, r_y), str(i), font = font, fill=(0,0,0)) 
        
    #replace stair textures
    for i in dm.stairs:
        if(i[0] == 'up'):
            stair_img = Image.open('dungeon_generator/stair_up.jpg','r').resize((3*scale,5*scale))
        else:
            stair_img = Image.open('dungeon_generator/stair_down.jpg','r').resize((3*scale,5*scale))
        #x,y
        s_x,s_y = i[1]
        s_x *= scale
        s_y *= scale
        im.paste(stair_img,(s_y,s_x))
        
    im.save('dungeonmap.png')
    
    return im


def create_stairs(layers):
    stairs = []
    
    #no layers = no stairs
    if(layers == 1):
        stairs = [[]]
        return stairs
    
    #determine up and down stairs
    for i in range(layers):
        if(i == 0):
            stairs.append(['down'])
        elif(i == layers-1):
            stairs.append(['up'])
        else:
            stairs.append(['up','down'])
            
    return stairs

def place_stairs(rooms, stairs):
    stair_loc = []
    for i in stairs:
        target_room = random.choice(rooms)
        target_x, target_y = target_room.x, target_room.y
        stair_loc.append([i,[target_x,target_y]])

    return stair_loc

def room_sort(dm, sort_order):
    def size_sort(x):
        return x.width * x.height;
    
    def grid_sort(x):
        return x.y + x.x * (1*x.x/dm.height); #digits creates effect of rows
    
    if(sort_order == "size"):
        return sorted(dm.rooms, key=size_sort, reverse=True)
    else:
        return sorted(dm.rooms, key=grid_sort, reverse=False)

def create_dungeon(dungeon_class, room_class, density_class, layers):
    logging.info("Creating dungeon [dungeon_class={}, room_class={}, density_class={}, layers={}]".format(dungeon_class, room_class, density_class, layers))
    stairs = create_stairs(layers)
    
    #determine encounter distribution    
    #generate dungeon layer-by-layer
    #pre-generating the stairs allows this to be deferred to later
    dungeon_layers = []
    for i in range(layers):
        dungeon_layers.append(generate_layer(dungeon_class, room_class, density_class, stairs[i]))
    return dungeon_layers

def generate_layer(dungeon_class, room_class, density_class, stairs):
    dung_size_dict = {"Small" : [50, 50], "Medium" : [100, 100], "Large" : [200, 200], "Dangerous" : [400, 400]}
    dungeon_size = dung_size_dict.setdefault(dungeon_class, [100, 100])
    
    room_size_dict = {"Small" : [5, 8], "Medium" : [8, 14], "Large" : [15, 22], "Ballroom" : [30, 50], "Varied" : [6, 20]}
    room_size = room_size_dict.setdefault(room_class, [8, 14])
    
    room_density_dict = {"Sparse" : 2, "Moderate" : 20, "Dense" : 80, "Full" : 1000}
    room_density = room_density_dict.setdefault(density_class, 1000)
    
    dm = dungeonGenerator(dungeon_size[0], dungeon_size[1])
 
    dm.placeRoom(0, 0, 10, 10, True)
    dm.placeRandomRooms(room_size[0], room_size[1], 1, 4, room_density) #num_rooms = 100 will fill the entire map space with rooms
    
    #connect rooms    
    dm.rooms = room_sort(dm,"grid")
    dm.generateCorridors('r') #'r','f','l','m'
    dm.connectAllRooms(50)
    
    #join unconnected areas
    unconnected = dm.findUnconnectedAreas()
    dm.joinUnconnectedAreas(unconnected)
    dm.pruneDeadends(100)
    
    #add stairs
    dm.stairs = place_stairs(dm.rooms, stairs)
 
    return dm
    
    
if __name__ == '__main__':
    do = {}
    do['dungeon_class'] = 'Small'
    do['room_class'] = 'Medium'
    do['density_class'] = 'Dense'
    do['layers'] = 1

    layer_list = create_dungeon(do['dungeon_class'], do['room_class'], do['density_class'], do['layers'])
    for layer in layer_list:
        to_image(layer).show()